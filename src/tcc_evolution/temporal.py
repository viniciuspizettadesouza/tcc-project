"""Maturity-aware chronological partitions for evolved credit-risk audits."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

FINAL_LOAN_STATUSES = frozenset({"Fully Paid", "Charged Off", "Default"})


@dataclass(frozen=True)
class TemporalBacktestSpec:
    """Fixed monthly windows and term scope for one temporal audit."""

    name: str
    allowed_terms: tuple[int, ...]
    train_start: str
    train_end: str
    calibration_start: str
    calibration_end: str
    test_start: str
    test_end: str
    observation_horizon: str = "2020-09"


@dataclass(frozen=True)
class TemporalPartitions:
    """Chronological model/calibration/test data plus auditable populations."""

    spec: TemporalBacktestSpec
    X_train: pd.DataFrame
    y_train: pd.Series
    X_calibration: pd.DataFrame
    y_calibration: pd.Series
    X_test: pd.DataFrame
    y_test: pd.Series
    population_summary: pd.DataFrame
    exclusion_summary: pd.DataFrame


ALL_TERMS_MATURE_SPEC = TemporalBacktestSpec(
    name="all_terms_mature",
    allowed_terms=(36, 60),
    train_start="2008-01",
    train_end="2014-12",
    calibration_start="2015-01",
    calibration_end="2015-03",
    test_start="2015-04",
    test_end="2015-09",
)

TERM_36_SENSITIVITY_SPEC = TemporalBacktestSpec(
    name="term_36_sensitivity",
    allowed_terms=(36,),
    train_start="2008-01",
    train_end="2015-12",
    calibration_start="2016-01",
    calibration_end="2016-12",
    test_start="2017-01",
    test_end="2017-09",
)


def _month_ordinals(values: pd.Series) -> tuple[pd.Series, pd.Series]:
    dates = pd.to_datetime(values, errors="coerce")
    valid = dates.notna()
    ordinals = pd.Series(np.nan, index=values.index, dtype="float64")
    ordinals.loc[valid] = dates.loc[valid].dt.to_period("M").astype("int64")
    return ordinals, dates


def _term_months(values: pd.Series) -> pd.Series:
    extracted = values.astype("string").str.extract(r"(\d+)", expand=False)
    return pd.to_numeric(extracted, errors="coerce").astype("Float64")


def _period_ordinal(value: str) -> int:
    return pd.Period(value, freq="M").ordinal


def build_temporal_partitions(
    frame: pd.DataFrame,
    X: pd.DataFrame,
    y: pd.Series,
    spec: TemporalBacktestSpec,
) -> TemporalPartitions:
    """Build disjoint chronological partitions and exclusive exclusion counts."""

    required = {"issue_d", "term", "loan_status"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError("missing temporal columns: " + ", ".join(missing))
    if not frame.index.equals(X.index) or not frame.index.equals(y.index):
        raise ValueError("frame, X, and y must have identical ordered indexes")
    if y.isna().any() or not set(y.unique()).issubset({0, 1}):
        raise ValueError("target must contain only non-missing binary values")

    issue_ordinal, issue_dates = _month_ordinals(frame["issue_d"])
    term_months = _term_months(frame["term"])
    status = frame["loan_status"].astype("string")

    invalid_date = issue_ordinal.isna()
    invalid_term = ~invalid_date & term_months.isna()
    non_final = ~invalid_date & ~invalid_term & ~status.isin(FINAL_LOAN_STATUSES)
    term_out_of_scope = (
        ~invalid_date
        & ~invalid_term
        & ~non_final
        & ~term_months.isin(spec.allowed_terms)
    )
    base_valid = ~(
        invalid_date | invalid_term | non_final | term_out_of_scope
    )
    maturity_ordinal = issue_ordinal + term_months.astype("float64")
    not_mature = base_valid & maturity_ordinal.gt(
        _period_ordinal(spec.observation_horizon)
    )
    mature = base_valid & ~not_mature

    windows = {
        "train": (spec.train_start, spec.train_end),
        "calibration": (spec.calibration_start, spec.calibration_end),
        "test": (spec.test_start, spec.test_end),
    }
    masks: dict[str, pd.Series] = {}
    for name, (start, end) in windows.items():
        masks[name] = (
            mature
            & issue_ordinal.ge(_period_ordinal(start))
            & issue_ordinal.le(_period_ordinal(end))
        )
    selected = masks["train"] | masks["calibration"] | masks["test"]
    outside_windows = mature & ~selected

    if any((masks[left] & masks[right]).any() for left, right in (
        ("train", "calibration"),
        ("train", "test"),
        ("calibration", "test"),
    )):
        raise ValueError("temporal windows overlap")
    if not all(masks[name].any() for name in windows):
        raise ValueError("every temporal partition must contain rows")
    if any(y.loc[masks[name]].nunique() != 2 for name in windows):
        raise ValueError("every temporal partition must contain both target classes")

    exclusion_masks = {
        "invalid_issue_date": invalid_date,
        "invalid_term": invalid_term,
        "non_final_status": non_final,
        "term_out_of_scope": term_out_of_scope,
        "not_mature_by_horizon": not_mature,
        "outside_partition_windows": outside_windows,
        "selected": selected,
    }
    if sum(int(mask.sum()) for mask in exclusion_masks.values()) != len(frame):
        raise RuntimeError("temporal exclusion accounting is not exhaustive")
    exclusion_summary = pd.DataFrame(
        {
            "audit": spec.name,
            "reason": list(exclusion_masks),
            "rows": [int(mask.sum()) for mask in exclusion_masks.values()],
        }
    )

    population_rows = []
    for name, mask in masks.items():
        target = y.loc[mask]
        dates = issue_dates.loc[mask]
        population_rows.append(
            {
                "audit": spec.name,
                "partition": name,
                "rows": int(mask.sum()),
                "defaults": int(target.sum()),
                "prevalence_default": float(target.mean()),
                "issue_min": dates.min().strftime("%Y-%m"),
                "issue_max": dates.max().strftime("%Y-%m"),
                "terms": ",".join(
                    str(int(value))
                    for value in sorted(term_months.loc[mask].dropna().unique())
                ),
            }
        )
    population_summary = pd.DataFrame(population_rows)

    return TemporalPartitions(
        spec=spec,
        X_train=X.loc[masks["train"]],
        y_train=y.loc[masks["train"]],
        X_calibration=X.loc[masks["calibration"]],
        y_calibration=y.loc[masks["calibration"]],
        X_test=X.loc[masks["test"]],
        y_test=y.loc[masks["test"]],
        population_summary=population_summary,
        exclusion_summary=exclusion_summary,
    )
