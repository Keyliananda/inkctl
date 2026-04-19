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


class FindSimilarElementsCommandTests(unittest.TestCase):
    def test_uses_exported_selection_and_returns_similar_ids(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            selection_path = Path(tmpdir) / "inkscape_selection.json"
            svg_path = Path(tmpdir) / "drawing.svg"
            svg_path.write_text(
                """
                <svg xmlns="http://www.w3.org/2000/svg">
                  <path id="ref1" stroke="#b5c3d1" vector-effect="non-scaling-stroke" d="M 0,0 L 5,5" />
                  <path id="match1" stroke="#b5c3d1" vector-effect="non-scaling-stroke" d="M 1,1 L 6,6" />
                  <path id="too-large" stroke="#b5c3d1" vector-effect="non-scaling-stroke" d="M 2,2 L 20,20" />
                  <path id="other-stroke" stroke="#808080" vector-effect="non-scaling-stroke" d="M 3,3 L 8,8" />
                </svg>
                """,
                encoding="utf-8",
            )
            selection_path.write_text(
                json.dumps(
                    {
                        "file": str(svg_path),
                        "selected_ids": ["ref1"],
                        "count": 1,
                    }
                ),
                encoding="utf-8",
            )

            geometry = {
                "ref1": {"x": 0.0, "y": 0.0, "width": 10.0, "height": 6.0},
                "match1": {"x": 1.0, "y": 1.0, "width": 9.0, "height": 6.5},
                "too-large": {"x": 2.0, "y": 2.0, "width": 40.0, "height": 28.0},
                "other-stroke": {"x": 3.0, "y": 3.0, "width": 9.5, "height": 6.2},
            }

            with (
                mock.patch.object(elements, "SELECTION_EXPORT_PATH", selection_path),
                mock.patch.object(elements, "InkscapeRunner") as runner_cls,
            ):
                runner_cls.return_value.query_all.return_value = geometry
                output = elements.cmd_find_similar_elements(Namespace(file=str(svg_path), ids=None, select=False))

        data = json.loads(output)
        self.assertEqual(data["reference_ids"], ["ref1"])
        self.assertEqual(data["matched_ids"], ["match1"])
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["missing_reference_ids"], [])


if __name__ == "__main__":
    unittest.main()
