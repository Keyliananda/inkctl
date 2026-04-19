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
from typing import Any

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


def _get_subparsers_action(parser: argparse.ArgumentParser) -> argparse._SubParsersAction | None:
    """Liefert die Subparser-Action des Root-Parsers."""
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    return None


def _get_command_parsers(parser: argparse.ArgumentParser) -> dict[str, argparse.ArgumentParser]:
    """Liefert alle registrierten Command-Parser."""
    subparsers_action = _get_subparsers_action(parser)
    if subparsers_action is None:
        return {}
    return dict(subparsers_action.choices)


def _get_command_summaries(parser: argparse.ArgumentParser) -> dict[str, str]:
    """Liefert die Kurzbeschreibungen aller Commands."""
    subparsers_action = _get_subparsers_action(parser)
    if subparsers_action is None:
        return {}
    return {
        choice_action.dest: choice_action.help or ""
        for choice_action in subparsers_action._choices_actions
    }


def _normalize_json_value(value: Any) -> Any:
    """Wandelt argparse-Werte in JSON-kompatible Werte um."""
    if value is argparse.SUPPRESS:
        return None
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_normalize_json_value(item) for item in value]
    return str(value)


def _infer_argument_type(action: argparse.Action) -> str:
    """Leitet einen menschenlesbaren Argumenttyp aus argparse ab."""
    if isinstance(action, (argparse._StoreTrueAction, argparse._StoreFalseAction)):
        return "bool"
    if action.type is not None:
        return getattr(action.type, "__name__", str(action.type))
    if action.choices:
        return "choice"
    return "string"


def _is_argument_required(action: argparse.Action) -> bool:
    """Ermittelt, ob ein Argument zwingend angegeben werden muss."""
    if action.option_strings:
        return bool(action.required)
    return action.nargs not in ("?", "*")


def _serialize_argument(action: argparse.Action) -> dict[str, Any] | None:
    """Serialisiert ein argparse-Argument als JSON-Struktur."""
    if isinstance(action, (argparse._HelpAction, argparse._SubParsersAction)):
        return None

    payload = {
        "name": action.dest,
        "kind": "option" if action.option_strings else "positional",
        "option_strings": action.option_strings,
        "required": _is_argument_required(action),
        "type": _infer_argument_type(action),
        "help": action.help,
        "default": _normalize_json_value(action.default),
        "choices": _normalize_json_value(list(action.choices)) if action.choices else None,
        "nargs": action.nargs,
        "metavar": action.metavar,
    }
    return payload


def _serialize_command(
    name: str,
    parser: argparse.ArgumentParser,
    summary: str,
) -> dict[str, Any]:
    """Serialisiert einen Command-Parser inklusive Argumenten."""
    arguments = []
    for action in parser._actions:
        serialized = _serialize_argument(action)
        if serialized is not None:
            arguments.append(serialized)

    return {
        "name": name,
        "summary": summary,
        "description": parser.description or summary,
        "usage": parser.format_usage().strip(),
        "arguments": arguments,
    }


def build_capabilities_payload(parser: argparse.ArgumentParser) -> dict[str, Any]:
    """Erzeugt eine maschinenlesbare Übersicht aller CLI-Commands."""
    command_parsers = _get_command_parsers(parser)
    summaries = _get_command_summaries(parser)
    commands = [
        _serialize_command(name, command_parsers[name], summaries.get(name, ""))
        for name in command_parsers
    ]
    return {
        "program": parser.prog,
        "description": parser.description or "",
        "usage": parser.format_usage().strip(),
        "commands": commands,
    }


def build_help_json_payload(
    parser: argparse.ArgumentParser,
    command_name: str | None,
) -> tuple[dict[str, Any], int]:
    """Erzeugt JSON-Hilfe für das Root-CLI oder einen einzelnen Command."""
    if command_name is None:
        return build_capabilities_payload(parser), 0

    command_parsers = _get_command_parsers(parser)
    if command_name not in command_parsers:
        return {"error": f"Unbekannter Command: {command_name}"}, 2

    summaries = _get_command_summaries(parser)
    return _serialize_command(
        command_name,
        command_parsers[command_name],
        summaries.get(command_name, ""),
    ), 0


