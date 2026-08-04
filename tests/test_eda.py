from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from tcc_reconstruction.eda import (
    FIGURE_TITLES,
    add_log1p_columns,
    aggregate_column_profile,
    calculate_pearson_correlations,
    deterministic_plot_sample,
    select_defaulted_loans,
)


class ExploratoryAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = pd.DataFrame(
            {
                "id": ["a", "b", "c", "d"],
                "loan_status": [
                    "Fully Paid",
                    "Charged Off",
                    "Default",
                    "Fully Paid",
                ],
                "loan_amnt": [1.0, 2.0, 3.0, 4.0],
                "funded_amnt": [2.0, 4.0, 6.0, 8.0],
                "fico_range_low": [600.0, 650.0, 700.0, np.nan],
                "fico_range_high": [604.0, 654.0, 704.0, np.nan],
                "total_acc": [2.0, 4.0, 6.0, 8.0],
                "open_acc": [1.0, 2.0, 3.0, 4.0],
                "annual_inc": [0.0, 9.0, 99.0, 999.0],
            }
        )

    def test_titles_cover_figures_9_through_19_in_order(self) -> None:
        self.assertEqual(list(FIGURE_TITLES), list(range(9, 20)))

    def test_correlations_are_calculated_from_valid_pairs(self) -> None:
        result = calculate_pearson_correlations(self.frame)
        self.assertEqual(result["n_pares_validos"].tolist(), [4, 3, 4])
        np.testing.assert_allclose(result["correlacao_pearson"], [1.0, 1.0, 1.0])

    def test_default_population_excludes_fully_paid_loans(self) -> None:
        result = select_defaulted_loans(self.frame)
        self.assertEqual(result["id"].tolist(), ["b", "c"])

    def test_plot_sample_is_stable_and_bounded(self) -> None:
        first = deterministic_plot_sample(self.frame, sample_size=2, seed=7)
        second = deterministic_plot_sample(self.frame, sample_size=2, seed=7)
        self.assertEqual(first["id"].tolist(), second["id"].tolist())
        self.assertEqual(len(first), 2)
        with self.assertRaisesRegex(ValueError, "positive"):
            deterministic_plot_sample(self.frame, sample_size=0)

    def test_log1p_is_non_destructive_and_rejects_negative_values(self) -> None:
        result = add_log1p_columns(self.frame)
        np.testing.assert_allclose(
            result["annual_inc_log1p"], np.log1p(self.frame["annual_inc"])
        )
        np.testing.assert_allclose(
            result["open_acc_log1p"], np.log1p(self.frame["open_acc"])
        )
        self.assertNotIn("annual_inc_log1p", self.frame)

        invalid = self.frame.copy()
        invalid.loc[0, "annual_inc"] = -1
        with self.assertRaisesRegex(ValueError, "annual_inc"):
            add_log1p_columns(invalid)

    def test_aggregate_profile_contains_no_record_identifiers(self) -> None:
        result = aggregate_column_profile(self.frame, ["annual_inc", "open_acc"])
        self.assertEqual(result["coluna"].tolist(), ["annual_inc", "open_acc"])
        self.assertEqual(result.loc[0, "mediana"], 54.0)
        self.assertNotIn("id", result.columns)


if __name__ == "__main__":
    unittest.main()
