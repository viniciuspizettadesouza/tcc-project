"""Leakage-safe fitting and expanded probability metrics for evolved models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from tcc_reconstruction.poc2 import (
    PHASE5_RANDOM_SEED,
    build_logistic_pipeline,
    build_xgboost_pipeline,
)
from tcc_reconstruction.score import fit_sigmoid_calibrator


@dataclass(frozen=True)
class CalibratedModel:
    """One fitted classifier and its calibration-only wrapper."""

    name: str
    requested_feature_names: tuple[str, ...]
    feature_names: tuple[str, ...]
    dropped_all_missing_features: tuple[str, ...]
    estimator: Any
    calibrated_estimator: Any


def evaluate_probabilities(
    y_true: pd.Series | np.ndarray,
    probability_default: np.ndarray,
    *,
    threshold: float = 0.5,
) -> dict[str, float]:
    """Evaluate discrimination, calibration, and diagnostic threshold metrics."""

    target = np.asarray(y_true)
    probability = np.asarray(probability_default, dtype="float64")
    if target.ndim != 1 or probability.ndim != 1:
        raise ValueError("target and probability must be one-dimensional")
    if len(target) != len(probability) or not len(target):
        raise ValueError("target and probability must have equal non-zero length")
    if set(np.unique(target)) != {0, 1}:
        raise ValueError("target must contain both binary classes 0 and 1")
    if not np.isfinite(probability).all() or (
        (probability < 0) | (probability > 1)
    ).any():
        raise ValueError("probability must contain finite values from 0 to 1")
    if not 0 < threshold < 1:
        raise ValueError("threshold must be strictly between 0 and 1")

    prediction = probability >= threshold
    return {
        "roc_auc": float(roc_auc_score(target, probability)),
        "pr_auc": float(average_precision_score(target, probability)),
        "brier_score": float(brier_score_loss(target, probability)),
        "precision_default": float(
            precision_score(target, prediction, zero_division=0)
        ),
        "recall_default": float(recall_score(target, prediction, zero_division=0)),
        "f1_default": float(f1_score(target, prediction, zero_division=0)),
        "prevalence_default": float(target.mean()),
        "predicted_non_default_rate": float((~prediction).mean()),
        "diagnostic_threshold": float(threshold),
    }


def fit_calibrated_models(
    X_model_train: pd.DataFrame,
    y_model_train: pd.Series,
    X_calibration: pd.DataFrame,
    y_calibration: pd.Series,
    feature_names: tuple[str, ...],
    *,
    random_seed: int = PHASE5_RANDOM_SEED,
    xgboost_estimators: int = 200,
) -> dict[str, CalibratedModel]:
    """Fit logistic/XGBoost models, then calibrate only on the supplied holdout."""

    requested_features = tuple(feature_names)
    if not requested_features:
        raise ValueError("feature_names must not be empty")
    missing_train = sorted(set(requested_features) - set(X_model_train.columns))
    missing_calibration = sorted(
        set(requested_features) - set(X_calibration.columns)
    )
    if missing_train or missing_calibration:
        raise ValueError(
            "missing scenario features; "
            f"train={missing_train}, calibration={missing_calibration}"
        )
    dropped_all_missing = tuple(
        feature
        for feature in requested_features
        if not X_model_train[feature].notna().any()
    )
    features = tuple(
        feature
        for feature in requested_features
        if feature not in dropped_all_missing
    )
    if not features:
        raise ValueError("all requested features are missing in model training")

    builders = {
        "logistic_regression": lambda: build_logistic_pipeline(
            features, random_seed=random_seed
        ),
        "xgboost": lambda: build_xgboost_pipeline(
            features,
            random_seed=random_seed,
            n_estimators=xgboost_estimators,
        ),
    }
    fitted: dict[str, CalibratedModel] = {}
    for name, builder in builders.items():
        estimator = builder()
        estimator.fit(X_model_train[list(features)], y_model_train)
        calibrated = fit_sigmoid_calibrator(
            estimator,
            X_calibration[list(features)],
            y_calibration,
        )
        fitted[name] = CalibratedModel(
            name=name,
            requested_feature_names=requested_features,
            feature_names=features,
            dropped_all_missing_features=dropped_all_missing,
            estimator=estimator,
            calibrated_estimator=calibrated,
        )
    return fitted


def evaluate_calibrated_models(
    models: dict[str, CalibratedModel],
    X_test: pd.DataFrame,
    y_test: pd.Series,
    *,
    threshold: float = 0.5,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    """Evaluate already fitted models without exposing test data to fitting."""

    rows = []
    probabilities: dict[str, np.ndarray] = {}
    for name, bundle in models.items():
        probability = bundle.calibrated_estimator.predict_proba(
            X_test[list(bundle.feature_names)]
        )[:, 1]
        probabilities[name] = probability
        rows.append(
            {
                "model": name,
                "requested_feature_count": len(bundle.requested_feature_names),
                "feature_count": len(bundle.feature_names),
                "dropped_all_missing_features": ",".join(
                    bundle.dropped_all_missing_features
                ),
                "calibration": "sigmoid",
                **evaluate_probabilities(y_test, probability, threshold=threshold),
            }
        )
    return pd.DataFrame(rows), probabilities
