from __future__ import annotations

import unittest

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

from tcc_reconstruction.score import (
    ABOVE_SCORE_RANGE,
    BELOW_SCORE_RANGE,
    categorize_credit_score,
    categorize_recovered_risk_score,
    category_b_interest_rate,
    evidenced_interest_offer,
    fit_sigmoid_calibrator,
    probability_metrics,
    probability_to_scores,
)


class Phase6ScoreTests(unittest.TestCase):
    def test_score_directions_are_explicit_inverses(self) -> None:
        scores = probability_to_scores(np.array([0.1, 0.25, 0.9]))
        self.assertEqual(scores["risk_score"].tolist(), [100.0, 250.0, 900.0])
        np.testing.assert_allclose(scores["credit_score"], [900.0, 750.0, 100.0])
        self.assertTrue(scores["risk_score"].is_monotonic_increasing)
        self.assertTrue(scores["credit_score"].is_monotonic_decreasing)

    def test_thesis_and_recovered_category_inversion_is_explicit(self) -> None:
        boundaries = pd.Series(
            [174.99, 175, 225, 225.01, 725, 725.01, 825, 900, 900.01]
        )
        thesis = categorize_credit_score(boundaries).tolist()
        recovered = categorize_recovered_risk_score(boundaries).tolist()
        self.assertEqual(
            thesis,
            [
                BELOW_SCORE_RANGE,
                "G",
                "G",
                "F",
                "C",
                "B",
                "B",
                "A",
                ABOVE_SCORE_RANGE,
            ],
        )
        self.assertEqual(
            recovered,
            [
                BELOW_SCORE_RANGE,
                "A",
                "A",
                "B",
                "E",
                "F",
                "F",
                "G",
                ABOVE_SCORE_RANGE,
            ],
        )

    def test_score_750_is_thesis_category_b(self) -> None:
        self.assertEqual(categorize_credit_score([750]).iloc[0], "B")

    def test_invalid_probability_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            probability_to_scores(np.array([0.5, 1.01]))


class Phase6OfferTests(unittest.TestCase):
    def test_rate_boundaries_and_direction(self) -> None:
        self.assertAlmostEqual(category_b_interest_rate(725), 16.08)
        self.assertAlmostEqual(category_b_interest_rate(825), 13.33)
        self.assertGreater(category_b_interest_rate(750), category_b_interest_rate(800))

    def test_published_750_example_has_reconstructed_rate(self) -> None:
        self.assertAlmostEqual(category_b_interest_rate(750), 15.3925)

    def test_non_b_rates_are_not_invented(self) -> None:
        self.assertTrue(np.isnan(evidenced_interest_offer("D", 550)))
        with self.assertRaises(ValueError):
            evidenced_interest_offer("B", 700)


class Phase6CalibrationTests(unittest.TestCase):
    def test_frozen_estimator_calibration_and_metrics(self) -> None:
        X, y = make_classification(n_samples=120, random_state=7)
        fitted = LogisticRegression(max_iter=500, random_state=7).fit(X[:80], y[:80])
        calibrated = fit_sigmoid_calibrator(fitted, X[80:100], pd.Series(y[80:100]))
        probability = calibrated.predict_proba(X[100:])[:, 1]
        metrics = probability_metrics(pd.Series(y[100:]), probability)
        self.assertEqual(set(metrics), {"roc_auc", "brier_score"})
        self.assertTrue(((probability >= 0) & (probability <= 1)).all())


if __name__ == "__main__":
    unittest.main()
