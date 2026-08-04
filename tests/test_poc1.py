from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from tcc_reconstruction.poc1 import (
    CAMPAIGN_1,
    CAMPAIGN_2,
    CAMPAIGN_2_STRICT,
    eligibility_mask,
    encode_grades,
    evaluate_campaign,
    example_profiles,
    normalized_distance,
    reproduce_table_7,
    robust_component_scales,
)


class ContentRecommendationTests(unittest.TestCase):
    def test_grade_encoding_is_explicit_and_ordinal(self) -> None:
        encoded = encode_grades(pd.Series(list("ABCDEFGX") + [None]))
        self.assertEqual(encoded.iloc[:7].tolist(), list(range(1, 8)))
        self.assertTrue(encoded.iloc[7:].isna().all())

    def test_eligibility_boundaries_are_inclusive(self) -> None:
        boundary = pd.DataFrame(
            {
                "annual_inc": [30_000.0, 60_000.0],
                "all_util": [60.0, 35.0],
                "acc_open_past_24mths": [1.0, 5.0],
                "grade": ["E", "C"],
            }
        )
        self.assertTrue(eligibility_mask(boundary.iloc[[0]], CAMPAIGN_1).iloc[0])
        self.assertTrue(eligibility_mask(boundary.iloc[[1]], CAMPAIGN_2).iloc[0])

    def test_table_7_examples_are_reproduced(self) -> None:
        result = reproduce_table_7()
        np.testing.assert_allclose(
            result["campaign_1_distance"], [5.0, 30_000.010433331518]
        )
        np.testing.assert_allclose(
            result["campaign_2_distance"], [30_000.004016666397, 5.0]
        )
        self.assertEqual(result["campaign_1_qualified"].tolist(), [True, False])
        self.assertEqual(result["campaign_2_qualified"].tolist(), [False, True])

    def test_strict_35_percent_reference_exposes_table_conflict(self) -> None:
        strict = evaluate_campaign(example_profiles(), CAMPAIGN_2_STRICT)
        np.testing.assert_allclose(strict["distance"], [30_000.006933332534, 0.0])

    def test_threshold_twenty_is_inclusive_and_requires_eligibility(self) -> None:
        profiles = pd.DataFrame(
            {
                "annual_inc": [30_000.0, 30_000.0, 30_020.0, 30_020.01],
                "all_util": [40.0, 80.0, 60.0, 60.0],
                "acc_open_past_24mths": [1.0, 1.0, 1.0, 1.0],
                "grade": ["C", "C", "C", "C"],
            }
        )
        result = evaluate_campaign(profiles, CAMPAIGN_1)
        np.testing.assert_allclose(result["distance"], [20.0, 20.0, 20.0, 20.01])
        self.assertEqual(result["eligible"].tolist(), [True, False, True, True])
        self.assertEqual(result["qualified"].tolist(), [True, False, True, False])

    def test_normalized_distance_uses_non_zero_robust_scales(self) -> None:
        profiles = example_profiles()
        scales = robust_component_scales(profiles)
        self.assertTrue(scales.gt(0).all())
        distances = normalized_distance(profiles, CAMPAIGN_1, scales)
        self.assertTrue(np.isfinite(distances).all())

    def test_missing_values_never_qualify(self) -> None:
        profiles = example_profiles()
        profiles.loc[0, "all_util"] = np.nan
        result = evaluate_campaign(profiles, CAMPAIGN_1)
        self.assertFalse(result.loc[0, "eligible"])
        self.assertFalse(result.loc[0, "qualified"])
        self.assertTrue(np.isnan(result.loc[0, "distance"]))


if __name__ == "__main__":
    unittest.main()
