"""Content-based recommendation experiment reconstructed for Phase 4.

The recovered notebook contains no PoC 1 implementation.  This module follows
the thesis criteria and separately preserves the distance convention inferred
from its published example table.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

POC1_COLUMNS = ("annual_inc", "all_util", "acc_open_past_24mths", "grade")
DEFAULT_DISTANCE_THRESHOLD = 20.0
GRADE_TO_NUMBER = {grade: index for index, grade in enumerate("ABCDEFG", start=1)}


@dataclass(frozen=True)
class Campaign:
    """Eligibility rules and reference point for one credit campaign."""

    name: str
    minimum_annual_income: float
    maximum_utilization: float
    minimum_recent_accounts: float
    minimum_grade: str
    maximum_grade: str
    distance_utilization_reference: float

    def with_utilization_reference(self, value: float) -> Campaign:
        return replace(self, distance_utilization_reference=value)


CAMPAIGN_1 = Campaign(
    name="Campanha 1",
    minimum_annual_income=30_000.0,
    maximum_utilization=60.0,
    minimum_recent_accounts=1.0,
    minimum_grade="B",
    maximum_grade="E",
    distance_utilization_reference=60.0,
)

# The eligibility limit remains 35%, exactly as stated in the thesis.  A 40%
# distance reference is retained separately because it is the only value that
# reproduces both Campaign 2 distances printed in Table 7.
CAMPAIGN_2 = Campaign(
    name="Campanha 2",
    minimum_annual_income=60_000.0,
    maximum_utilization=35.0,
    minimum_recent_accounts=5.0,
    minimum_grade="A",
    maximum_grade="C",
    distance_utilization_reference=40.0,
)
CAMPAIGN_2_STRICT = CAMPAIGN_2.with_utilization_reference(35.0)


def _numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").astype("float64")


def encode_grades(series: pd.Series) -> pd.Series:
    """Encode Lending Club grades ordinally as A=1 through G=7."""

    normalized = series.astype("string").str.strip().str.upper()
    return normalized.map(GRADE_TO_NUMBER).astype("Float64")


def _components(frame: pd.DataFrame, campaign: Campaign) -> pd.DataFrame:
    missing = sorted(set(POC1_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError("missing PoC 1 columns: " + ", ".join(missing))

    annual_income = _numeric(frame["annual_inc"])
    utilization = _numeric(frame["all_util"])
    recent_accounts = _numeric(frame["acc_open_past_24mths"])
    grade = encode_grades(frame["grade"]).astype("float64")
    minimum_grade = GRADE_TO_NUMBER[campaign.minimum_grade]
    maximum_grade = GRADE_TO_NUMBER[campaign.maximum_grade]

    return pd.DataFrame(
        {
            # The published Elder/Campaign 1 distance proves that income above
            # the minimum is still measured against the boundary, not clipped.
            "annual_inc": annual_income - campaign.minimum_annual_income,
            "all_util": utilization - campaign.distance_utilization_reference,
            # Excess recent accounts satisfy the minimum and add no distance.
            "acc_open_past_24mths": (
                campaign.minimum_recent_accounts - recent_accounts
            ).clip(lower=0),
            # Grades within the accepted interval add no distance.
            "grade": np.maximum(
                minimum_grade - grade,
                np.maximum(grade - maximum_grade, 0),
            ),
        },
        index=frame.index,
    )


def eligibility_mask(frame: pd.DataFrame, campaign: Campaign) -> pd.Series:
    """Apply every thesis boundary inclusively (>= minima and <= maxima)."""

    annual_income = _numeric(frame["annual_inc"])
    utilization = _numeric(frame["all_util"])
    recent_accounts = _numeric(frame["acc_open_past_24mths"])
    grade = encode_grades(frame["grade"])
    minimum_grade = GRADE_TO_NUMBER[campaign.minimum_grade]
    maximum_grade = GRADE_TO_NUMBER[campaign.maximum_grade]

    complete = frame[list(POC1_COLUMNS)].notna().all(axis=1) & grade.notna()
    return (
        complete
        & annual_income.ge(campaign.minimum_annual_income)
        & utilization.le(campaign.maximum_utilization)
        & recent_accounts.ge(campaign.minimum_recent_accounts)
        & grade.between(minimum_grade, maximum_grade, inclusive="both")
    )


def raw_distance(frame: pd.DataFrame, campaign: Campaign) -> pd.Series:
    """Calculate the unscaled Euclidean distance evidenced by Table 7."""

    components = _components(frame, campaign)
    return np.sqrt(components.pow(2).sum(axis=1, min_count=len(POC1_COLUMNS)))


def robust_component_scales(frame: pd.DataFrame) -> pd.Series:
    """Estimate non-zero IQR scales for a normalized sensitivity analysis."""

    values = pd.DataFrame(
        {
            "annual_inc": _numeric(frame["annual_inc"]),
            "all_util": _numeric(frame["all_util"]),
            "acc_open_past_24mths": _numeric(frame["acc_open_past_24mths"]),
            "grade": encode_grades(frame["grade"]).astype("float64"),
        }
    )
    scales = values.quantile(0.75) - values.quantile(0.25)
    return scales.mask(scales.le(0) | scales.isna(), 1.0)


def normalized_distance(
    frame: pd.DataFrame, campaign: Campaign, scales: pd.Series
) -> pd.Series:
    """Calculate an IQR-normalized Euclidean distance as an adaptation."""

    missing_scales = sorted(set(POC1_COLUMNS) - set(scales.index))
    if missing_scales:
        raise ValueError("missing normalization scales: " + ", ".join(missing_scales))
    components = _components(frame, campaign)
    normalized = components.div(scales[list(POC1_COLUMNS)], axis="columns")
    return np.sqrt(normalized.pow(2).sum(axis=1, min_count=len(POC1_COLUMNS)))


def evaluate_campaign(
    frame: pd.DataFrame,
    campaign: Campaign,
    *,
    threshold: float = DEFAULT_DISTANCE_THRESHOLD,
    scales: pd.Series | None = None,
) -> pd.DataFrame:
    """Return eligibility, distance, and inclusive-threshold qualification."""

    if threshold < 0:
        raise ValueError("threshold must be non-negative")
    distance = (
        raw_distance(frame, campaign)
        if scales is None
        else normalized_distance(frame, campaign, scales)
    )
    eligible = eligibility_mask(frame, campaign)
    qualified = eligible & distance.le(threshold)
    return pd.DataFrame(
        {
            "eligible": eligible,
            "distance": distance,
            "qualified": qualified,
        },
        index=frame.index,
    )


def example_profiles() -> pd.DataFrame:
    """Return the two synthetic profiles published in Table 7."""

    return pd.DataFrame(
        {
            "user_id": ["Vinicius", "Elder"],
            "annual_inc": [30_000.0, 60_000.0],
            "all_util": [55.0, 35.0],
            "acc_open_past_24mths": [1.0, 5.0],
            "grade": ["C", "A"],
        }
    )


def reproduce_table_7() -> pd.DataFrame:
    """Reproduce Table 7 using the distance convention implied by its values."""

    profiles = example_profiles()
    campaign_1 = evaluate_campaign(profiles, CAMPAIGN_1)
    campaign_2 = evaluate_campaign(profiles, CAMPAIGN_2)
    result = profiles.copy()
    result["campaign_1_distance"] = campaign_1["distance"]
    result["campaign_1_qualified"] = campaign_1["qualified"]
    result["campaign_2_distance"] = campaign_2["distance"]
    result["campaign_2_qualified"] = campaign_2["qualified"]
    return result
