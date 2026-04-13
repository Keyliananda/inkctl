"""Befehle zum Verwalten von Ebenen und Gruppen."""

from inkscape_cli.svg_builder import SVGBuilder


def add_layer(args) -> str:
    """Fügt eine Ebene zu einer SVG-Datei hinzu."""
    svg = SVGBuilder(args.file if hasattr(args, 'file') and args.file else None)

    svg.add_layer(
        label=args.name,
        element_id=args.id if hasattr(args, 'id') else None,
    )

    output = args.output or args.file or "output.svg"
    svg.save(output)
    return f"Ebene '{args.name}' hinzugefügt: {output}"


def list_layers(args) -> str:
    """Listet alle Ebenen einer SVG-Datei auf."""
    if not args.file:
        return "Fehler: --file ist erforderlich."

    svg = SVGBuilder(args.file)
    info = svg.get_info()

    if not info["layers"]:
        return "Keine Ebenen gefunden."

    lines = ["Ebenen:"]
    for i, name in enumerate(info["layers"], 1):
        lines.append(f"  {i}. {name}")
    return "\n".join(lines)


def register_layers_commands(subparsers):
    """Registriert alle Ebenen-Befehle im CLI."""

    # --- Ebene hinzufügen ---
    layer_parser = subparsers.add_parser("add-layer", help="Fügt eine Ebene hinzu")
    layer_parser.add_argument("name", help="Name der Ebene")
    layer_parser.add_argument("--id", default=None, help="Element-ID")
    layer_parser.add_argument("--file", default=None, help="Bestehende SVG-Datei bearbeiten")
    layer_parser.add_argument("--output", "-o", default=None, help="Ausgabedatei")
    layer_parser.set_defaults(func=add_layer)

    # --- Ebenen auflisten ---
    list_parser = subparsers.add_parser("list-layers", help="Listet Ebenen auf")
    list_parser.add_argument("--file", required=True, help="SVG-Datei")
    list_parser.set_defaults(func=list_layers)
