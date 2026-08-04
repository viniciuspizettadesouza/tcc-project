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
        cls.phase5_index = next(
            index
            for index, cell in enumerate(cls.notebook.cells)
            if cell.source.startswith("## 9. PoC 2")
        )
        cls.code_source_before_phase5 = "\n".join(
            cell.source
            for cell in cls.notebook.cells[: cls.phase5_index]
            if cell.cell_type == "code"
        )

    def test_phase_3_titles_appear_in_thesis_order(self) -> None:
        headings = [
            "### Figura 9",
            "### Figuras 10–12",
            "### Figura 13",
            "### Figura 14",
            "### Figura 15",
            "### Figuras 16–17",
            "### Figuras 18–19",
        ]
        positions = [self.source.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("FIGURE_TITLES", self.code_source)
        self.assertEqual(list(FIGURE_TITLES), list(range(9, 20)))

    def test_phase_4_deliverables_follow_phase_3(self) -> None:
        headings = [
            "## 8. PoC 1",
            "### Tabela 7",
            "### Figura 20",
            "### Figuras 21–22",
            "### Sensibilidade",
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

    def test_phase_5_models_and_figures_follow_phase_4(self) -> None:
        headings = [
            "## 9. PoC 2",
            "### Figura 23",
            "### Redução rastreável",
            "### Figura 24",
            "### Figura 25",
            "### Comparação histórica",
        ]
        positions = [self.source.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("logistic_baseline_pipeline", self.code_source)
        self.assertIn("xgboost_full_pipeline", self.code_source)
        self.assertIn("xgboost_reduced_pipeline", self.code_source)
        self.assertIn("predict_proba", self.code_source)

    def test_phase_6_scores_offers_and_figures_follow_phase_5(self) -> None:
        headings = [
            "## 10. Score e taxa personalizada",
            "### Calibração da probabilidade de inadimplência",
            "### Scores, categorias e linhas fora da faixa",
            "### Oferta sustentada e exemplo de score 750",
            "### Figuras 26–29",
            "### Resultado e limitações do score",
        ]
        positions = [self.source.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("fit_sigmoid_calibrator", self.code_source)
        self.assertIn("probability_to_scores", self.code_source)
        self.assertIn("category_b_interest_rate(750)", self.code_source)
        for title in (
            "Figura 26 — Taxa de Juros por Categoria de Score",
            "Figura 27 — DTI por Categoria de Score",
            "Figura 28 — Tipo de Propriedade por Categoria de Score",
            "Figura 29 — Tipo de Aplicação por Categoria de Score",
        ):
            self.assertIn(title, self.code_source)

    def test_phase_7_narrative_has_all_sections_and_provenance(self) -> None:
        headings = [
            "## 1. Descrição do projeto",
            "## 2. Notas de reprodutibilidade",
            "## 3. Aquisição do dataset",
            "## 4. Imports e configuração",
            "## 5. Carregamento e populações analíticas",
            "## 6. Análise exploratória dos dados",
            "## 7. Limpeza e pré-processamento",
            "## 8. PoC 1",
            "## 9. PoC 2",
            "## 10. Score e taxa personalizada",
            "## 11. Resultados",
            "## 12. Comparação com a tese",
            "## 13. Limitações",
            "## 14. Conclusões",
            "## 15. Proveniência e notas de reconstrução",
        ]
        positions = [self.source.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        for heading in headings:
            cell = next(
                cell
                for cell in self.notebook.cells
                if cell.cell_type == "markdown" and heading in cell.source
            )
            self.assertIn("**Tipo:**", cell.source)

    def test_phase_7_preserves_definition_before_use(self) -> None:
        code_cells = [
            (index, cell.source)
            for index, cell in enumerate(self.notebook.cells)
            if cell.cell_type == "code"
        ]

        def code_index(fragment: str) -> int:
            return next(index for index, source in code_cells if fragment in source)

        self.assertLess(code_index("DATASET_PATH ="), code_index("pipeline_result ="))
        self.assertLess(
            code_index("verified_loans ="),
            code_index("prepare_supervised_data(verified_loans)"),
        )
        self.assertLess(
            code_index("xgboost_reduced_pipeline ="),
            code_index("fit_sigmoid_calibrator("),
        )

    def test_notebook_uses_configurable_relative_dataset_path(self) -> None:
        self.assertIn("DATA_PATH_ENV", self.code_source)
        self.assertIn("data/raw/Loan_status_2007-2020Q3.gzip", self.source)
        self.assertNotIn("/content/", self.source)
        self.assertNotIn("/home/", self.source)

    def test_notebook_avoids_obsolete_or_future_phase_apis(self) -> None:
        self.assertNotIn("distplot", self.code_source)
        self.assertNotIn("RandomUnderSampler", self.code_source_before_phase5)
        self.assertNotIn("XGBClassifier", self.code_source_before_phase5)
        self.assertNotIn("LogisticRegression", self.code_source_before_phase5)

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
