"""Befehle zum Erstellen und Bearbeiten von Formen."""

from inkscape_cli.svg_builder import SVGBuilder


def create_rect(args) -> str:
    """Erstellt eine SVG-Datei mit einem Rechteck."""
    svg = SVGBuilder(args.file if hasattr(args, 'file') and args.file else None)

    svg.add_rect(
        x=args.x,
        y=args.y,
        width=args.width,
        height=args.height,
        fill=args.fill,
        stroke=args.stroke,
        stroke_width=args.stroke_width,
        rx=args.rx,
        element_id=args.id if hasattr(args, 'id') else None,
    )

    output = args.output or args.file or "output.svg"
    svg.save(output)
    return f"Rechteck erstellt und gespeichert: {output}"


def create_circle(args) -> str:
    """Erstellt eine SVG-Datei mit einem Kreis."""
    svg = SVGBuilder(args.file if hasattr(args, 'file') and args.file else None)

    svg.add_circle(
        cx=args.cx,
        cy=args.cy,
        r=args.r,
        fill=args.fill,
        stroke=args.stroke,
        stroke_width=args.stroke_width,
        element_id=args.id if hasattr(args, 'id') else None,
    )

    output = args.output or args.file or "output.svg"
    svg.save(output)
    return f"Kreis erstellt und gespeichert: {output}"


def create_ellipse(args) -> str:
    """Erstellt eine SVG-Datei mit einer Ellipse."""
    svg = SVGBuilder(args.file if hasattr(args, 'file') and args.file else None)

    svg.add_ellipse(
        cx=args.cx,
        cy=args.cy,
        rx=args.rx,
        ry=args.ry,
        fill=args.fill,
        stroke=args.stroke,
        stroke_width=args.stroke_width,
        element_id=args.id if hasattr(args, 'id') else None,
    )

    output = args.output or args.file or "output.svg"
    svg.save(output)
    return f"Ellipse erstellt und gespeichert: {output}"


def register_shapes_commands(subparsers):
    """Registriert alle Formen-Befehle im CLI."""

    # --- Rechteck ---
    rect_parser = subparsers.add_parser("create-rect", help="Erstellt ein Rechteck")
    rect_parser.add_argument("--x", type=float, default=10, help="X-Position")
    rect_parser.add_argument("--y", type=float, default=10, help="Y-Position")
    rect_parser.add_argument("--width", type=float, default=100, help="Breite")
    rect_parser.add_argument("--height", type=float, default=50, help="Höhe")
    rect_parser.add_argument("--fill", default="#4A90D9", help="Füllfarbe")
    rect_parser.add_argument("--stroke", default="none", help="Konturfarbe")
    rect_parser.add_argument("--stroke-width", type=float, default=0, help="Konturbreite")
    rect_parser.add_argument("--rx", type=float, default=0, help="Eckenradius")
    rect_parser.add_argument("--id", default=None, help="Element-ID")
    rect_parser.add_argument("--file", default=None, help="Bestehende SVG-Datei bearbeiten")
    rect_parser.add_argument("--output", "-o", default=None, help="Ausgabedatei")
    rect_parser.set_defaults(func=create_rect)

    # --- Kreis ---
    circle_parser = subparsers.add_parser("create-circle", help="Erstellt einen Kreis")
    circle_parser.add_argument("--cx", type=float, default=50, help="X-Mittelpunkt")
    circle_parser.add_argument("--cy", type=float, default=50, help="Y-Mittelpunkt")
    circle_parser.add_argument("--r", type=float, default=25, help="Radius")
    circle_parser.add_argument("--fill", default="#E74C3C", help="Füllfarbe")
    circle_parser.add_argument("--stroke", default="none", help="Konturfarbe")
    circle_parser.add_argument("--stroke-width", type=float, default=0, help="Konturbreite")
    circle_parser.add_argument("--id", default=None, help="Element-ID")
    circle_parser.add_argument("--file", default=None, help="Bestehende SVG-Datei bearbeiten")
    circle_parser.add_argument("--output", "-o", default=None, help="Ausgabedatei")
    circle_parser.set_defaults(func=create_circle)

    # --- Ellipse ---
    ellipse_parser = subparsers.add_parser("create-ellipse", help="Erstellt eine Ellipse")
    ellipse_parser.add_argument("--cx", type=float, default=50, help="X-Mittelpunkt")
    ellipse_parser.add_argument("--cy", type=float, default=50, help="Y-Mittelpunkt")
    ellipse_parser.add_argument("--rx", type=float, default=40, help="X-Radius")
    ellipse_parser.add_argument("--ry", type=float, default=25, help="Y-Radius")
    ellipse_parser.add_argument("--fill", default="#2ECC71", help="Füllfarbe")
    ellipse_parser.add_argument("--stroke", default="none", help="Konturfarbe")
    ellipse_parser.add_argument("--stroke-width", type=float, default=0, help="Konturbreite")
    ellipse_parser.add_argument("--id", default=None, help="Element-ID")
    ellipse_parser.add_argument("--file", default=None, help="Bestehende SVG-Datei bearbeiten")
    ellipse_parser.add_argument("--output", "-o", default=None, help="Ausgabedatei")
    ellipse_parser.set_defaults(func=create_ellipse)
