from __future__ import annotations

import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MAKEFILE_PATH = REPOSITORY_ROOT / "Makefile"
GITIGNORE_PATH = REPOSITORY_ROOT / ".gitignore"


class StandardProjectCommandsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    def test_required_targets_are_defined(self) -> None:
        for target in (
            "install",
            "test",
            "validate",
            "validate-html",
            "notebook",
            "notebook-evolved",
            "reproduce-reconstructed",
            "export",
            "export-evolved",
            "export-reconstructed",
        ):
            with self.subTest(target=target):
                self.assertIn(f"\n{target}:\n", self.makefile)

    def test_install_test_and_validation_commands_are_explicit(self) -> None:
        required_commands = (
            "-m pip install -r requirements.txt",
            "-m unittest discover -s tests -v",
            "scripts/verify_source_integrity.py",
            "scripts/validate_final_reconstruction.py",
            "scripts.validate_evolved_notebook",
            "-m pip check",
            "git diff --check",
        )
        for command in required_commands:
            with self.subTest(command=command):
                self.assertIn(command, self.makefile)

    def test_notebook_requires_dataset_and_starts_fresh_kernel(self) -> None:
        environment_guard = 'test -n "$$LENDING_CLUB_DATA_PATH"'
        file_guard = 'test -f "$$LENDING_CLUB_DATA_PATH"'
        execution_command = "-m jupyter nbconvert"
        self.assertLess(
            self.makefile.index(environment_guard),
            self.makefile.index(execution_command),
        )
        self.assertLess(
            self.makefile.index(file_guard),
            self.makefile.index(execution_command),
        )
        self.assertIn("--execute", self.makefile)
        self.assertIn("--inplace", self.makefile)
        self.assertIn('--inplace "$(EVOLVED_NOTEBOOK)"', self.makefile)
        self.assertNotIn('--inplace "$(HISTORICAL_NOTEBOOK)"', self.makefile)

    def test_historical_reproduction_uses_disposable_script(self) -> None:
        self.assertIn("scripts.reproduce_historical_notebook", self.makefile)
        self.assertNotIn(
            '--execute --inplace "$(HISTORICAL_NOTEBOOK)"', self.makefile
        )

    def test_export_is_local_and_ignored(self) -> None:
        self.assertIn("EXPORT_DIR := artifacts/html", self.makefile)
        self.assertIn("scripts/export_notebook_html.py", self.makefile)
        self.assertIn('--output "$(EVOLVED_HTML_EXPORT)"', self.makefile)
        self.assertIn('--output "$(HISTORICAL_HTML_EXPORT)"', self.makefile)
        gitignore = GITIGNORE_PATH.read_text(encoding="utf-8")
        self.assertIn("artifacts/", gitignore)

    def test_targets_have_no_implicit_download_or_repository_publication(self) -> None:
        forbidden_fragments = (
            "kaggle ",
            "curl ",
            "wget ",
            "git commit",
            "git push",
            "git tag",
            "gh release",
        )
        for fragment in forbidden_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, self.makefile)


if __name__ == "__main__":
    unittest.main()
