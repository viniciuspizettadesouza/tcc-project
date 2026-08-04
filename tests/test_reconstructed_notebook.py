from __future__ import annotations

import unittest
from pathlib import Path

import nbformat

from tcc_reconstruction.eda import FIGURE_TITLES

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = REPOSITORY_ROOT / "notebooks" / "tcc-reconstructed.ipynb"


class ReconstructedNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
        nbformat.validate(cls.notebook)
        cls.source = "\n".join(cell.source for cell in cls.notebook.cells)
        cls.code_source = "\n".join(
            cell.source for cell in cls.notebook.cells if cell.cell_type == "code"
        )

    def test_phase_3_titles_appear_in_thesis_order(self) -> None:
        headings = [
            "## Figura 9",
            "## Figuras 10–12",
            "## Figura 13",
            "## Figura 14",
            "## Figura 15",
            "## Figuras 16–17",
            "## Figuras 18–19",
        ]
        positions = [self.source.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("FIGURE_TITLES", self.code_source)
        self.assertEqual(list(FIGURE_TITLES), list(range(9, 20)))

    def test_phase_4_deliverables_follow_phase_3(self) -> None:
        headings = [
            "# Fase 4 — PoC 1",
            "## Tabela 7",
            "## Figura 20",
            "## Figuras 21–22",
            "## Sensibilidade",
        ]
        positions = [self.source.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertGreater(positions[0], self.source.index("## Resultados observados"))
        for title in (
            "Total de Aprovados em Cada Campanha",
            "Pontuação da Campanha 1 (Distância)",
            "Pontuação da Campanha 2 (Distância)",
        ):
            self.assertIn(title, self.code_source)

    def test_notebook_uses_configurable_relative_dataset_path(self) -> None:
        self.assertIn("DATA_PATH_ENV", self.code_source)
        self.assertIn("data/raw/Loan_status_2007-2020Q3.gzip", self.source)
        self.assertNotIn("/content/", self.source)
        self.assertNotIn("/home/", self.source)

    def test_notebook_avoids_obsolete_or_future_phase_apis(self) -> None:
        self.assertNotIn("distplot", self.code_source)
        self.assertNotIn("RandomUnderSampler", self.code_source)
        self.assertNotIn("XGBClassifier", self.code_source)
        self.assertNotIn("LogisticRegression", self.code_source)

    def test_saved_execution_has_no_errors(self) -> None:
        code_cells = [cell for cell in self.notebook.cells if cell.cell_type == "code"]
        self.assertTrue(all(cell.execution_count is not None for cell in code_cells))
        errors = [
            output
            for cell in code_cells
            for output in cell.outputs
            if output.output_type == "error"
        ]
        self.assertEqual(errors, [])

    def test_outputs_do_not_contain_borrower_ids(self) -> None:
        for cell in self.notebook.cells:
            for output in cell.get("outputs", []):
                text = output.get("data", {}).get("text/plain", "")
                self.assertNotIn("1077501", text)


if __name__ == "__main__":
    unittest.main()
