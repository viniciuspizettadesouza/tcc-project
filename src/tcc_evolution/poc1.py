"""Threshold sensitivity for the historical content-based campaigns."""

from __future__ import annotations

import numpy as np
import pandas as pd

from tcc_reconstruction.poc1 import (
    DEFAULT_DISTANCE_THRESHOLD,
    Campaign,
    eligibility_mask,
    normalized_distance,
    raw_distance,
    robust_component_scales,
)

DEFAULT_SENSITIVITY_PERCENTILES = (0.10, 0.25, 0.50, 0.75, 0.90)


def campaign_distance_sensitivity(
    frame: pd.DataFrame,
    campaign: Campaign,
    *,
    percentiles: tuple[float, ...] = DEFAULT_SENSITIVITY_PERCENTILES,
) -> pd.DataFrame:
    """Evaluate percentile cuts among eligible profiles without selecting one."""

    if not percentiles or any(not 0 < value < 1 for value in percentiles):
        raise ValueError("percentiles must contain values strictly between zero and one")
    if tuple(sorted(set(percentiles))) != percentiles:
        raise ValueError("percentiles must be unique and strictly increasing")
    eligible = eligibility_mask(frame, campaign)
    eligible_frame = frame.loc[eligible]
    if eligible_frame.empty:
        raise ValueError("campaign has no eligible profiles")

    scales = robust_component_scales(eligible_frame)
    distances = {
        "raw": raw_distance(eligible_frame, campaign),
        "normalized": normalized_distance(eligible_frame, campaign, scales),
    }
    rows = []
    for distance_kind, values in distances.items():
        for percentile in percentiles:
            threshold = float(values.quantile(percentile))
            qualified = int(values.le(threshold).sum())
            rows.append(
                {
                    "campaign": campaign.name,
                    "distance_kind": distance_kind,
                    "threshold_origin": f"P{int(percentile * 100):02d}",
                    "threshold": threshold,
                    "eligible_rows": len(eligible_frame),
                    "qualified_rows": qualified,
                    "qualified_share": qualified / len(eligible_frame),
                    "automatically_selected": False,
                }
            )
    historical_qualified = int(distances["raw"].le(DEFAULT_DISTANCE_THRESHOLD).sum())
    rows.append(
        {
            "campaign": campaign.name,
            "distance_kind": "raw",
            "threshold_origin": "historical_20",
            "threshold": DEFAULT_DISTANCE_THRESHOLD,
            "eligible_rows": len(eligible_frame),
            "qualified_rows": historical_qualified,
            "qualified_share": historical_qualified / len(eligible_frame),
            "automatically_selected": False,
        }
    )
    return pd.DataFrame(rows)
