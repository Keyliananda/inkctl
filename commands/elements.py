"""Befehle zum Verwalten von SVG-Elementen per ID."""

import json
import shutil

from inkscape_cli.svg_builder import SVGBuilder


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
