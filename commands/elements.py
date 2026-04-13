"""Befehle zum Verwalten von SVG-Elementen per ID."""

import json
import os
import shutil
import sys
from importlib import resources
from pathlib import Path

from inkscape_cli.svg_builder import SVGBuilder

SELECTION_EXPORT_PATH = Path("/tmp/inkscape_selection.json")
SELECTION_EXTENSION_FILES = ("export_selection.py", "export_selection.inx")


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
    from inkscape_cli.runner import InkscapeRunner

    runner = InkscapeRunner()
    ids = [element_id.strip() for element_id in args.ids.split(",") if element_id.strip()]

    action_parts = [f"select-by-id:{element_id}" for element_id in ids]
    actions = "; ".join(action_parts)

    result = runner.run_actions(actions, input_file=args.file, batch=False)

    if result.returncode == 0:
        return f"{len(ids)} Elemente in Inkscape ausgewählt."
    return f"Fehler: {result.stderr}"


def cmd_get_selection(args) -> str:
    """Liest die zuletzt exportierte Inkscape-Selektion aus."""
    if not SELECTION_EXPORT_PATH.exists():
        return json.dumps(
            {
                "error": (
                    "Keine Selektion gefunden. Bitte zuerst in Inkscape: "
                    "Extensions > inkctl > Export Selection IDs ausführen."
                )
            },
            indent=2,
            ensure_ascii=False,
        )

    with SELECTION_EXPORT_PATH.open(encoding="utf-8") as selection_file:
        data = json.load(selection_file)

    exported_file = data.get("file")
    if exported_file:
        requested_file = _normalize_file_path(args.file)
        if _normalize_file_path(exported_file) != requested_file:
            return json.dumps(
                {
                    "error": "Die exportierte Selektion gehört zu einer anderen Datei.",
                    "requested_file": requested_file,
                    "selection_file": exported_file,
                },
                indent=2,
                ensure_ascii=False,
            )

    return json.dumps(data, indent=2, ensure_ascii=False)


def cmd_install_extension(args) -> str:
    """Installiert die inkctl-Inkscape-Extension für den Selektionsexport."""
    target_dir = _get_inkscape_extensions_dir()
    copied_files = _copy_selection_extension(target_dir)
    installed_files = ", ".join(path.name for path in copied_files)
    return (
        f"Extension installiert nach {target_dir}: {installed_files}. "
        "Bitte Inkscape neu starten."
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
        "install-extension",
        help="inkctl Inkscape-Extension installieren",
    )
    parser.set_defaults(func=cmd_install_extension)
