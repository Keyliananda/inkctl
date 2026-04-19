"""Befehle zum Verwalten von SVG-Elementen per ID."""

import json
import os
import shutil
import sys
from argparse import Namespace
from importlib import resources
from pathlib import Path

from inkscape_cli.runner import InkscapeRunner
from inkscape_cli.svg_builder import SVGBuilder

SELECTION_EXPORT_PATH = Path("/tmp/inkscape_selection.json")
SELECTION_EXTENSION_FILES = ("export_selection.py", "export_selection.inx")
SELECTION_EXTENSION_MENU_PATH = "Extensions > inkctl > Send Selection to AI"
SIMILARITY_LOWER_RATIO = 0.45
SIMILARITY_UPPER_RATIO = 2.5


def _normalize_file_path(path: str) -> str:
    """Normalisiert einen Dateipfad für Vergleiche."""
    return str(Path(path).expanduser().resolve())


def _get_inkscape_extensions_dir() -> Path:
    """Ermittelt den Inkscape-Extensions-Ordner für das aktuelle System."""
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions"
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "inkscape/extensions"
        return home / "AppData/Roaming/inkscape/extensions"
    return home / ".config/inkscape/extensions"


def _copy_selection_extension(destination: Path) -> list[Path]:
    """Kopiert die inkctl-Selection-Extension in den Zielordner."""
    destination.mkdir(parents=True, exist_ok=True)
    copied_files = []

    for filename in SELECTION_EXTENSION_FILES:
        resource = resources.files("inkscape_cli").joinpath("extensions", filename)
        with resources.as_file(resource) as source_path:
            target_path = destination / filename
            shutil.copy2(source_path, target_path)
            copied_files.append(target_path)

    return copied_files


def _load_selection_data(requested_file: str | None = None) -> tuple[dict | None, dict | None]:
    """Lädt die zuletzt exportierte Inkscape-Selektion."""
    if not SELECTION_EXPORT_PATH.exists():
        return None, {
            "error": (
                "Keine Selektion gefunden. Bitte zuerst in Inkscape: "
                f"{SELECTION_EXTENSION_MENU_PATH} ausführen."
            )
        }

    with SELECTION_EXPORT_PATH.open(encoding="utf-8") as selection_file:
        data = json.load(selection_file)

    exported_file = data.get("file")
    if requested_file and exported_file:
        normalized_requested = _normalize_file_path(requested_file)
        if _normalize_file_path(exported_file) != normalized_requested:
            return None, {
                "error": "Die exportierte Selektion gehört zu einer anderen Datei.",
                "requested_file": normalized_requested,
                "selection_file": exported_file,
            }

    return data, None


def _parse_ids(ids_value: str | None) -> list[str]:
    """Parst eine kommaseparierte ID-Liste."""
    if not ids_value:
        return []
    return [element_id.strip() for element_id in ids_value.split(",") if element_id.strip()]


def _local_tag_name(element) -> str:
    """Liefert den lokalen Tag-Namen ohne Namespace."""
    return element.tag.rsplit("}", 1)[-1]


def _element_signature(element) -> tuple[str, tuple[tuple[str, str], ...]]:
    """Erzeugt eine stabile Vergleichssignatur für ähnliche SVG-Elemente."""
    ignored_attributes = {"id", "d"}
    comparable_attributes = tuple(
        sorted(
            (key, value)
            for key, value in element.attrib.items()
            if key not in ignored_attributes
        )
    )
    return _local_tag_name(element), comparable_attributes


def _bbox_area(box: dict[str, float]) -> float:
    """Berechnet die Fläche einer Bounding-Box."""
    return box["width"] * box["height"]


def _is_within_reference_ratio(value: float, reference_values: list[float]) -> bool:
    """Prüft, ob ein Wert in einem tolerierten Verhältnis zu Referenzwerten liegt."""
    if value <= 0 or not reference_values:
        return False
    lower_bound = min(reference_values) * SIMILARITY_LOWER_RATIO
    upper_bound = max(reference_values) * SIMILARITY_UPPER_RATIO
    return lower_bound <= value <= upper_bound


