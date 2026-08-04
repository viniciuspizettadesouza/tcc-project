from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_local_html import (
    DEFAULT_HTML_PATH,
    LocalHtmlValidationError,
    is_ignored,
    validate_html,
)


class LocalHtmlValidationTests(unittest.TestCase):
    def write_html(self, directory: str, content: str) -> Path:
        path = Path(directory) / "notebook.html"
        path.write_text(content, encoding="utf-8")
        return path

    def test_safe_html_content_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_html(
                directory,
                "<html><body><table><th>feature</th><td>fico</td></table></body></html>",
            )
            summary = validate_html(path, require_ignored=False)
        self.assertEqual(summary["absolute_paths_found"], 0)
        self.assertEqual(summary["record_identifier_tables_found"], 0)
        self.assertEqual(len(summary["sha256"]), 64)

    def test_absolute_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_html(directory, "<p>/home/user/private/data.csv</p>")
            with self.assertRaisesRegex(LocalHtmlValidationError, "absolute path"):
                validate_html(path, require_ignored=False)

    def test_record_identifier_tables_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_html(directory, "<table><th>id</th><td>123</td></table>")
            with self.assertRaisesRegex(LocalHtmlValidationError, "record-level"):
                validate_html(path, require_ignored=False)

    def test_known_borrower_identifier_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_html(directory, "<p>Borrower 1077501</p>")
            with self.assertRaisesRegex(LocalHtmlValidationError, "borrower"):
                validate_html(path, require_ignored=False)

    def test_default_generated_path_is_ignored(self) -> None:
        self.assertTrue(is_ignored(DEFAULT_HTML_PATH))


if __name__ == "__main__":
    unittest.main()
