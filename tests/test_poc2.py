from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from tcc_reconstruction.poc2 import (
    DERIVED_FEATURE,
    MODEL_FEATURES,
    REDUCED_FEATURES,
    SOURCE_FEATURES,
    aggregate_xgboost_importance,
    build_logistic_pipeline,
    build_xgboost_pipeline,
    calculate_monthly_load,
    derive_target,
    evaluate_classifier,
    prepare_supervised_data,
    resampled_class_counts,
)


def model_fixture(rows: int = 40) -> pd.DataFrame:
    frame = pd.DataFrame(index=range(rows))
    for index, column in enumerate(SOURCE_FEATURES):
        frame[column] = np.arange(rows, dtype=float) + index + 1
    frame["loan_status"] = ["Fully Paid", "Charged Off"] * (rows // 2)
    frame["term"] = ["36 months", "60 months"] * (rows // 2)
    frame["sub_grade"] = ["A1", "C3"] * (rows // 2)
    frame["emp_length"] = ["1 year", "10+ years"] * (rows // 2)
    frame["home_ownership"] = ["RENT", "MORTGAGE"] * (rows // 2)
    frame["purpose"] = ["credit_card", "debt_consolidation"] * (rows // 2)
    frame["addr_state"] = ["CA", "NY"] * (rows // 2)
    frame["initial_list_status"] = ["f", "w"] * (rows // 2)
    frame["application_type"] = ["Individual", "Joint App"] * (rows // 2)
    frame["earliest_cr_line"] = ["Jan-2000", "Feb-2001"] * (rows // 2)
    frame["annual_inc"] = np.linspace(30_000, 100_000, rows)
    frame["installment"] = np.linspace(100, 500, rows)
    frame["open_acc"] = np.arange(rows, dtype=float)
    return frame


class Phase5FeatureTests(unittest.TestCase):
    def test_annex_count_is_reconciled_without_target_leakage(self) -> None:
        self.assertEqual(len(SOURCE_FEATURES), 42)
        self.assertEqual(len(MODEL_FEATURES), 43)
        self.assertEqual(MODEL_FEATURES[-1], DERIVED_FEATURE)
        self.assertNotIn("default", MODEL_FEATURES)

    def test_target_and_monthly_load_rules(self) -> None:
        target = derive_target(pd.Series(["Fully Paid", "Charged Off", "Default"]))
        self.assertEqual(target.tolist(), [0, 1, 1])
        burden = calculate_monthly_load(
            pd.DataFrame({"installment": [100.0, 100.0], "annual_inc": [12_000.0, 0]})
        )
        self.assertEqual(burden.tolist(), [10.0, -1.0])

    def test_deterministic_engineering_preserves_semantics(self) -> None:
        features, target = prepare_supervised_data(model_fixture())
        self.assertEqual(features.columns.tolist(), list(MODEL_FEATURES))
        self.assertEqual(target.value_counts().to_dict(), {0: 20, 1: 20})
        self.assertEqual(features["emp_length"].iloc[:2].tolist(), [1, 10])
        self.assertEqual(features["earliest_cr_line"].iloc[:2].tolist(), [2000, 2001])
        self.assertTrue(np.isfinite(features["monthly_load"]).all())

    def test_zero_income_sentinel_survives_feature_engineering(self) -> None:
        frame = model_fixture()
        frame.loc[0, "annual_inc"] = 0
        features, _ = prepare_supervised_data(frame)
        self.assertEqual(features.loc[0, "monthly_load"], -1.0)
        self.assertEqual(features.loc[0, "annual_inc"], 0.0)


class Phase5PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.X, self.y = prepare_supervised_data(model_fixture())

    def test_logistic_baseline_is_separate_and_undersamples_training(self) -> None:
        y = self.y.copy()
        y.iloc[:30] = 0
        pipeline = build_logistic_pipeline(REDUCED_FEATURES)
        pipeline.fit(self.X[list(REDUCED_FEATURES)], y)
        self.assertIn("logistic_regression", pipeline.named_steps)
        self.assertEqual(resampled_class_counts(pipeline, y), {0: 5, 1: 5})
        metrics = evaluate_classifier(pipeline, self.X[list(REDUCED_FEATURES)], y)
        self.assertIn("roc_auc_probability", metrics)

    def test_xgboost_uses_binary_objective_and_gain_importance(self) -> None:
        pipeline = build_xgboost_pipeline(MODEL_FEATURES, n_estimators=2)
        pipeline.fit(self.X, self.y)
        model = pipeline.named_steps["xgboost_classifier"]
        self.assertEqual(model.objective, "binary:logistic")
        self.assertEqual(model.importance_type, "gain")
        importance = aggregate_xgboost_importance(pipeline, MODEL_FEATURES)
        self.assertEqual(set(importance["feature"]), set(MODEL_FEATURES))
        self.assertAlmostEqual(float(importance["gain"].sum()), 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