def _is_similar_bbox(box: dict[str, float], reference_boxes: list[dict[str, float]]) -> bool:
    """Vergleicht die Bounding-Box eines Kandidaten mit den Referenzen."""
    widths = [reference_box["width"] for reference_box in reference_boxes]
    heights = [reference_box["height"] for reference_box in reference_boxes]
    areas = [_bbox_area(reference_box) for reference_box in reference_boxes]
    return (
        _is_within_reference_ratio(box["width"], widths)
        and _is_within_reference_ratio(box["height"], heights)
        and _is_within_reference_ratio(_bbox_area(box), areas)
    )


def _similarity_score(box: dict[str, float], reference_boxes: list[dict[str, float]]) -> float:
    """Berechnet einen einfachen Distanz-Score für Sortierung der Treffer."""
    avg_width = sum(reference_box["width"] for reference_box in reference_boxes) / len(reference_boxes)
    avg_height = sum(reference_box["height"] for reference_box in reference_boxes) / len(reference_boxes)
    avg_area = sum(_bbox_area(reference_box) for reference_box in reference_boxes) / len(reference_boxes)
    return (
        abs(box["width"] - avg_width) / max(avg_width, 1e-9)
        + abs(box["height"] - avg_height) / max(avg_height, 1e-9)
        + abs(_bbox_area(box) - avg_area) / max(avg_area, 1e-9)
    )


def cmd_remove_elements(args) -> str:
    """Entfernt Elemente aus einer SVG-Datei anhand einer ID-Liste."""
    svg = SVGBuilder(args.file)
    ids = [element_id.strip() for element_id in args.ids.split(",") if element_id.strip()]

    backup_path = None
    if args.backup:
        backup_path = f"{args.file}.bak"
        shutil.copy2(args.file, backup_path)

    removed = []
    not_found = []

    for element_id in ids:
        element = svg.find_by_id(element_id)
        if element is None:
            not_found.append(element_id)
            continue

        if not args.dry_run:
            svg.remove_element(element)
        removed.append(element_id)

    if not args.dry_run:
        svg.save(args.file)

    return json.dumps(
        {
            "removed": removed,
            "not_found": not_found,
            "total_removed": len(removed),
            "dry_run": args.dry_run,
            "backup": backup_path,
        },
        indent=2,
    )


def cmd_select_elements(args) -> str:
    """Öffnet Inkscape mit vorausgewählten Elementen."""
    runner = InkscapeRunner()
    ids = [element_id.strip() for element_id in args.ids.split(",") if element_id.strip()]

    action_parts = [f"select-by-id:{element_id}" for element_id in ids]
    actions = "; ".join(action_parts)

    result = runner.run_actions(actions, input_file=args.file, batch=False)

    if result.returncode == 0:
        return f"{len(ids)} Elemente in Inkscape ausgewählt."
    return f"Fehler: {result.stderr}"


