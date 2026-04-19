"""Inkscape-Extension: sendet die aktuelle Auswahl an inkctl."""

import json

import inkex


class ExportSelection(inkex.EffectExtension):
    def effect(self):
        selected_ids = list(self.svg.selection.ids)
        output = {
            "file": self.document_path(),
            "selected_ids": selected_ids,
            "count": len(selected_ids),
        }
        with open("/tmp/inkscape_selection.json", "w", encoding="utf-8") as output_file:
            json.dump(output, output_file, indent=2)


if __name__ == "__main__":
    ExportSelection().run()
