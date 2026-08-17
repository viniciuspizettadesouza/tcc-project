from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from tcc_evolution.bands import (
    apply_experimental_bands,
    band_performance,
    fit_experimental_bands,
    population_stability_index,
)


class ExperimentalBandTests(unittest.TestCase):
    def test_septiles_are_fitted_and_applied_with_frozen_edges(self) -> None:
        definition = fit_experimental_bands(np.arange(70.0), requested_bands=7)
        self.assertEqual(definition.actual_bands, 7)
        bands = apply_experimental_bands(pd.Series([-100.0, 1_000.0]), definition)
        self.assertEqual(bands.astype("string").tolist(), ["E01", "E07"])

    def test_duplicate_cuts_reduce_band_count_explicitly(self) -> None:
        definition = fit_experimental_bands([500.0] * 20, requested_bands=7)
        self.assertEqual(definition.requested_bands, 7)
        self.assertEqual(definition.actual_bands, 1)
        self.assertEqual(definition.labels, ("E01",))

    def test_performance_retains_empty_bands_and_checks_monotonicity(self) -> None:
        definition = fit_experimental_bands(np.arange(70.0), requested_bands=7)
        scores = pd.Series([1.0, 2.0, 65.0, 66.0])
        bands = apply_experimental_bands(scores, definition)
        result = band_performance(bands, pd.Series([1, 1, 0, 0]), definition)
        self.assertEqual(len(result), 7)
        self.assertEqual(int((result["rows"] == 0).sum()), 5)
        self.assertTrue(result["monotonic_overall"].all())

    def test_psi_is_finite_when_a_population_has_zero_share(self) -> None:
        definition = fit_experimental_bands(np.arange(70.0), requested_bands=7)
        calibration = apply_experimental_bands(pd.Series([1.0, 2.0]), definition)
        test = apply_experimental_bands(pd.Series([65.0, 66.0]), definition)
        result = population_stability_index(calibration, test, definition)
        self.assertTrue(np.isfinite(result["psi_component"]).all())
        self.assertTrue(np.isfinite(result["psi_total"]).all())

    def test_target_index_must_match_band_index(self) -> None:
        definition = fit_experimental_bands(np.arange(70.0), requested_bands=7)
        bands = apply_experimental_bands(pd.Series([1.0, 65.0]), definition)
        target = pd.Series([1, 0], index=[10, 11])
        with self.assertRaisesRegex(ValueError, "same index"):
            band_performance(bands, target, definition)


if __name__ == "__main__":
    unittest.main()
