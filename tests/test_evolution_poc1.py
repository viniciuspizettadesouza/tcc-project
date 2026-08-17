from __future__ import annotations

import unittest

import pandas as pd

from tcc_evolution.poc1 import campaign_distance_sensitivity
from tcc_reconstruction.poc1 import CAMPAIGN_1


class CampaignSensitivityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profiles = pd.DataFrame(
            {
                "annual_inc": [30_000.0, 30_010.0, 30_020.0, 30_030.0, 30_040.0],
                "all_util": [60.0] * 5,
                "acc_open_past_24mths": [1.0] * 5,
                "grade": ["C"] * 5,
            }
        )

    def test_both_distances_publish_all_percentiles_without_selection(self) -> None:
        result = campaign_distance_sensitivity(self.profiles, CAMPAIGN_1)
        percentile_rows = result[result["threshold_origin"].str.startswith("P")]
        self.assertEqual(len(percentile_rows), 10)
        self.assertEqual(set(percentile_rows["distance_kind"]), {"raw", "normalized"})
        self.assertFalse(result["automatically_selected"].any())

    def test_twenty_is_retained_only_as_historical_raw_reference(self) -> None:
        result = campaign_distance_sensitivity(self.profiles, CAMPAIGN_1)
        historical = result[result["threshold_origin"] == "historical_20"]
        self.assertEqual(len(historical), 1)
        self.assertEqual(historical.iloc[0]["distance_kind"], "raw")
        self.assertEqual(historical.iloc[0]["threshold"], 20.0)

    def test_no_eligible_profiles_fails_clearly(self) -> None:
        profiles = self.profiles.assign(annual_inc=1.0)
        with self.assertRaisesRegex(ValueError, "no eligible profiles"):
            campaign_distance_sensitivity(profiles, CAMPAIGN_1)


if __name__ == "__main__":
    unittest.main()
