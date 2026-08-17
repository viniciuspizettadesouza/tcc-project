from __future__ import annotations

import unittest
from pathlib import Path

from tcc_evolution.features import (
    APPLICATION_FEATURES,
    APPLICATION_INPUT_FEATURES,
    HISTORICAL_FEATURES,
    POST_DECISION_FEATURES,
    PROFILE_FEATURES,
    TARGET_NAME,
    AvailabilityStage,
    availability_stage,
    feature_availability_records,
    feature_availability_table,
)


class EvolutionFeatureContractTests(unittest.TestCase):
    def test_scenario_counts_and_historical_order_are_stable(self) -> None:
        self.assertEqual(len(HISTORICAL_FEATURES), 43)
        self.assertEqual(len(APPLICATION_FEATURES), 38)
        self.assertEqual(len(PROFILE_FEATURES), 34)
        self.assertEqual(
            APPLICATION_FEATURES,
            tuple(f for f in HISTORICAL_FEATURES if f not in POST_DECISION_FEATURES),
        )
        self.assertEqual(
            PROFILE_FEATURES,
            tuple(f for f in APPLICATION_FEATURES if f not in APPLICATION_INPUT_FEATURES),
        )

    def test_target_and_post_decision_features_are_excluded(self) -> None:
        for features in (HISTORICAL_FEATURES, APPLICATION_FEATURES, PROFILE_FEATURES):
            self.assertNotIn(TARGET_NAME, features)
        self.assertTrue(POST_DECISION_FEATURES.isdisjoint(APPLICATION_FEATURES))
        self.assertTrue(POST_DECISION_FEATURES.isdisjoint(PROFILE_FEATURES))
        self.assertTrue(APPLICATION_INPUT_FEATURES.isdisjoint(PROFILE_FEATURES))

    def test_availability_stages_are_explicit(self) -> None:
        self.assertEqual(availability_stage("fico"), AvailabilityStage.PROFILE)
        self.assertEqual(availability_stage("loan_amnt"), AvailabilityStage.APPLICATION)
        self.assertEqual(availability_stage("int_rate"), AvailabilityStage.POST_DECISION)
        with self.assertRaisesRegex(ValueError, "unknown historical feature"):
            availability_stage("default")

    def test_every_historical_feature_has_one_governance_record(self) -> None:
        records = feature_availability_records()
        table = feature_availability_table()
        self.assertEqual(tuple(record.feature for record in records), HISTORICAL_FEATURES)
        self.assertEqual(table["feature"].tolist(), list(HISTORICAL_FEATURES))
        self.assertEqual(len(table), 43)
        self.assertTrue(table["rationale"].str.len().gt(0).all())
        self.assertEqual(int(table["application_known"].sum()), 38)
        self.assertEqual(int(table["profile_only"].sum()), 34)

    def test_scope_document_summarizes_the_executable_governance_contract(self) -> None:
        root = Path(__file__).resolve().parents[1]
        scope = (root / "docs" / "evolution-scope.md").read_text(encoding="utf-8")
        self.assertIn("43 atributos", scope)
        self.assertIn("38 na solicitação conhecida", scope)
        self.assertIn("34 no perfil puro", scope)
        self.assertIn("feature_availability_table()", scope)
        for feature in (
            "int_rate",
            "installment",
            "sub_grade",
            "initial_list_status",
            "monthly_load",
            "loan_amnt",
            "term",
            "purpose",
            "application_type",
        ):
            with self.subTest(feature=feature):
                self.assertIn(f"`{feature}`", scope)


if __name__ == "__main__":
    unittest.main()
