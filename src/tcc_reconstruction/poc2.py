"""Leakage-safe baseline and XGBoost reconstruction for Phase 5."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd
from imblearn.pipeline import Pipeline as ImbalancedPipeline
from imblearn.under_sampling import RandomUnderSampler
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

PHASE5_RANDOM_SEED = 1
PHASE5_TEST_SIZE = 0.20

# The recovered cell 37 and Annex A enumerate 43 items, but one is the target
# `default`.  These are therefore the 42 original predictors, in source order.
SOURCE_FEATURES = (
    "year",
    "avg_cur_bal",
    "fico",
    "loan_amnt",
    "term",
    "int_rate",
    "installment",
    "sub_grade",
    "emp_length",
    "home_ownership",
    "annual_inc",
    "purpose",
    "addr_state",
    "dti",
    "earliest_cr_line",
    "inq_last_6mths",
    "open_acc",
    "pub_rec",
    "initial_list_status",
    "mths_since_last_major_derog",
    "application_type",
    "acc_now_delinq",
    "tot_cur_bal",
    "open_acc_6m",
    "open_act_il",
    "open_il_12m",
    "mths_since_rcnt_il",
    "total_bal_il",
    "open_rv_12m",
    "max_bal_bc",
    "total_cu_tl",
    "mo_sin_old_il_acct",
    "mo_sin_old_rev_tl_op",
    "mo_sin_rcnt_rev_tl_op",
    "mo_sin_rcnt_tl",
    "mort_acc",
    "mths_since_recent_bc",
    "mths_since_recent_revol_delinq",
    "num_actv_rev_tl",
    "num_il_tl",
    "pct_tl_nvr_dlq",
    "pub_rec_bankruptcies",
)
DERIVED_FEATURE = "monthly_load"
MODEL_FEATURES = SOURCE_FEATURES + (DERIVED_FEATURE,)

CATEGORICAL_FEATURES = frozenset(
    {
        "term",
        "sub_grade",
        "home_ownership",
        "purpose",
        "addr_state",
        "initial_list_status",
        "application_type",
    }
)

# Recovered cell 63 selected these source-level variables.  The old dummy
# `TERM 60 months` is represented by its semantic source feature `term`.
REDUCED_FEATURES = (
    "year",
    "monthly_load",
    "int_rate",
    "avg_cur_bal",
    "term",
    "fico",
    "dti",
    "mo_sin_old_rev_tl_op",
    "annual_inc",
    "emp_length",
    "num_actv_rev_tl",
    "home_ownership",
)

EMPLOYMENT_LENGTH_MAP = {
    "< 1 year": 0,
    "1 year": 1,
    "2 years": 2,
    "3 years": 3,
    "4 years": 4,
    "5 years": 5,
    "6 years": 6,
    "7 years": 7,
    "8 years": 8,
    "9 years": 9,
    "10+ years": 10,
}


def derive_target(loan_status: pd.Series) -> pd.Series:
    """Map Fully Paid to 0 and Charged Off/Default to 1."""

    target = loan_status.astype("string").map(
        {"Fully Paid": 0, "Charged Off": 1, "Default": 1}
    )
    if target.isna().any():
        invalid = sorted(loan_status[target.isna()].astype("string").unique())
        raise ValueError("unmapped loan statuses: " + ", ".join(invalid))
    return target.astype("int8").rename("default")


def calculate_monthly_load(frame: pd.DataFrame) -> pd.Series:
    """Calculate annualized installment burden; income zero is the -1 sentinel."""

    installment = pd.to_numeric(frame["installment"], errors="coerce")
    annual_income = pd.to_numeric(frame["annual_inc"], errors="coerce")
    monthly_load = ((installment * 12) / annual_income) * 100
    monthly_load = monthly_load.mask(annual_income.eq(0), -1.0)
    return monthly_load.rename(DERIVED_FEATURE)


def _extract_year(series: pd.Series) -> pd.Series:
    years = series.astype("string").str.extract(r"(\d{4})$")[0]
    return pd.to_numeric(years, errors="coerce")


def prepare_supervised_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Apply deterministic feature engineering without learning from the data."""

    required = set(SOURCE_FEATURES) | {"loan_status"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError("missing PoC 2 columns: " + ", ".join(missing))

    features = frame[list(SOURCE_FEATURES)].copy()
    features[DERIVED_FEATURE] = calculate_monthly_load(frame)
    features["emp_length"] = (
        features["emp_length"].astype("string").map(EMPLOYMENT_LENGTH_MAP)
    )
    features["earliest_cr_line"] = _extract_year(features["earliest_cr_line"])

    # log1p is a fixed row-wise transformation and learns no population statistic.
    for column in ("annual_inc", "open_acc"):
        numeric = pd.to_numeric(features[column], errors="coerce")
        negative = numeric.notna() & numeric.lt(0)
        if negative.any():
            raise ValueError(f"{column} contains {int(negative.sum())} negative values")
        features[column] = np.log1p(numeric)

    for column in MODEL_FEATURES:
        if column in CATEGORICAL_FEATURES:
            values = features[column].astype("string")
            features[column] = values.where(values.notna(), np.nan).astype(object)
        else:
            features[column] = pd.to_numeric(features[column], errors="coerce")

    return features[list(MODEL_FEATURES)], derive_target(frame["loan_status"])


def split_feature_types(feature_names: Sequence[str]) -> tuple[list[str], list[str]]:
    """Return numeric and categorical columns in stable source order."""

    unknown = sorted(set(feature_names) - set(MODEL_FEATURES))
    if unknown:
        raise ValueError("unknown model features: " + ", ".join(unknown))
    categorical = [name for name in feature_names if name in CATEGORICAL_FEATURES]
    numeric = [name for name in feature_names if name not in CATEGORICAL_FEATURES]
    return numeric, categorical


def build_preprocessor(
    feature_names: Sequence[str], *, scale_numeric: bool
) -> ColumnTransformer:
    """Build train-fitted imputers, one-hot encoding, and optional scaling."""

    numeric, categorical = split_feature_types(feature_names)
    numeric_steps: list[tuple[str, Any]] = [
        ("imputer", SimpleImputer(strategy="median"))
    ]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))
    numeric_pipeline = Pipeline(numeric_steps)
    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=True),
            ),
        ]
    )
    return ColumnTransformer(
        [
            ("numeric", numeric_pipeline, numeric),
            ("categorical", categorical_pipeline, categorical),
        ],
        sparse_threshold=1.0,
    )


