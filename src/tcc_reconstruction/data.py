"""Memory-conscious ingestion and initial cleaning for Lending Club data.

This module implements Phase 2 of the reconstruction. It intentionally does not
impute model features, encode categories, balance classes, or train models; those
operations belong to later phases and must be fit using training data only.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

DATA_PATH_ENV = "LENDING_CLUB_DATA_PATH"
DEFAULT_DATA_DIRECTORY = Path("data/raw")
DEFAULT_CHUNK_SIZE = 100_000
DEFAULT_SAMPLE_SIZE = 10_000
DEFAULT_RANDOM_SEED = 42
SUPPORTED_SUFFIXES = frozenset({".csv", ".gz", ".gzip", ".zip"})

ALLOWED_LOAN_STATUSES = frozenset({"Fully Paid", "Charged Off", "Default"})
VERIFIED_INCOME_STATUSES = frozenset({"Verified", "Source Verified"})

# Union of the columns required by the thesis EDA, PoC 1, and PoC 2. Reading
# this subset avoids loading roughly 90 columns that are not used by the plan.
REQUIRED_COLUMNS = frozenset(
    {
        "id",
        "loan_amnt",
        "funded_amnt",
        "term",
        "int_rate",
        "installment",
        "grade",
        "sub_grade",
        "emp_length",
        "home_ownership",
        "annual_inc",
        "verification_status",
        "issue_d",
        "loan_status",
        "purpose",
        "addr_state",
        "dti",
        "earliest_cr_line",
        "inq_last_6mths",
        "open_acc",
        "total_acc",
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
        "avg_cur_bal",
        "fico_range_low",
        "fico_range_high",
        "all_util",
        "acc_open_past_24mths",
    }
)

STRING_INPUT_COLUMNS = frozenset(
    {
        "id",
        "term",
        "int_rate",
        "grade",
        "sub_grade",
        "emp_length",
        "home_ownership",
        "verification_status",
        "issue_d",
        "loan_status",
        "purpose",
        "addr_state",
        "earliest_cr_line",
        "initial_list_status",
        "application_type",
    }
)

CATEGORICAL_OUTPUT_COLUMNS = frozenset(
    {
        "term",
        "grade",
        "sub_grade",
        "emp_length",
        "home_ownership",
        "verification_status",
        "loan_status",
        "purpose",
        "addr_state",
        "initial_list_status",
        "application_type",
    }
)


class DataPipelineError(RuntimeError):
    """Base class for clear, user-facing ingestion failures."""


class DatasetPathError(DataPipelineError):
    """Raised when a dataset path cannot be resolved unambiguously."""


class SchemaValidationError(DataPipelineError):
    """Raised before full loading when expected columns are absent."""


class DataConversionError(DataPipelineError):
    """Raised when non-null source values cannot be converted safely."""


@dataclass(frozen=True)
class DataPipelineConfig:
    """Configuration for one deterministic ingestion run."""

    dataset_path: str | Path | None = None
    sample_size: int | None = DEFAULT_SAMPLE_SIZE
    random_seed: int = DEFAULT_RANDOM_SEED
    chunk_size: int = DEFAULT_CHUNK_SIZE
    verified_only: bool = True
    fail_on_conversion_errors: bool = True
    include_source_hash: bool = False

    def __post_init__(self) -> None:
        if self.sample_size is not None and self.sample_size <= 0:
            raise ValueError("sample_size must be positive or None for a full load")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")


@dataclass
class PipelineSummary:
    """Auditable counters collected before and after each operation."""

    source_columns: int
    selected_columns: int
    sample_size_requested: int | None
    random_seed: int
    verified_only: bool
    chunks_read: int = 0
    rows_read: int = 0
    rows_after_status_filter: int = 0
    rows_after_verification_filter: int = 0
    rows_output: int = 0
    source_memory_bytes: int = 0
    filtered_memory_bytes: int = 0
    output_memory_bytes: int = 0
    invalid_interest_rate_values: int = 0
    invalid_issue_date_values: int = 0
    invalid_fico_bound_values: int = 0
    status_counts: Counter[str] = field(default_factory=Counter)
    verification_counts_after_status_filter: Counter[str] = field(
        default_factory=Counter
    )
    missing_counts_after_filters: Counter[str] = field(default_factory=Counter)
    minimum_issue_year: int | None = None
    maximum_issue_year: int | None = None
    source_minimum_issue_month: str | None = None
    source_maximum_issue_month: str | None = None

    def to_dict(self) -> dict[str, Any]:
        denominator = self.rows_after_verification_filter
        if denominator:
            missing_percent = {
                column: round((count / denominator) * 100, 6)
                for column, count in sorted(self.missing_counts_after_filters.items())
            }
        else:
            missing_percent = {
                column: None for column in sorted(self.missing_counts_after_filters)
            }

        sparse_columns = [
            column
            for column, percent in missing_percent.items()
            if percent is not None and percent >= 90.0
        ]

        return {
            "chunks_read": self.chunks_read,
            "rows": {
                "read": self.rows_read,
                "after_status_filter": self.rows_after_status_filter,
                "after_verification_filter": self.rows_after_verification_filter,
                "output": self.rows_output,
            },
            "columns": {
                "source": self.source_columns,
                "selected_for_pipeline": self.selected_columns,
                "output": self.selected_columns + 2,
            },
            "sampling": {
                "requested": self.sample_size_requested,
                "seed": self.random_seed,
                "applied": (
                    self.sample_size_requested is not None
                    and self.rows_after_verification_filter > self.rows_output
                ),
            },
            "verified_only": self.verified_only,
            "memory_bytes": {
                "source_chunks_total": self.source_memory_bytes,
                "filtered_chunks_total": self.filtered_memory_bytes,
                "output_dataframe": self.output_memory_bytes,
            },
            "conversion_errors": {
                "int_rate": self.invalid_interest_rate_values,
                "issue_d": self.invalid_issue_date_values,
                "fico_bounds": self.invalid_fico_bound_values,
            },
            "issue_year": {
                "minimum": self.minimum_issue_year,
                "maximum": self.maximum_issue_year,
            },
            "source_issue_month": {
                "minimum": self.source_minimum_issue_month,
                "maximum": self.source_maximum_issue_month,
            },
            "loan_status_counts_before_filter": dict(
                sorted(self.status_counts.items())
            ),
            "verification_counts_after_status_filter": dict(
                sorted(self.verification_counts_after_status_filter.items())
            ),
            "missing_counts_after_filters": dict(
                sorted(self.missing_counts_after_filters.items())
            ),
            "missing_percent_after_filters": missing_percent,
            "sparse_columns_at_or_above_90_percent": sparse_columns,
        }


@dataclass(frozen=True)
class DataPipelineResult:
    """Prepared data plus source metadata and preprocessing counters."""

    data: pd.DataFrame
    manifest: dict[str, Any]
    summary: PipelineSummary

    def metadata_json(self) -> str:
        return json.dumps(
            {"manifest": self.manifest, "summary": self.summary.to_dict()},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )


def _repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_supported_dataset(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES


def _compression_for(path: Path) -> str | None:
    with path.open("rb") as source:
        signature = source.read(4)
    if signature.startswith(b"\x1f\x8b"):
        return "gzip"
    if signature.startswith(b"PK\x03\x04"):
        return "zip"
    return None


def _validated_dataset_path(candidate: str | Path, source: str) -> Path:
    path = Path(candidate).expanduser().resolve()
    if not path.is_file():
        raise DatasetPathError(
            f"dataset from {source} does not exist or is not a file: {path}"
        )
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise DatasetPathError(
            f"unsupported dataset extension for {path.name}; expected one of: {supported}"
        )
    return path


def resolve_dataset_path(
    explicit_path: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    repository_root: str | Path | None = None,
) -> Path:
    """Resolve explicit path, environment variable, then one file in data/raw."""

    if explicit_path is not None:
        return _validated_dataset_path(explicit_path, "explicit configuration")

    environment = os.environ if environ is None else environ
    environment_path = environment.get(DATA_PATH_ENV)
    if environment_path:
        return _validated_dataset_path(environment_path, DATA_PATH_ENV)

    root = Path(repository_root).resolve() if repository_root else _repository_root()
    data_directory = root / DEFAULT_DATA_DIRECTORY
    candidates = (
        sorted(path for path in data_directory.iterdir() if _is_supported_dataset(path))
        if data_directory.is_dir()
        else []
    )
    if len(candidates) == 1:
        return candidates[0].resolve()
    if not candidates:
        raise DatasetPathError(
            "dataset not found; pass --dataset, set LENDING_CLUB_DATA_PATH, "
            "or place exactly one supported file in data/raw/"
        )
    names = ", ".join(path.name for path in candidates)
    raise DatasetPathError(
        f"multiple dataset files found in data/raw/ ({names}); choose one explicitly"
    )


def inspect_schema(path: str | Path) -> tuple[str, ...]:
    """Read only the CSV header, before any expensive data loading."""

    dataset_path = _validated_dataset_path(path, "schema inspection")
    try:
        header = pd.read_csv(
            dataset_path,
            nrows=0,
            compression=_compression_for(dataset_path),
        )
    except Exception as error:  # pandas exposes multiple parser/compression errors
        raise DataPipelineError(
            f"could not read dataset header from {dataset_path.name}: {error}"
        ) from error
    return tuple(str(column) for column in header.columns)


def validate_schema(
    columns: Iterable[str], required_columns: Iterable[str] = REQUIRED_COLUMNS
) -> None:
    """Fail early with all missing columns in a stable, readable order."""

    observed = set(columns)
    missing = sorted(set(required_columns) - observed)
    if missing:
        raise SchemaValidationError(
            "dataset is missing required columns: " + ", ".join(missing)
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build_dataset_manifest(
    path: str | Path,
    *,
    columns: Iterable[str] | None = None,
    include_sha256: bool = False,
) -> dict[str, Any]:
    """Build metadata that can be recorded without exposing dataset rows."""

    dataset_path = _validated_dataset_path(path, "manifest generation")
    observed_columns = (
        tuple(columns) if columns is not None else inspect_schema(dataset_path)
    )
    modified_at = datetime.fromtimestamp(dataset_path.stat().st_mtime, tz=UTC)
    return {
        "file_name": dataset_path.name,
        "size_bytes": dataset_path.stat().st_size,
        "sha256": _sha256(dataset_path) if include_sha256 else None,
        "sha256_computed": include_sha256,
        "modified_at_utc": modified_at.isoformat(),
        "source_slug": "ethon0426/lending-club-20072020q1",
        "source_version_warning": "thesis and recovered notebook refer to 2020Q3",
        "column_count": len(observed_columns),
        "columns": list(observed_columns),
        "thesis_expected_rows": 2_925_493,
        "thesis_expected_columns": 142,
    }


def _normalized_counts(series: pd.Series) -> Counter[str]:
    counts: Counter[str] = Counter()
    for value, count in series.value_counts(dropna=False).items():
        label = "<NA>" if pd.isna(value) else str(value)
        counts[label] += int(count)
    return counts


def _convert_chunk(
    frame: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    converted = frame.copy()

    interest_source = converted["int_rate"]
    normalized_interest = interest_source.astype("string").str.strip().str.rstrip("%")
    interest = pd.to_numeric(normalized_interest, errors="coerce")
    invalid_interest = int((interest_source.notna() & interest.isna()).sum())
    converted["int_rate"] = interest.astype("Float64")

    issue_source = converted["issue_d"]
    issue_date = pd.to_datetime(issue_source, format="mixed", errors="coerce")
    invalid_issue_date = int((issue_source.notna() & issue_date.isna()).sum())
    converted["issue_d"] = issue_date
    converted["year"] = issue_date.dt.year.astype("Int16")

    low_source = converted["fico_range_low"]
    high_source = converted["fico_range_high"]
    low = pd.to_numeric(low_source, errors="coerce")
    high = pd.to_numeric(high_source, errors="coerce")
    invalid_fico = int(
        (low_source.notna() & low.isna()).sum()
        + (high_source.notna() & high.isna()).sum()
    )
    # Evidence-backed reconstruction decision: midpoint of the published range.
    # Missing either bound intentionally produces a missing derived FICO value.
    converted["fico"] = ((low + high) / 2).astype("Float64")

    return converted, {
        "int_rate": invalid_interest,
        "issue_d": invalid_issue_date,
        "fico_bounds": invalid_fico,
    }


def _sample_priority(frame: pd.DataFrame, seed: int) -> pd.Series:
    keys = (
        frame["id"].astype("string").fillna("<NA>")
        + "|"
        + frame.index.to_series().astype("string")
        + f"|{seed}"
    )
    return pd.util.hash_pandas_object(keys, index=False)


def _retain_sample(
    current: pd.DataFrame | None,
    new_rows: pd.DataFrame,
    sample_size: int,
    seed: int,
) -> pd.DataFrame:
    candidate = new_rows.copy()
    candidate["__sample_priority"] = _sample_priority(candidate, seed).to_numpy()
    candidate["__source_position"] = candidate.index.to_numpy()
    if current is not None:
        candidate = pd.concat([current, candidate], ignore_index=True)
    return candidate.nsmallest(
        sample_size, ["__sample_priority", "__source_position"], keep="first"
    )


def _update_issue_year_bounds(summary: PipelineSummary, frame: pd.DataFrame) -> None:
    years = frame["year"].dropna()
    if years.empty:
        return
    chunk_minimum = int(years.min())
    chunk_maximum = int(years.max())
    summary.minimum_issue_year = (
        chunk_minimum
        if summary.minimum_issue_year is None
        else min(summary.minimum_issue_year, chunk_minimum)
    )
    summary.maximum_issue_year = (
        chunk_maximum
        if summary.maximum_issue_year is None
        else max(summary.maximum_issue_year, chunk_maximum)
    )


def _update_source_issue_month_bounds(
    summary: PipelineSummary, issue_dates: pd.Series
) -> None:
    parsed = pd.to_datetime(issue_dates, format="mixed", errors="coerce").dropna()
    if parsed.empty:
        return
    chunk_minimum = parsed.min().strftime("%Y-%m")
    chunk_maximum = parsed.max().strftime("%Y-%m")
    summary.source_minimum_issue_month = min(
        value
        for value in (summary.source_minimum_issue_month, chunk_minimum)
        if value is not None
    )
    summary.source_maximum_issue_month = max(
        value
        for value in (summary.source_maximum_issue_month, chunk_maximum)
        if value is not None
    )


def _finalize_output(frame: pd.DataFrame) -> pd.DataFrame:
    internal_columns = ["__sample_priority", "__source_position"]
    output = frame.drop(columns=internal_columns, errors="ignore").reset_index(
        drop=True
    )
    for column in sorted(CATEGORICAL_OUTPUT_COLUMNS & set(output.columns)):
        output[column] = output[column].astype("category")
    return output


def run_data_pipeline(config: DataPipelineConfig | None = None) -> DataPipelineResult:
    """Validate, filter, convert, and optionally sample Lending Club data."""

    effective_config = config or DataPipelineConfig()
    path = resolve_dataset_path(effective_config.dataset_path)
    columns = inspect_schema(path)
    validate_schema(columns)
    manifest = build_dataset_manifest(
        path,
        columns=columns,
        include_sha256=effective_config.include_source_hash,
    )

    summary = PipelineSummary(
        source_columns=len(columns),
        selected_columns=len(REQUIRED_COLUMNS),
        sample_size_requested=effective_config.sample_size,
        random_seed=effective_config.random_seed,
        verified_only=effective_config.verified_only,
    )
    string_dtypes = {
        column: "string" for column in STRING_INPUT_COLUMNS & REQUIRED_COLUMNS
    }
    reader = pd.read_csv(
        path,
        compression=_compression_for(path),
        usecols=sorted(REQUIRED_COLUMNS),
        dtype=string_dtypes,
        chunksize=effective_config.chunk_size,
        low_memory=False,
        on_bad_lines="error",
    )

    retained_sample: pd.DataFrame | None = None
    retained_frames: list[pd.DataFrame] = []

    for chunk in reader:
        summary.chunks_read += 1
        summary.rows_read += len(chunk)
        summary.source_memory_bytes += int(chunk.memory_usage(deep=True).sum())
        summary.status_counts.update(_normalized_counts(chunk["loan_status"]))
        _update_source_issue_month_bounds(summary, chunk["issue_d"])

        status_filtered = chunk[chunk["loan_status"].isin(ALLOWED_LOAN_STATUSES)].copy()
        summary.rows_after_status_filter += len(status_filtered)
        summary.verification_counts_after_status_filter.update(
            _normalized_counts(status_filtered["verification_status"])
        )

        if effective_config.verified_only:
            filtered = status_filtered[
                status_filtered["verification_status"].isin(VERIFIED_INCOME_STATUSES)
            ].copy()
        else:
            filtered = status_filtered
        summary.rows_after_verification_filter += len(filtered)

        converted, conversion_errors = _convert_chunk(filtered)
        summary.invalid_interest_rate_values += conversion_errors["int_rate"]
        summary.invalid_issue_date_values += conversion_errors["issue_d"]
        summary.invalid_fico_bound_values += conversion_errors["fico_bounds"]

        if effective_config.fail_on_conversion_errors and any(
            conversion_errors.values()
        ):
            details = ", ".join(
                f"{column}={count}"
                for column, count in conversion_errors.items()
                if count
            )
            reader.close()
            raise DataConversionError(
                f"non-null values failed conversion in chunk {summary.chunks_read}: {details}"
            )

        summary.filtered_memory_bytes += int(converted.memory_usage(deep=True).sum())
        summary.missing_counts_after_filters.update(
            {column: int(count) for column, count in converted.isna().sum().items()}
        )
        _update_issue_year_bounds(summary, converted)

        if effective_config.sample_size is None and not converted.empty:
            retained_frames.append(converted)
        elif not converted.empty:
            retained_sample = _retain_sample(
                retained_sample,
                converted,
                effective_config.sample_size,
                effective_config.random_seed,
            )

    reader.close()

    if effective_config.sample_size is None:
        if retained_frames:
            combined = pd.concat(retained_frames, ignore_index=True)
        else:
            combined = pd.DataFrame(columns=sorted(REQUIRED_COLUMNS | {"fico", "year"}))
    elif retained_sample is not None:
        combined = retained_sample
    else:
        combined = pd.DataFrame(columns=sorted(REQUIRED_COLUMNS | {"fico", "year"}))

    output = _finalize_output(combined)
    summary.rows_output = len(output)
    summary.output_memory_bytes = int(output.memory_usage(deep=True).sum())
    return DataPipelineResult(data=output, manifest=manifest, summary=summary)
