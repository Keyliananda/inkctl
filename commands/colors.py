"""Befehle zum Ändern von Farben und Styles."""

from lxml import etree
from inkscape_cli.svg_builder import SVGBuilder
from inkscape_cli.config import SVG_NS


def change_fill(args) -> str:
    """Ändert die Füllfarbe eines Elements."""
    if not args.file:
        return "Fehler: --file ist erforderlich."

    svg = SVGBuilder(args.file)

    if args.element_id:
        el = svg.find_by_id(args.element_id)
        if not el:
            return f"Fehler: Element mit ID '{args.element_id}' nicht gefunden."
        _update_style_property(el, "fill", args.color)
        count = 1
    elif args.tag:
        elements = svg.find_all(args.tag)
        for el in elements:
            _update_style_property(el, "fill", args.color)
        count = len(elements)
    else:
        return "Fehler: --element-id oder --tag muss angegeben werden."

    output = args.output or args.file
    svg.save(output)
    return f"Füllfarbe auf '{args.color}' geändert bei {count} Element(en): {output}"


def change_stroke(args) -> str:
    """Ändert die Konturfarbe eines Elements."""
    if not args.file:
        return "Fehler: --file ist erforderlich."

    svg = SVGBuilder(args.file)

    if args.element_id:
        el = svg.find_by_id(args.element_id)
        if not el:
            return f"Fehler: Element mit ID '{args.element_id}' nicht gefunden."
        _update_style_property(el, "stroke", args.color)
        if args.width is not None:
            _update_style_property(el, "stroke-width", str(args.width))
        count = 1
    elif args.tag:
        elements = svg.find_all(args.tag)
        for el in elements:
            _update_style_property(el, "stroke", args.color)
            if args.width is not None:
                _update_style_property(el, "stroke-width", str(args.width))
        count = len(elements)
    else:
        return "Fehler: --element-id oder --tag muss angegeben werden."

    output = args.output or args.file
    svg.save(output)
    return f"Kontur auf '{args.color}' geändert bei {count} Element(en): {output}"


def _update_style_property(element: etree._Element, prop: str, value: str) -> None:
    """Aktualisiert eine einzelne CSS-Eigenschaft im style-Attribut."""
    style = element.get("style", "")
    parts = [p.strip() for p in style.split(";") if p.strip()]

    updated = False
    new_parts = []
    for part in parts:
        if ":" in part:
            key, _ = part.split(":", 1)
            if key.strip() == prop:
                new_parts.append(f"{prop}:{value}")
                updated = True
            else:
                new_parts.append(part)
        else:
            new_parts.append(part)

    if not updated:
        new_parts.append(f"{prop}:{value}")

    element.set("style", ";".join(new_parts))


def register_colors_commands(subparsers):
    """Registriert alle Farb-Befehle im CLI."""

    # --- Füllfarbe ändern ---
    fill_parser = subparsers.add_parser("change-fill", help="Ändert die Füllfarbe")
    fill_parser.add_argument("color", help="Neue Farbe (z.B. #FF0000, red)")
    fill_parser.add_argument("--element-id", default=None, help="ID des Elements")
    fill_parser.add_argument("--tag", default=None, help="Alle Elemente dieses Typs (z.B. rect, circle)")
    fill_parser.add_argument("--file", required=True, help="SVG-Datei")
    fill_parser.add_argument("--output", "-o", default=None, help="Ausgabedatei")
    fill_parser.set_defaults(func=change_fill)

    # --- Kontur ändern ---
    stroke_parser = subparsers.add_parser("change-stroke", help="Ändert die Konturfarbe")
    stroke_parser.add_argument("color", help="Neue Farbe (z.B. #FF0000, red)")
    stroke_parser.add_argument("--width", type=float, default=None, help="Konturbreite")
    stroke_parser.add_argument("--element-id", default=None, help="ID des Elements")
    stroke_parser.add_argument("--tag", default=None, help="Alle Elemente dieses Typs")
    stroke_parser.add_argument("--file", required=True, help="SVG-Datei")
    stroke_parser.add_argument("--output", "-o", default=None, help="Ausgabedatei")
    stroke_parser.set_defaults(func=change_stroke)
