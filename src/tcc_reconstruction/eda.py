"""Exploratory analysis helpers for Phase 3 of the reconstruction.

The functions in this module operate on the filtered output of the Phase 2 data
pipeline.  They do not impute, encode, balance, or otherwise prepare model
features; those transformations remain reserved for Phase 5.
"""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

DEFAULT_EDA_SEED = 42
DEFAULT_PLOT_SAMPLE_SIZE = 100_000
DEFAULTED_LOAN_STATUSES = frozenset({"Charged Off", "Default"})

FIGURE_TITLES = {
    9: "Distribuição do Montante de Empréstimo por Ano",
    10: "Correlação entre loan_amnt e funded_amnt",
    11: "Correlação entre fico_range_low e fico_range_high",
    12: "Correlação entre total_acc e open_acc",
    13: "Gráfico de Barras das Razões de Inadimplência",
    14: "Mapa Coroplético de Empréstimos por Estado",
    15: "Distribuição da Relação Dívida/Renda (DTI)",
    16: (
        "Função de densidade de probabilidade para a variável renda anual "
        "(Antes da transformação)"
    ),
    17: (
        "Função de densidade de probabilidade para a variável renda anual "
        "(Depois da transformação)"
    ),
    18: (
        "Histograma da variável número de linhas de crédito abertas "
        "(Antes da transformação)"
    ),
    19: (
        "Histograma da variável número de linhas de crédito abertas "
        "(Depois da transformação)"
    ),
}

CORRELATION_PAIRS = (
    ("loan_amnt", "funded_amnt"),
    ("fico_range_low", "fico_range_high"),
    ("total_acc", "open_acc"),
)


def calculate_pearson_correlations(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate the three Pearson correlations required by Figures 10–12."""

    records: list[dict[str, object]] = []
    for left, right in CORRELATION_PAIRS:
        paired = frame[[left, right]].dropna()
        records.append(
            {
                "variavel_x": left,
                "variavel_y": right,
                "n_pares_validos": len(paired),
                "correlacao_pearson": paired[left].corr(paired[right]),
            }
        )
    return pd.DataFrame.from_records(records)


def select_defaulted_loans(frame: pd.DataFrame) -> pd.DataFrame:
    """Return only the population that actually defaulted for Figure 13."""

    return frame[frame["loan_status"].isin(DEFAULTED_LOAN_STATUSES)].copy()


def deterministic_plot_sample(
    frame: pd.DataFrame,
    *,
    sample_size: int = DEFAULT_PLOT_SAMPLE_SIZE,
    seed: int = DEFAULT_EDA_SEED,
) -> pd.DataFrame:
    """Bound rendering cost with a stable hash sample, without changing metrics."""

    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    if len(frame) <= sample_size:
        return frame.copy()

    identifiers = frame["id"].astype("string").fillna("<NA>")
    keys = identifiers + "|" + frame.index.to_series().astype("string") + f"|{seed}"
    priorities = pd.util.hash_pandas_object(keys, index=False)
    positions = np.argpartition(priorities.to_numpy(), sample_size - 1)[:sample_size]
    sampled = frame.iloc[positions].copy()
    sampled["__priority"] = priorities.iloc[positions].to_numpy()
    return sampled.sort_values("__priority").drop(columns="__priority")


def add_log1p_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Add non-destructive log1p views used only in Figures 17 and 19."""

    transformed = frame.copy()
    for source, target in (
        ("annual_inc", "annual_inc_log1p"),
        ("open_acc", "open_acc_log1p"),
    ):
        numeric = pd.to_numeric(transformed[source], errors="coerce")
        invalid = numeric.notna() & (numeric < 0)
        if invalid.any():
            raise ValueError(f"{source} contains {int(invalid.sum())} negative values")
        transformed[target] = np.log1p(numeric)
    return transformed


def aggregate_column_profile(
    frame: pd.DataFrame, columns: Iterable[str]
) -> pd.DataFrame:
    """Create a privacy-conscious table with aggregates instead of borrower rows."""

    records: list[dict[str, object]] = []
    for column in columns:
        series = frame[column]
        numeric = pd.to_numeric(series, errors="coerce")
        records.append(
            {
                "coluna": column,
                "tipo": str(series.dtype),
                "não_nulos": int(series.notna().sum()),
                "ausentes": int(series.isna().sum()),
                "mínimo": numeric.min() if numeric.notna().any() else pd.NA,
                "mediana": numeric.median() if numeric.notna().any() else pd.NA,
                "máximo": numeric.max() if numeric.notna().any() else pd.NA,
            }
        )
    return pd.DataFrame.from_records(records)
