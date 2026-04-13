"""Konfiguration für das Inkscape CLI Addon."""

import shutil
import platform
import os

# Standard-Inkscape-Pfade je nach Betriebssystem
INKSCAPE_PATHS = {
    "Darwin": [  # macOS
        "/Applications/Inkscape.app/Contents/MacOS/inkscape",
        "/usr/local/bin/inkscape",
        "/opt/homebrew/bin/inkscape",
    ],
    "Linux": [
        "/usr/bin/inkscape",
        "/usr/local/bin/inkscape",
        "/snap/bin/inkscape",
    ],
    "Windows": [
        r"C:\Program Files\Inkscape\bin\inkscape.exe",
        r"C:\Program Files (x86)\Inkscape\bin\inkscape.exe",
    ],
}

# SVG Namespaces
SVG_NS = "http://www.w3.org/2000/svg"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
SODIPODI_NS = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
XLINK_NS = "http://www.w3.org/1999/xlink"

NSMAP = {
    None: SVG_NS,
    "inkscape": INKSCAPE_NS,
    "sodipodi": SODIPODI_NS,
    "xlink": XLINK_NS,
}

# Standard SVG-Dokumenteinstellungen
DEFAULT_WIDTH = "210mm"   # A4
DEFAULT_HEIGHT = "297mm"  # A4
DEFAULT_VIEWBOX = "0 0 210 297"


def find_inkscape() -> str:
    """Findet den Inkscape-Pfad auf dem System.

    Returns:
        Pfad zur Inkscape-Executable.

    Raises:
        FileNotFoundError: Wenn Inkscape nicht gefunden wird.
    """
    # Zuerst: ist 'inkscape' direkt im PATH?
    inkscape_in_path = shutil.which("inkscape")
    if inkscape_in_path:
        return inkscape_in_path

    # Dann: bekannte Pfade prüfen
    system = platform.system()
    candidates = INKSCAPE_PATHS.get(system, [])

    for path in candidates:
        if os.path.isfile(path):
            return path

    raise FileNotFoundError(
        f"Inkscape wurde nicht gefunden. Bitte installiere Inkscape 1.4+ "
        f"oder setze die Umgebungsvariable INKSCAPE_PATH.\n"
        f"Geprüfte Pfade: {candidates}"
    )


def get_inkscape_path() -> str:
    """Gibt den Inkscape-Pfad zurück (aus Umgebungsvariable oder Auto-Erkennung)."""
    env_path = os.environ.get("INKSCAPE_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path
    return find_inkscape()
