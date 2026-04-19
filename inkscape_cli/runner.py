"""Inkscape CLI Runner - Führt Inkscape-Actions über die Kommandozeile aus."""

import subprocess
import shlex
from typing import Optional

from .config import get_inkscape_path


class InkscapeRunner:
    """Wrapper um die Inkscape CLI zum Ausführen von Actions."""

    def __init__(self, inkscape_path: Optional[str] = None):
        self.inkscape_path = inkscape_path or get_inkscape_path()

    def run_actions(
        self,
        actions: str,
        input_file: Optional[str] = None,
        batch: bool = True,
    ) -> subprocess.CompletedProcess:
        """Führt Inkscape-Actions aus.

        Args:
            actions: Semikolon-getrennte Action-Strings,
                     z.B. "export-filename:out.png; export-do"
            input_file: Optionale SVG-Eingabedatei.
            batch: Wenn True, wird --batch-process verwendet.

        Returns:
            CompletedProcess mit stdout/stderr.
        """
        cmd = [self.inkscape_path]

        if batch:
            cmd.append("--batch-process")

        cmd.extend(["--actions", actions])

        if input_file:
            cmd.append(input_file)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result

    def export_png(
        self,
        input_file: str,
        output_file: str,
        dpi: int = 96,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> subprocess.CompletedProcess:
        """Exportiert eine SVG-Datei als PNG.

        Args:
            input_file: Pfad zur SVG-Datei.
            output_file: Pfad für die PNG-Ausgabe.
            dpi: Auflösung in DPI (Standard: 96).
            width: Optionale Breite in Pixeln.
            height: Optionale Höhe in Pixeln.
        """
        actions = f"export-filename:{output_file}; export-dpi:{dpi}"

        if width:
            actions += f"; export-width:{width}"
        if height:
            actions += f"; export-height:{height}"

        actions += "; export-do"
        return self.run_actions(actions, input_file=input_file)

    def export_pdf(
        self,
        input_file: str,
        output_file: str,
    ) -> subprocess.CompletedProcess:
        """Exportiert eine SVG-Datei als PDF."""
        actions = f"export-filename:{output_file}; export-type:pdf; export-do"
        return self.run_actions(actions, input_file=input_file)

    def get_action_list(self) -> list[str]:
        """Gibt die Liste aller verfügbaren Inkscape-Actions zurück."""
        result = subprocess.run(
            [self.inkscape_path, "--action-list"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return []

    def query_all(self, input_file: str) -> dict[str, dict[str, float]]:
        """Liest Bounding-Boxen aller SVG-Objekte via Inkscape aus."""
        result = subprocess.run(
            [self.inkscape_path, "--query-all", input_file],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            message = result.stderr.strip() or "query-all fehlgeschlagen."
            raise RuntimeError(message)

        boxes: dict[str, dict[str, float]] = {}
        for line in result.stdout.splitlines():
            parts = [part.strip() for part in line.split(",")]
            if len(parts) != 5:
                continue
            element_id, x, y, width, height = parts
            boxes[element_id] = {
                "x": float(x),
                "y": float(y),
                "width": float(width),
                "height": float(height),
            }
        return boxes

    def get_version(self) -> str:
        """Gibt die installierte Inkscape-Version zurück."""
        result = subprocess.run(
            [self.inkscape_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else "Unbekannt"
