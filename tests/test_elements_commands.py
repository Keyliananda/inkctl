import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

from commands import elements


class GetSelectionCommandTests(unittest.TestCase):
    def test_returns_error_when_selection_file_is_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            selection_path = Path(tmpdir) / "inkscape_selection.json"
            svg_path = Path(tmpdir) / "drawing.svg"
            svg_path.write_text("<svg/>", encoding="utf-8")

            with mock.patch.object(elements, "SELECTION_EXPORT_PATH", selection_path):
                output = elements.cmd_get_selection(Namespace(file=str(svg_path)))

        data = json.loads(output)
        self.assertIn("error", data)

    def test_returns_selection_when_exported_file_matches(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            selection_path = Path(tmpdir) / "inkscape_selection.json"
            svg_path = Path(tmpdir) / "drawing.svg"
            svg_path.write_text("<svg/>", encoding="utf-8")
            selection_path.write_text(
                json.dumps(
                    {
                        "file": str(svg_path),
                        "selected_ids": ["rect1", "circle2"],
                        "count": 2,
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(elements, "SELECTION_EXPORT_PATH", selection_path):
                output = elements.cmd_get_selection(Namespace(file=str(svg_path)))

        data = json.loads(output)
        self.assertEqual(data["selected_ids"], ["rect1", "circle2"])
        self.assertEqual(data["count"], 2)

    def test_returns_error_when_selection_belongs_to_another_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            selection_path = Path(tmpdir) / "inkscape_selection.json"
            requested_svg_path = Path(tmpdir) / "requested.svg"
            exported_svg_path = Path(tmpdir) / "other.svg"
            requested_svg_path.write_text("<svg/>", encoding="utf-8")
            exported_svg_path.write_text("<svg/>", encoding="utf-8")
            selection_path.write_text(
                json.dumps(
                    {
                        "file": str(exported_svg_path),
                        "selected_ids": ["rect1"],
                        "count": 1,
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(elements, "SELECTION_EXPORT_PATH", selection_path):
                output = elements.cmd_get_selection(Namespace(file=str(requested_svg_path)))

        data = json.loads(output)
        self.assertEqual(
            data["error"],
            "Die exportierte Selektion gehört zu einer anderen Datei.",
        )
        self.assertEqual(data["selection_file"], str(exported_svg_path))


class InstallExtensionCommandTests(unittest.TestCase):
    def test_installs_selection_extension_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_dir = Path(tmpdir) / "extensions"

            with mock.patch.object(elements, "_get_inkscape_extensions_dir", return_value=target_dir):
                output = elements.cmd_install_extension(Namespace())

            self.assertTrue((target_dir / "export_selection.py").exists())
            self.assertTrue((target_dir / "export_selection.inx").exists())
            self.assertIn(str(target_dir), output)


if __name__ == "__main__":
    unittest.main()
