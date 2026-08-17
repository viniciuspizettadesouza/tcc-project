from __future__ import annotations

import unittest
from pathlib import Path

import nbformat


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = REPOSITORY_ROOT / "notebooks" / "tcc-evolved.ipynb"


class EvolvedNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
        nbformat.validate(cls.notebook)
        cls.source = "\n".join(cell.source for cell in cls.notebook.cells)
        cls.code_source = "\n".join(
            cell.source for cell in cls.notebook.cells if cell.cell_type == "code"
        )

    def test_e1_scope_follows_the_immutable_reconstruction_narrative(self) -> None:
        self.assertLess(
            self.source.index("## 15. Proveniência e notas de reconstrução"),
            self.source.index(
                "## 16. Fase E1 — escopo metodológico e momentos de inferência"
            ),
        )
        self.assertIn("**Tipo:** extensão nova de 2026", self.source)
        self.assertIn("target permanece **inadimplência**", self.source)
        self.assertIn("não significa que o modelo aprendeu aderência", self.source)

    def test_e1_publishes_all_three_feature_contracts(self) -> None:
        for symbol in (
            "HISTORICAL_FEATURES",
            "APPLICATION_FEATURES",
            "PROFILE_FEATURES",
            "feature_availability_table",
        ):
            self.assertIn(symbol, self.code_source)
        self.assertIn("Esta fase não treina modelos novos", self.source)

    def test_evolution_metadata_records_completed_phases(self) -> None:
        self.assertEqual(
            self.notebook.metadata.tcc_evolution.completed_phases,
            ["E0", "E1", "E2", "E3", "E4", "E5"],
        )

    def test_e2_models_follow_scope_and_keep_test_out_of_fitting(self) -> None:
        self.assertLess(
            self.source.index(
                "## 16. Fase E1 — escopo metodológico e momentos de inferência"
            ),
            self.source.index(
                "## 17. Fase E2 — modelos pré-oferta e métricas ampliadas"
            ),
        )
        self.assertIn("fit_calibrated_models(", self.code_source)
        self.assertIn("evaluate_calibrated_models(", self.code_source)
        fitting_call = self.code_source.split("fit_calibrated_models(", 1)[1].split(
            ")", 1
        )[0]
        self.assertNotIn("X_test_phase5", fitting_call)
        self.assertIn("Nenhum modelo é declarado vencedor", self.source)

    def test_e2_saved_output_contains_all_scenarios_and_probability_metrics(self) -> None:
        e2_cell = next(
            cell
            for cell in self.notebook.cells
            if cell.cell_type == "code" and "model_comparison_e2" in cell.source
        )
        output_text = "\n".join(
            output.get("data", {}).get("text/plain", "")
            for output in e2_cell.get("outputs", [])
        )
        for fragment in (
            "referência histórica",
            "solicitação conhecida",
            "perfil puro",
            "roc_auc",
            "pr_auc",
            "brier_score",
            "recall_default",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, output_text)

    def test_e3_is_chronological_mature_and_follows_e2(self) -> None:
        self.assertLess(
            self.source.index(
                "## 17. Fase E2 — modelos pré-oferta e métricas ampliadas"
            ),
            self.source.index("## 18. Fase E3 — validação temporal com maturidade"),
        )
        for fragment in (
            "ALL_TERMS_MATURE_SPEC",
            "TERM_36_SENSITIVITY_SPEC",
            "build_temporal_partitions(",
            "random_vs_temporal_e3",
            "issue_d + term ≤ 2020-09",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.source)
        self.assertIn(
            "nenhum resultado temporal é usado para retreinamento", self.source
        )

    def test_e3_saved_outputs_are_clean_and_auditable(self) -> None:
        e3_cell = next(
            cell
            for cell in self.notebook.cells
            if cell.cell_type == "code" and "temporal_model_comparison_e3" in cell.source
        )
        self.assertEqual(
            [output.output_type for output in e3_cell.outputs],
            ["display_data"] * 4,
        )
        output_text = "\n".join(
            output.get("data", {}).get("text/plain", "")
            for output in e3_cell.outputs
        )
        for fragment in (
            "all_terms_mature",
            "term_36_sensitivity",
            "not_mature_by_horizon",
            "requested_feature_count",
            "dropped_all_missing_features",
            "roc_auc_delta_vs_random",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, output_text)

    def test_e4_fits_internal_bands_only_on_calibration(self) -> None:
        self.assertLess(
            self.source.index("## 18. Fase E3 — validação temporal com maturidade"),
            self.source.index(
                "## 19. Fase E4 — bandas experimentais e sensibilidade da PoC 1"
            ),
        )
        for fragment in (
            "fit_experimental_bands(",
            "calibration_credit_score_e4",
            "population_stability_index(",
            "external_equivalence",
            "campaign_distance_sensitivity(poc1_data, CAMPAIGN_1)",
            "Nenhum percentil é recomendado automaticamente",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.source)
        fitting_call = self.code_source.split("fit_experimental_bands(", 1)[1].split(
            ")", 1
        )[0]
        self.assertNotIn("test_credit_score_e4", fitting_call)

    def test_e4_saved_outputs_cover_bands_stability_and_poc1(self) -> None:
        e4_cell = next(
            cell
            for cell in self.notebook.cells
            if cell.cell_type == "code" and "band_summary_e4" in cell.source
        )
        self.assertEqual(
            [output.output_type for output in e4_cell.outputs],
            ["display_data"] * 5,
        )
        output_text = "\n".join(
            output.get("data", {}).get("text/plain", "")
            for output in e4_cell.outputs
        )
        for fragment in (
            "requested_bands",
            "actual_bands",
            "default_rate_ci95_low",
            "monotonic_overall",
            "psi_total",
            "historical_category",
            "historical_20",
            "normalized",
            "automatically_selected",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, output_text)

    def test_e5_consolidates_without_adding_an_unexecuted_code_cell(self) -> None:
        self.assertLess(
            self.source.index(
                "## 19. Fase E4 — bandas experimentais e sensibilidade da PoC 1"
            ),
            self.source.index("## 20. Fase E5 — consolidação e validação evolutiva"),
        )
        for fragment in (
            "docs/evolution-scope.md",
            "docs/evolution-results.md",
            "docs/evolution-history.md",
            "docs/result-comparison.md` permanece dedicado exclusivamente",
            "43/43 células de código",
            "ponto de entrada para pesquisas futuras",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.source)
        self.assertEqual(
            [cell.execution_count for cell in self.notebook.cells if cell.cell_type == "code"],
            list(range(1, 44)),
        )


if __name__ == "__main__":
    unittest.main()