def cmd_capabilities(args, parser: argparse.ArgumentParser) -> str:
    """Gibt die verfügbaren CLI-Fähigkeiten aus."""
    payload = build_capabilities_payload(parser)
    if args.json:
        return json.dumps(payload, indent=2, ensure_ascii=False)

    lines = ["Verfügbare Befehle:"]
    for command in payload["commands"]:
        lines.append(f"- {command['name']}: {command['summary']}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Erstellt und registriert den kompletten CLI-Parser."""
    parser = argparse.ArgumentParser(
        prog="inkctl",
        description="Inkscape CLI Addon - SVG-Dateien erstellen und bearbeiten",
    )
    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle")

    # --- Info ---
    info_parser = subparsers.add_parser(
        "info",
        help="SVG-Dateiinfos anzeigen",
        description="SVG-Dateiinfos anzeigen",
    )
    info_parser.add_argument("--file", required=True, help="SVG-Datei")
    info_parser.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    info_parser.set_defaults(func=cmd_info)

    # --- Neue Datei ---
    new_parser = subparsers.add_parser(
        "new",
        help="Neue SVG-Datei erstellen",
        description="Neue SVG-Datei erstellen",
    )
    new_parser.add_argument("--width", default=None, help="Breite (z.B. 210mm, 800px)")
    new_parser.add_argument("--height", default=None, help="Höhe (z.B. 297mm, 600px)")
    new_parser.add_argument("--output", "-o", default="new.svg", help="Ausgabedatei")
    new_parser.set_defaults(func=cmd_new)

    # --- Export ---
    export_parser = subparsers.add_parser(
        "export",
        help="SVG exportieren (PNG, PDF)",
        description="SVG-Datei exportieren",
    )
    export_parser.add_argument("--file", required=True, help="SVG-Eingabedatei")
    export_parser.add_argument("--output", "-o", required=True, help="Ausgabedatei")
    export_parser.add_argument("--format", "-f", default="png", help="Format: png, pdf")
    export_parser.add_argument("--dpi", type=int, default=96, help="DPI (nur PNG)")
    export_parser.add_argument("--width", type=int, default=None, help="Breite in px (nur PNG)")
    export_parser.add_argument("--height", type=int, default=None, help="Höhe in px (nur PNG)")
    export_parser.set_defaults(func=cmd_export)

    # --- Inkscape-Version ---
    version_parser = subparsers.add_parser(
        "version",
        help="Inkscape-Version anzeigen",
        description="Inkscape-Version anzeigen",
    )
    version_parser.set_defaults(func=cmd_inkscape_version)

    # --- Rohe Actions ---
    actions_parser = subparsers.add_parser(
        "actions",
        help="Rohe Inkscape-Actions ausführen",
        description="Rohe Inkscape-Actions ausführen",
    )
    actions_parser.add_argument("actions", help='Action-String (z.B. "export-filename:out.png; export-do")')
    actions_parser.add_argument("--file", default=None, help="SVG-Eingabedatei")
    actions_parser.set_defaults(func=cmd_actions)

    # --- Capabilities ---
    capabilities_parser = subparsers.add_parser(
        "capabilities",
        help="CLI-Fähigkeiten auflisten",
        description="CLI-Fähigkeiten auflisten",
    )
    capabilities_parser.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    capabilities_parser.set_defaults(func=cmd_capabilities)

    # --- Befehle aus Modulen registrieren ---
    register_shapes_commands(subparsers)
    register_text_commands(subparsers)
    register_layers_commands(subparsers)
    register_colors_commands(subparsers)
    register_elements_commands(subparsers)
    return parser


def _wants_json_help(argv: list[str]) -> bool:
    """Erkennt die Sonderform '--help --json'."""
    return "--help" in argv and "--json" in argv


def _resolve_help_json_target(
    parser: argparse.ArgumentParser,
    argv: list[str],
) -> tuple[str | None, int]:
    """Ermittelt den Ziel-Command für JSON-Hilfe."""
    command_parsers = _get_command_parsers(parser)
    for token in argv:
        if token.startswith("-"):
            continue
        if token in command_parsers:
            return token, 0
        return token, 2
    return None, 0


def main(argv: list[str] | None = None) -> int:
    """CLI-Einstiegspunkt."""
    parser = build_parser()
    argv = sys.argv[1:] if argv is None else argv

    if _wants_json_help(argv):
        command_name, status_code = _resolve_help_json_target(parser, argv)
        payload, payload_status = build_help_json_payload(parser, command_name)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return payload_status if status_code == 0 else status_code

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "capabilities":
        result = cmd_capabilities(args, parser)
    else:
        result = args.func(args)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
