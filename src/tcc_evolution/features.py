"""Decision-time feature contracts for post-reconstruction experiments."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum

import pandas as pd

from tcc_reconstruction.poc2 import MODEL_FEATURES

TARGET_NAME = "default"
HISTORICAL_FEATURES = tuple(MODEL_FEATURES)

POST_DECISION_FEATURES = frozenset(
    {
        "int_rate",
        "installment",
        "sub_grade",
        "initial_list_status",
        "monthly_load",
    }
)
APPLICATION_INPUT_FEATURES = frozenset(
    {"loan_amnt", "term", "purpose", "application_type"}
)

APPLICATION_FEATURES = tuple(
    feature
    for feature in HISTORICAL_FEATURES
    if feature not in POST_DECISION_FEATURES
)
PROFILE_FEATURES = tuple(
    feature
    for feature in APPLICATION_FEATURES
    if feature not in APPLICATION_INPUT_FEATURES
)


class AvailabilityStage(StrEnum):
    """Earliest declared decision stage at which a feature is available."""

    PROFILE = "profile"
    APPLICATION = "application"
    POST_DECISION = "post_decision"


@dataclass(frozen=True)
class FeatureAvailability:
    """Availability and rationale for one historical model input."""

    feature: str
    availability_stage: str
    historical_model: bool
    application_known: bool
    profile_only: bool
    rationale: str


_RATIONALES = {
    "year": "Calendar context known at the decision timestamp.",
    "avg_cur_bal": "Credit-file balance aggregate available before a new offer.",
    "fico": "Credit-bureau score range observed before underwriting output.",
    "loan_amnt": "Loan amount supplied in the known-application scenario.",
    "term": "Requested term supplied in the known-application scenario.",
    "int_rate": "Interest rate assigned by platform pricing after underwriting.",
    "installment": "Payment calculated from amount, term, and assigned rate.",
    "sub_grade": "Platform underwriting grade assigned after risk assessment.",
    "emp_length": "Borrower profile information available before the offer.",
    "home_ownership": "Borrower profile information available before the offer.",
    "annual_inc": "Borrower income available before the offer.",
    "purpose": "Declared loan purpose supplied with a known application.",
    "addr_state": "Borrower location available before the offer.",
    "dti": "Debt-to-income profile measure available before the offer.",
    "earliest_cr_line": "Credit-file history available before the offer.",
    "inq_last_6mths": "Credit-file inquiry history available before the offer.",
    "open_acc": "Credit-file account count available before the offer.",
    "pub_rec": "Credit-file public-record count available before the offer.",
    "initial_list_status": "Platform listing status determined after intake.",
    "mths_since_last_major_derog": "Credit-file derogatory-history measure.",
    "application_type": "Individual or joint choice supplied with an application.",
    "acc_now_delinq": "Credit-file delinquency state available before the offer.",
    "tot_cur_bal": "Credit-file current-balance aggregate.",
    "open_acc_6m": "Credit-file recent-account measure.",
    "open_act_il": "Credit-file installment-account measure.",
    "open_il_12m": "Credit-file recent installment-account measure.",
    "mths_since_rcnt_il": "Credit-file installment-history measure.",
    "total_bal_il": "Credit-file installment-balance aggregate.",
    "open_rv_12m": "Credit-file recent revolving-account measure.",
    "max_bal_bc": "Credit-file bankcard-balance measure.",
    "total_cu_tl": "Credit-file finance-account measure.",
    "mo_sin_old_il_acct": "Credit-file installment-history age.",
    "mo_sin_old_rev_tl_op": "Credit-file revolving-history age.",
    "mo_sin_rcnt_rev_tl_op": "Credit-file recent revolving-history age.",
    "mo_sin_rcnt_tl": "Credit-file recent-trade age.",
    "mort_acc": "Credit-file mortgage-account count.",
    "mths_since_recent_bc": "Credit-file recent-bankcard age.",
    "mths_since_recent_revol_delinq": "Credit-file revolving-delinquency age.",
    "num_actv_rev_tl": "Credit-file active revolving-trade count.",
    "num_il_tl": "Credit-file installment-trade count.",
    "pct_tl_nvr_dlq": "Credit-file share of trades never delinquent.",
    "pub_rec_bankruptcies": "Credit-file bankruptcy count.",
    "monthly_load": "Derived from installment, which depends on assigned pricing.",
}


def availability_stage(feature: str) -> AvailabilityStage:
    """Return the declared earliest availability stage for one feature."""

    if feature not in HISTORICAL_FEATURES:
        raise ValueError(f"unknown historical feature: {feature}")
    if feature in POST_DECISION_FEATURES:
        return AvailabilityStage.POST_DECISION
    if feature in APPLICATION_INPUT_FEATURES:
        return AvailabilityStage.APPLICATION
    return AvailabilityStage.PROFILE


def feature_availability_records() -> tuple[FeatureAvailability, ...]:
    """Return one ordered governance record for every historical input."""

    records = []
    for feature in HISTORICAL_FEATURES:
        stage = availability_stage(feature)
        records.append(
            FeatureAvailability(
                feature=feature,
                availability_stage=stage.value,
                historical_model=True,
                application_known=feature in APPLICATION_FEATURES,
                profile_only=feature in PROFILE_FEATURES,
                rationale=_RATIONALES[feature],
            )
        )
    return tuple(records)


def feature_availability_table() -> pd.DataFrame:
    """Return the complete feature-governance table in historical order."""

    return pd.DataFrame(asdict(record) for record in feature_availability_records())


if set(_RATIONALES) != set(HISTORICAL_FEATURES):
    missing = sorted(set(HISTORICAL_FEATURES) - set(_RATIONALES))
    extra = sorted(set(_RATIONALES) - set(HISTORICAL_FEATURES))
    raise RuntimeError(f"feature rationale mismatch; missing={missing}, extra={extra}")
if TARGET_NAME in HISTORICAL_FEATURES:
    raise RuntimeError("target leakage in historical feature contract")
