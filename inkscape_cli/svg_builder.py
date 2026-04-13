"""SVG Builder - Erstellt und bearbeitet SVG-Dateien direkt via lxml."""

from lxml import etree
from typing import Optional
import os

from .config import (
    SVG_NS, INKSCAPE_NS, SODIPODI_NS, NSMAP,
    DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_VIEWBOX,
)


class SVGBuilder:
    """Erstellt und bearbeitet SVG-Dokumente programmatisch."""

    def __init__(self, filepath: Optional[str] = None):
        """Erstellt einen neuen SVGBuilder.

        Args:
            filepath: Optionaler Pfad zu einer bestehenden SVG-Datei.
                      Wenn None, wird ein leeres SVG-Dokument erstellt.
        """
        if filepath and os.path.exists(filepath):
            self.tree = etree.parse(filepath)
            self.root = self.tree.getroot()
        else:
            self.root = etree.Element(
                f"{{{SVG_NS}}}svg",
                nsmap=NSMAP,
            )
            self.root.set("width", DEFAULT_WIDTH)
            self.root.set("height", DEFAULT_HEIGHT)
            self.root.set("viewBox", DEFAULT_VIEWBOX)
            self.root.set("version", "1.1")
            self.tree = etree.ElementTree(self.root)

    # ─── Formen ──────────────────────────────────────────

    def add_rect(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 50,
        fill: str = "#4A90D9",
        stroke: str = "none",
        stroke_width: float = 0,
        rx: float = 0,
        ry: float = 0,
        element_id: Optional[str] = None,
        parent: Optional[etree._Element] = None,
    ) -> etree._Element:
        """Fügt ein Rechteck hinzu."""
        target = parent if parent is not None else self.root
        rect = etree.SubElement(target, f"{{{SVG_NS}}}rect")
        rect.set("x", str(x))
        rect.set("y", str(y))
        rect.set("width", str(width))
        rect.set("height", str(height))
        rect.set("style", f"fill:{fill};stroke:{stroke};stroke-width:{stroke_width}")
        if rx:
            rect.set("rx", str(rx))
        if ry:
            rect.set("ry", str(ry))
        if element_id:
            rect.set("id", element_id)
        return rect

    def add_circle(
        self,
        cx: float = 50,
        cy: float = 50,
        r: float = 25,
        fill: str = "#E74C3C",
        stroke: str = "none",
        stroke_width: float = 0,
        element_id: Optional[str] = None,
        parent: Optional[etree._Element] = None,
    ) -> etree._Element:
        """Fügt einen Kreis hinzu."""
        target = parent if parent is not None else self.root
        circle = etree.SubElement(target, f"{{{SVG_NS}}}circle")
        circle.set("cx", str(cx))
        circle.set("cy", str(cy))
        circle.set("r", str(r))
        circle.set("style", f"fill:{fill};stroke:{stroke};stroke-width:{stroke_width}")
        if element_id:
            circle.set("id", element_id)
        return circle

    def add_ellipse(
        self,
        cx: float = 50,
        cy: float = 50,
        rx: float = 40,
        ry: float = 25,
        fill: str = "#2ECC71",
        stroke: str = "none",
        stroke_width: float = 0,
        element_id: Optional[str] = None,
        parent: Optional[etree._Element] = None,
    ) -> etree._Element:
        """Fügt eine Ellipse hinzu."""
        target = parent if parent is not None else self.root
        ellipse = etree.SubElement(target, f"{{{SVG_NS}}}ellipse")
        ellipse.set("cx", str(cx))
        ellipse.set("cy", str(cy))
        ellipse.set("rx", str(rx))
        ellipse.set("ry", str(ry))
        ellipse.set("style", f"fill:{fill};stroke:{stroke};stroke-width:{stroke_width}")
        if element_id:
            ellipse.set("id", element_id)
        return ellipse

    def add_line(
        self,
        x1: float = 0,
        y1: float = 0,
        x2: float = 100,
        y2: float = 100,
        stroke: str = "#333333",
        stroke_width: float = 2,
        element_id: Optional[str] = None,
        parent: Optional[etree._Element] = None,
    ) -> etree._Element:
        """Fügt eine Linie hinzu."""
        target = parent if parent is not None else self.root
        line = etree.SubElement(target, f"{{{SVG_NS}}}line")
        line.set("x1", str(x1))
        line.set("y1", str(y1))
        line.set("x2", str(x2))
        line.set("y2", str(y2))
        line.set("style", f"stroke:{stroke};stroke-width:{stroke_width}")
        if element_id:
            line.set("id", element_id)
        return line

    def add_path(
        self,
        d: str,
        fill: str = "none",
        stroke: str = "#333333",
        stroke_width: float = 2,
        element_id: Optional[str] = None,
        parent: Optional[etree._Element] = None,
    ) -> etree._Element:
        """Fügt einen Pfad hinzu.

        Args:
            d: SVG-Pfaddaten (z.B. "M 10 10 L 90 90 Z").
        """
        target = parent if parent is not None else self.root
        path = etree.SubElement(target, f"{{{SVG_NS}}}path")
        path.set("d", d)
        path.set("style", f"fill:{fill};stroke:{stroke};stroke-width:{stroke_width}")
        if element_id:
            path.set("id", element_id)
        return path

    # ─── Text ────────────────────────────────────────────

    def add_text(
        self,
        text: str,
        x: float = 10,
        y: float = 30,
        font_size: float = 16,
        font_family: str = "sans-serif",
        fill: str = "#000000",
        font_weight: str = "normal",
        text_anchor: str = "start",
        element_id: Optional[str] = None,
        parent: Optional[etree._Element] = None,
    ) -> etree._Element:
        """Fügt einen Text hinzu."""
        target = parent if parent is not None else self.root
        text_el = etree.SubElement(target, f"{{{SVG_NS}}}text")
        text_el.set("x", str(x))
        text_el.set("y", str(y))
        text_el.set(
            "style",
            f"font-size:{font_size}px;font-family:{font_family};"
            f"fill:{fill};font-weight:{font_weight};text-anchor:{text_anchor}"
        )
        text_el.text = text
        if element_id:
            text_el.set("id", element_id)
        return text_el

    # ─── Ebenen & Gruppen ────────────────────────────────

    def add_layer(
        self,
        label: str,
        element_id: Optional[str] = None,
    ) -> etree._Element:
        """Fügt eine Inkscape-Ebene hinzu.

        Args:
            label: Name der Ebene (wird in Inkscape angezeigt).
        """
        layer = etree.SubElement(self.root, f"{{{SVG_NS}}}g")
        layer.set(f"{{{INKSCAPE_NS}}}groupmode", "layer")
        layer.set(f"{{{INKSCAPE_NS}}}label", label)
        if element_id:
            layer.set("id", element_id)
        else:
            layer.set("id", f"layer-{label.lower().replace(' ', '-')}")
        return layer

    def add_group(
        self,
        element_id: Optional[str] = None,
        parent: Optional[etree._Element] = None,
    ) -> etree._Element:
        """Fügt eine Gruppe hinzu."""
        target = parent if parent is not None else self.root
        group = etree.SubElement(target, f"{{{SVG_NS}}}g")
        if element_id:
            group.set("id", element_id)
        return group

    # ─── Styles & Attribute ──────────────────────────────

    def set_style(self, element: etree._Element, **styles) -> None:
        """Setzt CSS-Styles auf ein Element.

        Args:
            element: Das SVG-Element.
            **styles: CSS-Eigenschaften als Keyword-Argumente,
                      z.B. fill="#ff0000", stroke_width=2
        """
        style_parts = []
        for key, value in styles.items():
            css_key = key.replace("_", "-")
            style_parts.append(f"{css_key}:{value}")
        element.set("style", ";".join(style_parts))

    def set_transform(self, element: etree._Element, transform: str) -> None:
        """Setzt eine Transformation auf ein Element.

        Args:
            transform: SVG-Transform-String, z.B. "translate(10, 20) rotate(45)"
        """
        element.set("transform", transform)

    # ─── Element finden ──────────────────────────────────

    def find_by_id(self, element_id: str) -> Optional[etree._Element]:
        """Findet ein Element anhand seiner ID."""
        results = self.root.xpath(
            f'//*[@id="{element_id}"]',
            namespaces={"svg": SVG_NS},
        )
        return results[0] if results else None

    def find_all(self, tag: str) -> list[etree._Element]:
        """Findet alle Elemente eines bestimmten Typs.

        Args:
            tag: SVG-Tag-Name ohne Namespace, z.B. "rect", "text", "g".
        """
        return self.root.findall(f".//{{{SVG_NS}}}{tag}")

    def remove_element(self, element: etree._Element) -> None:
        """Entfernt ein Element aus dem Dokument."""
        parent = element.getparent()
        if parent is not None:
            parent.remove(element)

    # ─── SVG Info ────────────────────────────────────────

    def get_info(self) -> dict:
        """Gibt Informationen über das SVG-Dokument zurück."""
        info = {
            "width": self.root.get("width", "unbekannt"),
            "height": self.root.get("height", "unbekannt"),
            "viewBox": self.root.get("viewBox", "nicht gesetzt"),
            "elements": {},
            "layers": [],
        }

        # Elemente zählen
        for tag in ["rect", "circle", "ellipse", "line", "path", "text", "g", "image"]:
            elements = self.find_all(tag)
            if elements:
                info["elements"][tag] = len(elements)

        # Ebenen auflisten
        for g in self.find_all("g"):
            groupmode = g.get(f"{{{INKSCAPE_NS}}}groupmode")
            if groupmode == "layer":
                label = g.get(f"{{{INKSCAPE_NS}}}label", "Ohne Name")
                info["layers"].append(label)

        return info

    # ─── Speichern ───────────────────────────────────────

    def save(self, filepath: str) -> None:
        """Speichert das SVG-Dokument in eine Datei."""
        self.tree.write(
            filepath,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )

    def to_string(self) -> str:
        """Gibt das SVG als String zurück."""
        return etree.tostring(
            self.root,
            pretty_print=True,
            xml_declaration=True,
            encoding="unicode",
        )
