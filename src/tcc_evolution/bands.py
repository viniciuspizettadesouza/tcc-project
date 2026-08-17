"""Calibration-only experimental score bands and stability diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ExperimentalBandDefinition:
    """Frozen score cuts learned from a calibration population only."""

    requested_bands: int
    labels: tuple[str, ...]
    edges: tuple[float, ...]
    calibration_rows: int

    @property
    def actual_bands(self) -> int:
        return len(self.labels)


def _finite_scores(values: pd.Series | np.ndarray, name: str) -> pd.Series:
    scores = pd.Series(values, dtype="float64", name=name)
    if scores.empty:
        raise ValueError(f"{name} must not be empty")
    if not np.isfinite(scores).all():
        raise ValueError(f"{name} must contain only finite values")
    return scores


def fit_experimental_bands(
    calibration_credit_score: pd.Series | np.ndarray,
    *,
    requested_bands: int = 7,
) -> ExperimentalBandDefinition:
    """Fit quantile cuts on calibration scores, dropping duplicate cuts."""

    if requested_bands < 1:
        raise ValueError("requested_bands must be at least one")
    scores = _finite_scores(calibration_credit_score, "calibration_credit_score")
    _, quantile_edges = pd.qcut(
        scores,
        q=requested_bands,
        retbins=True,
        duplicates="drop",
    )
    if len(quantile_edges) <= 1:
        application_edges = (-np.inf, np.inf)
    else:
        application_edges = (
            -np.inf,
            *tuple(float(edge) for edge in quantile_edges[1:-1]),
            np.inf,
        )
    actual_bands = len(application_edges) - 1
    labels = tuple(f"E{index:02d}" for index in range(1, actual_bands + 1))
    return ExperimentalBandDefinition(
        requested_bands=requested_bands,
        labels=labels,
        edges=tuple(application_edges),
        calibration_rows=len(scores),
    )


def apply_experimental_bands(
    credit_score: pd.Series | np.ndarray,
    definition: ExperimentalBandDefinition,
) -> pd.Series:
    """Apply frozen cuts; E01 always contains the lowest credit scores."""

    scores = _finite_scores(credit_score, "credit_score")
    bands = pd.cut(
        scores,
        bins=definition.edges,
        labels=definition.labels,
        include_lowest=True,
        right=True,
        ordered=True,
    )
    return bands.rename("experimental_band")


def _wilson_interval(
    defaults: int,
    rows: int,
    z: float = 1.959963984540054,
) -> tuple[float, float]:
    if rows == 0:
        return float("nan"), float("nan")
    rate = defaults / rows
    denominator = 1 + z**2 / rows
    centre = (rate + z**2 / (2 * rows)) / denominator
    margin = z * np.sqrt(rate * (1 - rate) / rows + z**2 / (4 * rows**2)) / denominator
    return float(centre - margin), float(centre + margin)


def band_performance(
    bands: pd.Series,
    target_default: pd.Series | np.ndarray,
    definition: ExperimentalBandDefinition,
    *,
    minimum_support: int = 30,
) -> pd.DataFrame:
    """Publish support, default rates, Wilson intervals, and monotonicity."""

    if minimum_support < 1:
        raise ValueError("minimum_support must be at least one")
    if isinstance(target_default, pd.Series) and not bands.index.equals(
        target_default.index
    ):
        raise ValueError("target_default must have the same index as bands")
    target = pd.Series(np.asarray(target_default), index=bands.index)
    if (
        len(target) != len(bands)
        or target.isna().any()
        or not set(target.unique()).issubset({0, 1})
    ):
        raise ValueError("target_default must be aligned, non-missing, and binary")
    observed = pd.DataFrame({"band": bands, "target": target})
    grouped = observed.groupby("band", observed=False)["target"].agg(["size", "sum"])
    grouped = grouped.reindex(definition.labels, fill_value=0)
    rows = []
    previous_rate: float | None = None
    monotonic_flags: list[bool] = []
    for label, values in grouped.iterrows():
        count = int(values["size"])
        defaults = int(values["sum"])
        rate = defaults / count if count else float("nan")
        lower, upper = _wilson_interval(defaults, count)
        monotonic = True if previous_rate is None or np.isnan(rate) else rate <= previous_rate
        if count:
            previous_rate = rate
        monotonic_flags.append(monotonic)
        rows.append(
            {
                "experimental_band": label,
                "rows": count,
                "population_share": count / len(bands),
                "defaults": defaults,
                "default_rate": rate,
                "default_rate_ci95_low": lower,
                "default_rate_ci95_high": upper,
                "minimum_support": minimum_support,
                "supported": count >= minimum_support,
                "monotonic_with_previous": monotonic,
            }
        )
    result = pd.DataFrame(rows)
    result["monotonic_overall"] = all(monotonic_flags)
    return result


def population_stability_index(
    calibration_bands: pd.Series,
    test_bands: pd.Series,
    definition: ExperimentalBandDefinition,
    *,
    epsilon: float = 1e-6,
) -> pd.DataFrame:
    """Calculate PSI by frozen band with finite handling for zero shares."""

    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    if calibration_bands.empty or test_bands.empty:
        raise ValueError("calibration_bands and test_bands must not be empty")
    calibration_share = calibration_bands.value_counts(normalize=True).reindex(
        definition.labels, fill_value=0.0
    )
    test_share = test_bands.value_counts(normalize=True).reindex(
        definition.labels, fill_value=0.0
    )
    calibration_safe = calibration_share.clip(lower=epsilon)
    test_safe = test_share.clip(lower=epsilon)
    component = (test_safe - calibration_safe) * np.log(test_safe / calibration_safe)
    result = pd.DataFrame(
        {
            "experimental_band": definition.labels,
            "calibration_share": calibration_share.to_numpy(),
            "test_share": test_share.to_numpy(),
            "psi_component": component.to_numpy(),
        }
    )
    result["psi_total"] = float(component.sum())
    return result
