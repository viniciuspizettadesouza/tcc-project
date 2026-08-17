from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from tcc_evolution.evaluation import (
    evaluate_calibrated_models,
    evaluate_probabilities,
    fit_calibrated_models,
)


class EvolutionEvaluationTests(unittest.TestCase):
    def test_probability_metrics_use_probabilities_and_threshold_half(self) -> None:
        target = pd.Series([0, 0, 1, 1])
        probability = np.array([0.1, 0.4, 0.35, 0.8])
        metrics = evaluate_probabilities(target, probability)
        self.assertEqual(
            set(metrics),
            {
                "roc_auc",
                "pr_auc",
                "brier_score",
                "precision_default",
                "recall_default",
                "f1_default",
                "prevalence_default",
                "predicted_non_default_rate",
                "diagnostic_threshold",
            },
        )
        self.assertAlmostEqual(metrics["roc_auc"], 0.75)
        self.assertAlmostEqual(metrics["recall_default"], 0.5)
        self.assertAlmostEqual(metrics["predicted_non_default_rate"], 0.75)
        self.assertEqual(metrics["diagnostic_threshold"], 0.5)

    def test_invalid_probability_contract_fails(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_probabilities(pd.Series([0, 1]), np.array([0.2, 1.1]))
        with self.assertRaises(ValueError):
            evaluate_probabilities(pd.Series([0, 0]), np.array([0.2, 0.3]))
        with self.assertRaises(ValueError):
            evaluate_probabilities(pd.Series([0, 1]), np.array([0.2]), threshold=0.5)

    def test_fit_and_evaluation_keep_calibration_separate_from_test(self) -> None:
        rows = 180
        frame = pd.DataFrame(
            {
                "fico": np.linspace(580, 800, rows),
                "annual_inc": np.log1p(np.linspace(20_000, 150_000, rows)),
            }
        )
        target = pd.Series(([0, 1, 0] * 60), dtype="int8")
        models = fit_calibrated_models(
            frame.iloc[:100],
            target.iloc[:100],
            frame.iloc[100:140],
            target.iloc[100:140],
            ("fico", "annual_inc"),
            xgboost_estimators=2,
        )
        self.assertEqual(set(models), {"logistic_regression", "xgboost"})
        for bundle in models.values():
            self.assertEqual(
                bundle.requested_feature_names, ("fico", "annual_inc")
            )
            self.assertEqual(bundle.feature_names, ("fico", "annual_inc"))
            self.assertEqual(bundle.dropped_all_missing_features, ())
            self.assertIsNot(bundle.estimator, bundle.calibrated_estimator)

        metrics, probabilities = evaluate_calibrated_models(
            models, frame.iloc[140:], target.iloc[140:]
        )
        self.assertEqual(metrics["model"].tolist(), ["logistic_regression", "xgboost"])
        self.assertEqual(set(probabilities), set(models))
        self.assertTrue(metrics["brier_score"].between(0, 1).all())
        self.assertTrue(metrics["pr_auc"].between(0, 1).all())

    def test_all_missing_training_features_are_dropped_without_test_information(self) -> None:
        frame = pd.DataFrame(
            {
                "fico": np.linspace(600, 800, 24),
                "annual_inc": [np.nan] * 18 + [10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
            }
        )
        target = pd.Series([0, 1] * 12)
        models = fit_calibrated_models(
            frame.iloc[:8],
            target.iloc[:8],
            frame.iloc[8:18],
            target.iloc[8:18],
            ("fico", "annual_inc"),
            xgboost_estimators=1,
        )
        for bundle in models.values():
            self.assertEqual(bundle.feature_names, ("fico",))
            self.assertEqual(bundle.dropped_all_missing_features, ("annual_inc",))
        metrics, _ = evaluate_calibrated_models(
            models, frame.iloc[18:], target.iloc[18:]
        )
        self.assertTrue((metrics["requested_feature_count"] == 2).all())
        self.assertTrue((metrics["feature_count"] == 1).all())
        self.assertTrue(
            (metrics["dropped_all_missing_features"] == "annual_inc").all()
        )

    def test_missing_features_fail_before_model_fitting(self) -> None:
        frame = pd.DataFrame({"fico": [600, 650, 700, 750]})
        target = pd.Series([0, 1, 0, 1])
        with self.assertRaisesRegex(ValueError, "missing scenario features"):
            fit_calibrated_models(
                frame,
                target,
                frame,
                target,
                ("fico", "annual_inc"),
                xgboost_estimators=1,
            )


if __name__ == "__main__":
    unittest.main()
