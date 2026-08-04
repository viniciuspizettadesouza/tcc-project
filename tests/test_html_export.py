from __future__ import annotations

import unittest

import nbformat

from scripts.export_notebook_html import PLOTLY_MIME_TYPE, add_plotly_html


class NotebookHtmlExportTests(unittest.TestCase):
    def test_plotly_output_receives_offline_html_representation(self) -> None:
        output = nbformat.v4.new_output(
            "display_data",
            data={
                PLOTLY_MIME_TYPE: {
                    "data": [{"type": "bar", "x": ["A"], "y": [1]}],
                    "layout": {"title": {"text": "Example"}},
                    "config": {"responsive": True},
                }
            },
        )
        notebook = nbformat.v4.new_notebook(
            cells=[nbformat.v4.new_code_cell(outputs=[output])]
        )

        self.assertEqual(add_plotly_html(notebook), 1)
        html = output["data"]["text/html"]
        self.assertIn("Plotly.newPlot", html)
        self.assertIn("plotly.js", html)

    def test_existing_html_representation_is_preserved(self) -> None:
        output = nbformat.v4.new_output(
            "display_data",
            data={PLOTLY_MIME_TYPE: {"data": []}, "text/html": "<p>saved</p>"},
        )
        notebook = nbformat.v4.new_notebook(
            cells=[nbformat.v4.new_code_cell(outputs=[output])]
        )

        self.assertEqual(add_plotly_html(notebook), 0)
        self.assertEqual(output["data"]["text/html"], "<p>saved</p>")


if __name__ == "__main__":
    unittest.main()
