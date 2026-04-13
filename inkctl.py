#!/usr/bin/env python3
"""
inkctl - Inkscape CLI Addon
Steuert Inkscape und bearbeitet SVG-Dateien via Kommandozeile.

Nutzung:
    python inkctl.py <befehl> [optionen]
    python inkctl.py --help
"""

import argparse
import sys
import json

from inkscape_cli.svg_builder import SVGBuilder
from inkscape_cli.runner import InkscapeRunner
from commands.shapes import register_shapes_commands
from commands.text import register_text_commands
from commands.layers import register_layers_commands
from commands.colors import register_colors_commands
from commands.elements import register_elements_commands


def cmd_info(args) -> str:
    """Zeigt Informationen über eine SVG-Datei."""
    if not args.file:
        return "Fehler: --file ist erforderlich."

    svg = SVGBuilder(args.file)
    info = svg.get_info()

    lines = [
        f"Datei: {args.file}",
        f"Größe: {info['width']} x {info['height']}",
        f"ViewBox: {info['viewBox']}",
        "",
        "Elemente:",
    ]

    if info["elements"]:
        for tag, count in info["elements"].items():
            lines.append(f"  {tag}: {count}")
    else:
        lines.append("  (keine)")

    if info["layers"]:
        lines.append("")
        lines.append("Ebenen:")
        for name in info["layers"]:
            lines.append(f"  - {name}")

    if args.json:
        return json.dumps(info, indent=2, ensure_ascii=False)

    return "\n".join(lines)


def cmd_new(args) -> str:
    """Erstellt eine neue leere SVG-Datei."""
    svg = SVGBuilder()

    if args.width:
        svg.root.set("width", args.width)
    if args.height:
        svg.root.set("height", args.height)

    output = args.output or "new.svg"
    svg.save(output)
    return f"Neue SVG-Datei erstellt: {output}"


def cmd_export(args) -> str:
    """Exportiert eine SVG-Datei in ein anderes Format."""
    runner = InkscapeRunner()

    fmt = args.format.lower()
    if fmt == "png":
        result = runner.export_png(
            args.file,
            args.output,
            dpi=args.dpi,
            width=args.width,
            height=args.height,
        )
    elif fmt == "pdf":
        result = runner.export_pdf(args.file, args.output)
    else:
        return f"Fehler: Format '{fmt}' nicht unterstützt. Verfügbar: png, pdf"

    if result.returncode == 0:
        return f"Export erfolgreich: {args.output}"
    else:
        return f"Export fehlgeschlagen:\n{result.stderr}"


def cmd_inkscape_version(args) -> str:
    """Zeigt die installierte Inkscape-Version."""
    try:
        runner = InkscapeRunner()
        return runner.get_version()
    except FileNotFoundError as e:
        return str(e)


def cmd_actions(args) -> str:
    """Führt rohe Inkscape-Actions aus."""
    runner = InkscapeRunner()
    result = runner.run_actions(
        args.actions,
        input_file=args.file,
    )
    output_parts = []
    if result.stdout:
        output_parts.append(result.stdout)
    if result.stderr:
        output_parts.append(f"[stderr] {result.stderr}")
    if result.returncode != 0:
        output_parts.append(f"[Exit-Code: {result.returncode}]")
    return "\n".join(output_parts) if output_parts else "Actions ausgeführt (keine Ausgabe)."


def main():
    parser = argparse.ArgumentParser(
        prog="inkctl",
        description="Inkscape CLI Addon - SVG-Dateien erstellen und bearbeiten",
    )
    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle")

    # --- Info ---
    info_parser = subparsers.add_parser("info", help="SVG-Dateiinfos anzeigen")
    info_parser.add_argument("--file", required=True, help="SVG-Datei")
    info_parser.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    info_parser.set_defaults(func=cmd_info)

    # --- Neue Datei ---
    new_parser = subparsers.add_parser("new", help="Neue SVG-Datei erstellen")
    new_parser.add_argument("--width", default=None, help="Breite (z.B. 210mm, 800px)")
    new_parser.add_argument("--height", default=None, help="Höhe (z.B. 297mm, 600px)")
    new_parser.add_argument("--output", "-o", default="new.svg", help="Ausgabedatei")
    new_parser.set_defaults(func=cmd_new)

    # --- Export ---
    export_parser = subparsers.add_parser("export", help="SVG exportieren (PNG, PDF)")
    export_parser.add_argument("--file", required=True, help="SVG-Eingabedatei")
    export_parser.add_argument("--output", "-o", required=True, help="Ausgabedatei")
    export_parser.add_argument("--format", "-f", default="png", help="Format: png, pdf")
    export_parser.add_argument("--dpi", type=int, default=96, help="DPI (nur PNG)")
    export_parser.add_argument("--width", type=int, default=None, help="Breite in px (nur PNG)")
    export_parser.add_argument("--height", type=int, default=None, help="Höhe in px (nur PNG)")
    export_parser.set_defaults(func=cmd_export)

    # --- Inkscape-Version ---
    version_parser = subparsers.add_parser("version", help="Inkscape-Version anzeigen")
    version_parser.set_defaults(func=cmd_inkscape_version)

    # --- Rohe Actions ---
    actions_parser = subparsers.add_parser("actions", help="Rohe Inkscape-Actions ausführen")
    actions_parser.add_argument("actions", help='Action-String (z.B. "export-filename:out.png; export-do")')
    actions_parser.add_argument("--file", default=None, help="SVG-Eingabedatei")
    actions_parser.set_defaults(func=cmd_actions)

    # --- Befehle aus Modulen registrieren ---
    register_shapes_commands(subparsers)
    register_text_commands(subparsers)
    register_layers_commands(subparsers)
    register_colors_commands(subparsers)
    register_elements_commands(subparsers)

    # --- Parse & Execute ---
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    result = args.func(args)
    print(result)


if __name__ == "__main__":
    main()
