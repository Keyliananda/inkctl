"""Befehle zum Erstellen und Bearbeiten von Text."""

from inkscape_cli.svg_builder import SVGBuilder


def add_text(args) -> str:
    """Fügt Text zu einer SVG-Datei hinzu."""
    svg = SVGBuilder(args.file if hasattr(args, 'file') and args.file else None)

    svg.add_text(
        text=args.text,
        x=args.x,
        y=args.y,
        font_size=args.font_size,
        font_family=args.font_family,
        fill=args.fill,
        font_weight=args.font_weight,
        text_anchor=args.text_anchor,
        element_id=args.id if hasattr(args, 'id') else None,
    )

    output = args.output or args.file or "output.svg"
    svg.save(output)
    return f"Text hinzugefügt und gespeichert: {output}"


def register_text_commands(subparsers):
    """Registriert alle Text-Befehle im CLI."""

    text_parser = subparsers.add_parser("add-text", help="Fügt Text hinzu")
    text_parser.add_argument("text", help="Der Text-Inhalt")
    text_parser.add_argument("--x", type=float, default=10, help="X-Position")
    text_parser.add_argument("--y", type=float, default=30, help="Y-Position")
    text_parser.add_argument("--font-size", type=float, default=16, help="Schriftgröße in px")
    text_parser.add_argument("--font-family", default="sans-serif", help="Schriftart")
    text_parser.add_argument("--fill", default="#000000", help="Textfarbe")
    text_parser.add_argument("--font-weight", default="normal", help="Schriftstärke (normal, bold)")
    text_parser.add_argument("--text-anchor", default="start", help="Ausrichtung (start, middle, end)")
    text_parser.add_argument("--id", default=None, help="Element-ID")
    text_parser.add_argument("--file", default=None, help="Bestehende SVG-Datei bearbeiten")
    text_parser.add_argument("--output", "-o", default=None, help="Ausgabedatei")
    text_parser.set_defaults(func=add_text)
