from __future__ import annotations

import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPOSITORY_ROOT / ".github" / "workflows" / "ci.yml"


class ContinuousIntegrationWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_expected_triggers_and_read_only_permissions(self) -> None:
        for trigger in ("push:", "pull_request:", "workflow_dispatch:"):
            self.assertIn(trigger, self.workflow)
        self.assertIn("permissions:\n  contents: read", self.workflow)

    def test_python_version_installation_and_make_targets(self) -> None:
        expected_fragments = (
            'python-version: "3.12"',
            "python -m pip install -r requirements.txt",
            "run: make test",
            "run: make validate",
        )
        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.workflow)

    def test_workflow_delegates_project_checks_to_makefile(self) -> None:
        duplicated_commands = (
            "python -m unittest discover",
            "python scripts/verify_source_integrity.py",
            "python scripts/validate_final_reconstruction.py",
            "python -m pip check",
            "git diff --check",
        )
        for command in duplicated_commands:
            with self.subTest(command=command):
                self.assertNotIn(command, self.workflow)

    def test_workflow_does_not_require_external_dataset(self) -> None:
        forbidden_fragments = (
            "LENDING_CLUB_DATA_PATH",
            "prepare_dataset.py",
            "jupyter nbconvert",
            "kaggle",
            "data/raw",
        )
        for fragment in forbidden_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, self.workflow)


if __name__ == "__main__":
    unittest.main()