def build_logistic_pipeline(
    feature_names: Sequence[str], *, random_seed: int = PHASE5_RANDOM_SEED
) -> ImbalancedPipeline:
    """Create the real, separately named logistic-regression baseline."""

    return ImbalancedPipeline(
        [
            ("undersampler", RandomUnderSampler(random_state=random_seed)),
            ("preprocessor", build_preprocessor(feature_names, scale_numeric=True)),
            (
                "logistic_regression",
                LogisticRegression(
                    solver="liblinear",
                    max_iter=1_000,
                    random_state=random_seed,
                ),
            ),
        ]
    )


def build_xgboost_pipeline(
    feature_names: Sequence[str],
    *,
    random_seed: int = PHASE5_RANDOM_SEED,
    n_estimators: int = 200,
) -> ImbalancedPipeline:
    """Create a binary classifier with explicit, deterministic parameters."""

    return ImbalancedPipeline(
        [
            ("undersampler", RandomUnderSampler(random_state=random_seed)),
            ("preprocessor", build_preprocessor(feature_names, scale_numeric=False)),
            (
                "xgboost_classifier",
                XGBClassifier(
                    objective="binary:logistic",
                    eval_metric="auc",
                    importance_type="gain",
                    n_estimators=n_estimators,
                    learning_rate=0.05,
                    max_depth=4,
                    min_child_weight=1,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    reg_lambda=1.0,
                    random_state=random_seed,
                    n_jobs=4,
                    tree_method="hist",
                ),
            ),
        ]
    )


def evaluate_classifier(
    estimator: ImbalancedPipeline, X: pd.DataFrame, y: pd.Series
) -> dict[str, Any]:
    """Evaluate with positive-class probabilities and retain label AUC historically."""

    probability = estimator.predict_proba(X)[:, 1]
    prediction = estimator.predict(X)
    report = classification_report(y, prediction, output_dict=True, zero_division=0)
    return {
        "roc_auc_probability": float(roc_auc_score(y, probability)),
        "historical_roc_auc_labels": float(roc_auc_score(y, prediction)),
        "accuracy": float(accuracy_score(y, prediction)),
        "confusion_matrix": confusion_matrix(y, prediction).tolist(),
        "class_0": report["0"],
        "class_1": report["1"],
        "probability": probability,
        "prediction": prediction,
    }


def aggregate_xgboost_importance(
    estimator: ImbalancedPipeline, feature_names: Sequence[str]
) -> pd.DataFrame:
    """Aggregate gain importance from one-hot columns back to source features."""

    numeric, categorical = split_feature_types(feature_names)
    preprocessor = estimator.named_steps["preprocessor"]
    encoder = preprocessor.named_transformers_["categorical"].named_steps["onehot"]
    source_names = list(numeric)
    for column, categories in zip(categorical, encoder.categories_, strict=True):
        source_names.extend([column] * len(categories))

    model = estimator.named_steps["xgboost_classifier"]
    importances = model.feature_importances_
    if len(source_names) != len(importances):
        raise ValueError(
            f"importance mapping mismatch: {len(source_names)} names, "
            f"{len(importances)} values"
        )
    return (
        pd.DataFrame({"feature": source_names, "gain": importances})
        .groupby("feature", as_index=False)["gain"]
        .sum()
        .sort_values("gain", ascending=False, ignore_index=True)
    )


def resampled_class_counts(
    estimator: ImbalancedPipeline, y_train: pd.Series
) -> dict[int, int]:
    """Return class counts selected from training by RandomUnderSampler."""

    indices = estimator.named_steps["undersampler"].sample_indices_
    return {
        int(label): int(count)
        for label, count in y_train.iloc[indices].value_counts().sort_index().items()
    }
