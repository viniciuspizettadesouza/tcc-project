"""Calibrated probabilities, explicit scores, and evidenced offers for Phase 6."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import brier_score_loss, roc_auc_score

SCORE_BINS = (175.0, 225.0, 350.0, 475.0, 600.0, 725.0, 825.0, 900.0)
THESIS_CREDIT_CATEGORIES = ("G", "F", "E", "D", "C", "B", "A")
RECOVERED_RISK_CATEGORIES = ("A", "B", "C", "D", "E", "F", "G")

BELOW_SCORE_RANGE = "Fora da faixa: abaixo de 175"
ABOVE_SCORE_RANGE = "Fora da faixa: acima de 900"

# The thesis publishes rate evidence only for its category-B example.  No
# ranges are inferred for A or C--G.
CATEGORY_B_SCORE_LIMITS = (725.0, 825.0)
CATEGORY_B_RATE_LIMITS = (13.33, 16.08)  # (minimum, maximum), percent p.a.


def fit_sigmoid_calibrator(
    fitted_estimator: Any, X_calibration: pd.DataFrame, y_calibration: pd.Series
) -> CalibratedClassifierCV:
    """Fit a sigmoid calibrator around an already fitted, frozen classifier."""

    calibrator = CalibratedClassifierCV(
        FrozenEstimator(fitted_estimator), method="sigmoid"
    )
    return calibrator.fit(X_calibration, y_calibration)


def probability_metrics(y_true: pd.Series, probability: np.ndarray) -> dict[str, float]:
    """Return discrimination and calibration metrics for positive-class PD."""

    probability = _validated_probability(probability)
    return {
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "brier_score": float(brier_score_loss(y_true, probability)),
    }


def probability_to_scores(probability_default: np.ndarray) -> pd.DataFrame:
    """Expose both score directions without silently calling risk 'credit'.

    The recovered notebook's ``PD * 1000`` is retained as ``risk_score``:
    higher means worse.  Its explicit inverse, ``(1 - PD) * 1000``, is the
    ``credit_score`` used with the thesis's G-to-A labels: higher means better.
    """

    probability = _validated_probability(probability_default)
    return pd.DataFrame(
        {
            "probability_default": probability,
            "risk_score": probability * 1_000.0,
            "credit_score": (1.0 - probability) * 1_000.0,
        }
    )


def categorize_credit_score(score: pd.Series | np.ndarray) -> pd.Series:
    """Apply thesis labels and explicitly retain scores outside 175--900."""

    values = pd.Series(score, dtype="float64")
    if not np.isfinite(values).all():
        raise ValueError("credit scores must be finite")
    categories = pd.cut(
        values,
        bins=SCORE_BINS,
        labels=THESIS_CREDIT_CATEGORIES,
        include_lowest=True,
        right=True,
    ).astype(object)
    categories.loc[values.lt(SCORE_BINS[0])] = BELOW_SCORE_RANGE
    categories.loc[values.gt(SCORE_BINS[-1])] = ABOVE_SCORE_RANGE
    return categories.rename("credit_category")


def categorize_recovered_risk_score(score: pd.Series | np.ndarray) -> pd.Series:
    """Reproduce the notebook labels, but name the underlying value as risk."""

    values = pd.Series(score, dtype="float64")
    if not np.isfinite(values).all():
        raise ValueError("risk scores must be finite")
    categories = pd.cut(
        values,
        bins=SCORE_BINS,
        labels=RECOVERED_RISK_CATEGORIES,
        include_lowest=True,
        right=True,
    ).astype(object)
    categories.loc[values.lt(SCORE_BINS[0])] = BELOW_SCORE_RANGE
    categories.loc[values.gt(SCORE_BINS[-1])] = ABOVE_SCORE_RANGE
    return categories.rename("recovered_risk_category")


def category_b_interest_rate(credit_score: float) -> float:
    """Interpolate the sole rate interval evidenced by the thesis.

    A better (higher) credit score receives a lower rate: 16.08% at 725 and
    13.33% at 825.  This direction resolves an ambiguity not stated in the PDF.
    """

    lower_score, upper_score = CATEGORY_B_SCORE_LIMITS
    minimum_rate, maximum_rate = CATEGORY_B_RATE_LIMITS
    if not np.isfinite(credit_score):
        raise ValueError("credit score must be finite")
    if not lower_score <= credit_score <= upper_score:
        raise ValueError("category-B offer requires a score from 725 through 825")
    position = (credit_score - lower_score) / (upper_score - lower_score)
    return float(maximum_rate + position * (minimum_rate - maximum_rate))


def evidenced_interest_offer(category: str, credit_score: float) -> float:
    """Return an offer only where the PDF supplies category-level evidence."""

    if category != "B":
        return float("nan")
    return category_b_interest_rate(credit_score)


def _validated_probability(probability: np.ndarray) -> np.ndarray:
    values = np.asarray(probability, dtype="float64")
    if values.ndim != 1:
        raise ValueError("probability_default must be one-dimensional")
    if not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError("probability_default must contain finite values from 0 to 1")
    return values