def cmd_find_similar_elements(args) -> str:
    """Findet ähnliche SVG-Elemente auf Basis einer Referenzselektion."""
    reference_ids = _parse_ids(getattr(args, "ids", None))
    if not reference_ids:
        selection_data, error = _load_selection_data(args.file)
        if error is not None:
            return json.dumps(error, indent=2, ensure_ascii=False)
        reference_ids = list(selection_data.get("selected_ids", []))

    if not reference_ids:
        return json.dumps(
            {"error": "Keine Referenz-IDs vorhanden."},
            indent=2,
            ensure_ascii=False,
        )

    svg = SVGBuilder(args.file)
    try:
        geometry = InkscapeRunner().query_all(args.file)
    except RuntimeError as error:
        return json.dumps({"error": str(error)}, indent=2, ensure_ascii=False)

    reference_boxes_by_signature: dict[tuple[str, tuple[tuple[str, str], ...]], list[dict[str, float]]] = {}
    found_reference_ids: list[str] = []
    missing_reference_ids: list[str] = []

    for element_id in reference_ids:
        element = svg.find_by_id(element_id)
        box = geometry.get(element_id)
        if element is None or box is None:
            missing_reference_ids.append(element_id)
            continue
        found_reference_ids.append(element_id)
        signature = _element_signature(element)
        reference_boxes_by_signature.setdefault(signature, []).append(box)

    if not found_reference_ids:
        return json.dumps(
            {
                "error": "Keine gültigen Referenzelemente gefunden.",
                "missing_reference_ids": missing_reference_ids,
            },
            indent=2,
            ensure_ascii=False,
        )

    matches = []
    for element in svg.root.xpath("//*[@id]"):
        element_id = element.get("id")
        if not element_id or element_id in found_reference_ids:
            continue

        signature = _element_signature(element)
        reference_boxes = reference_boxes_by_signature.get(signature)
        if not reference_boxes:
            continue

        box = geometry.get(element_id)
        if box is None or not _is_similar_bbox(box, reference_boxes):
            continue

        matches.append(
            {
                "id": element_id,
                "score": round(_similarity_score(box, reference_boxes), 4),
                "width": round(box["width"], 2),
                "height": round(box["height"], 2),
            }
        )

    matches.sort(key=lambda match: (match["score"], match["id"]))
    matched_ids = [match["id"] for match in matches]

    result = {
        "reference_ids": found_reference_ids,
        "matched_ids": matched_ids,
        "count": len(matched_ids),
        "missing_reference_ids": missing_reference_ids,
        "matches": matches,
    }

    if getattr(args, "select", False) and matched_ids:
        result["selection_result"] = cmd_select_elements(
            Namespace(file=args.file, ids=",".join(matched_ids))
        )

    return json.dumps(result, indent=2, ensure_ascii=False)


def cmd_get_selection(args) -> str:
    """Liest die zuletzt exportierte Inkscape-Selektion aus."""
    data, error = _load_selection_data(args.file)
    if error is not None:
        return json.dumps(error, indent=2, ensure_ascii=False)
    return json.dumps(data, indent=2, ensure_ascii=False)


def cmd_install_extension(args) -> str:
    """Installiert die inkctl-Inkscape-Extension für den Selektionsexport."""
    target_dir = _get_inkscape_extensions_dir()
    copied_files = _copy_selection_extension(target_dir)
    installed_files = ", ".join(path.name for path in copied_files)
    return (
        f"Extension installiert nach {target_dir}: {installed_files}. "
        f"Bitte Inkscape neu starten und danach {SELECTION_EXTENSION_MENU_PATH} verwenden."
    )


def register_elements_commands(subparsers):
    """Registriert Element-Befehle im CLI."""
    parser = subparsers.add_parser("remove-elements", help="Elemente per ID entfernen")
    parser.add_argument("--file", required=True, help="SVG-Datei")
    parser.add_argument("--ids", required=True, help="Komma-separierte Element-IDs")
    parser.add_argument("--backup", action="store_true", help="Backup erstellen")
    parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, nicht ändern")
    parser.set_defaults(func=cmd_remove_elements)

    parser = subparsers.add_parser(
        "select-elements",
        help="Elemente in Inkscape auswählen",
    )
    parser.add_argument("--file", required=True, help="SVG-Datei")
    parser.add_argument("--ids", required=True, help="Komma-separierte Element-IDs")
    parser.set_defaults(func=cmd_select_elements)

    parser = subparsers.add_parser(
        "get-selection",
        help="Aktuelle Inkscape-Selektion auslesen",
    )
    parser.add_argument("--file", required=True, help="SVG-Datei")
    parser.set_defaults(func=cmd_get_selection)

    parser = subparsers.add_parser(
        "find-similar-elements",
        help="Ähnliche Elemente zur Selektion finden",
    )
    parser.add_argument("--file", required=True, help="SVG-Datei")
    parser.add_argument(
        "--ids",
        help="Optionale Referenz-IDs. Standard: zuletzt exportierte Inkscape-Selektion",
    )
    parser.add_argument(
        "--select",
        action="store_true",
        help="Gefundene Elemente direkt in Inkscape auswählen",
    )
    parser.set_defaults(func=cmd_find_similar_elements)

    parser = subparsers.add_parser(
        "install-extension",
        help="inkctl Inkscape-Extension installieren",
    )
    parser.set_defaults(func=cmd_install_extension)
