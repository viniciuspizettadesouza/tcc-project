"""Shared column contracts for the reconstruction pipeline and models."""

PHASE5_SOURCE_FEATURES = (
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

# Phase 5 consumes ``year`` and ``fico`` after Phase 2 derives them from these
# three raw columns. Keeping the mapping here prevents the ingestion and model
# modules from maintaining independent copies of the feature contract.
PHASE5_RAW_COLUMNS = (frozenset(PHASE5_SOURCE_FEATURES) - {"year", "fico"}) | {
    "issue_d",
    "fico_range_low",
    "fico_range_high",
}

PHASE5_CATEGORICAL_FEATURES = frozenset(
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
