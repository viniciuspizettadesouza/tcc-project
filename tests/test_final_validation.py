from __future__ import annotations

import unittest

from scripts.validate_final_reconstruction import (
    MAIN_SECTIONS,
    TABLE_SECTION_MARKERS,
    run_final_validation,
)


class FinalReconstructionValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = run_final_validation()

    def test_saved_notebook_is_complete_and_executed(self) -> None:
        notebook = self.summary["notebook"]
        self.assertEqual(notebook["main_sections"], len(MAIN_SECTIONS))
        self.assertEqual(notebook["code_cells"], notebook["executed_code_cells"])
        self.assertEqual(notebook["error_outputs"], 0)
        self.assertEqual(notebook["png_figure_outputs"], 20)
        self.assertEqual(notebook["plotly_figure_outputs"], 1)
        self.assertTrue(notebook["explicit_figure_dimensions"])
        self.assertTrue(notebook["figure_axes_labeled"])
        self.assertEqual(notebook["table_sections"], len(TABLE_SECTION_MARKERS))

    def test_no_prohibited_artifacts_are_tracked(self) -> None:
        repository = self.summary["repository"]
        self.assertEqual(repository["tracked_dataset_files"], 0)
        self.assertEqual(repository["tracked_credential_files"], 0)
        self.assertEqual(repository["tracked_model_binaries"], 0)

    def test_direct_dependencies_are_pinned(self) -> None:
        self.assertGreater(self.summary["environment"]["pinned_direct_dependencies"], 0)

    def test_all_result_comparisons_have_final_status(self) -> None:
        comparison = self.summary["result_comparison"]
        self.assertEqual(comparison["classified_items"], 30)
        self.assertEqual(comparison["pending_items"], 0)

    def test_readme_covers_local_and_colab_execution(self) -> None:
        self.assertTrue(self.summary["readme"]["local_instructions"])
        self.assertTrue(self.summary["readme"]["colab_instructions"])


if __name__ == "__main__":
    unittest.main()
