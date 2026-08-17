#!/usr/bin/env python3
"""Validate the active evolutive notebook and its derivation metadata."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import nbformat

try:
    from scripts.create_evolved_notebook import SOURCE_SHA256
except ModuleNotFoundError:  # Support direct execution from the scripts directory.
    from create_evolved_notebook import SOURCE_SHA256  # type: ignore[no-redef]

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = REPOSITORY_ROOT / "notebooks" / "tcc-evolved.ipynb"
FORBIDDEN_FRAGMENTS = (
    "/content/",
    "/home/",
    "/Users/",
    "C:\\Users\\",
    "kaggle.json",
    "BEGIN OPENSSH PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
)
KNOWN_BORROWER_IDENTIFIER = "1077501"
IDENTIFIER_HEADER_PATTERN = re.compile(
    r"<th\b[^>]*>\s*(?:id|member_id|url|emp_title|desc|title|zip_code)\s*</th>",
    flags=re.IGNORECASE,
)


class EvolvedNotebookValidationError(RuntimeError):
    """Raised when the evolutive notebook violates its foundation contract."""


def validate_evolved_notebook(path: Path = NOTEBOOK_PATH) -> dict[str, Any]:
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    source = "\n".join(cell.source for cell in notebook.cells)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    errors: list[str] = []

    metadata = notebook.metadata.get("tcc_evolution", {})
    expected_metadata = {
        "schema_version": 1,
        "derived_from": "notebooks/tcc-reconstructed.ipynb",
        "derived_from_sha256": SOURCE_SHA256,
        "base_commit": "467a623a0e992363c6d3207d9e427973b751af8e",
        "derivation_date": "2026-08-17",
        "active_notebook": True,
    }
    for key, expected in expected_metadata.items():
        if metadata.get(key) != expected:
            errors.append(f"invalid evolution metadata: {key}")
    if metadata.get("completed_phases") != [
        "E0",
        "E1",
        "E2",
        "E3",
        "E4",
        "E5",
    ]:
        errors.append("invalid evolution metadata: completed_phases")

    required_text = (
        "# Evolução metodológica do TCC",
        "extensão nova derivada da reconstrução concluída",
        SOURCE_SHA256,
        "target da",
        "PoC preditiva permanece inadimplência",
        "não demonstram adesão",
        "## 16. Fase E1 — escopo metodológico e momentos de inferência",
        "feature_availability_table",
        "Esta fase não treina modelos novos",
        "## 17. Fase E2 — modelos pré-oferta e métricas ampliadas",
        "fit_calibrated_models",
        "evaluate_calibrated_models",
        "Nenhum modelo é declarado vencedor",
        "## 18. Fase E3 — validação temporal com maturidade",
        "build_temporal_partitions",
        "random_vs_temporal_e3",
        "nenhum resultado temporal é usado para retreinamento",
        "## 19. Fase E4 — bandas experimentais e sensibilidade da PoC 1",
        "fit_experimental_bands",
        "population_stability_index",
        "campaign_distance_sensitivity",
        "Nenhum percentil é recomendado automaticamente",
        "## 20. Fase E5 — consolidação e validação evolutiva",
        "docs/result-comparison.md` permanece dedicado exclusivamente",
        "ponto de entrada para pesquisas futuras",
    )
    errors.extend(
        f"missing provenance text: {fragment}"
        for fragment in required_text
        if fragment not in source
    )

    execution_counts = [cell.execution_count for cell in code_cells]
    if execution_counts != list(range(1, len(code_cells) + 1)):
        errors.append("saved code cells are not executed sequentially")
    output_errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.output_type == "error"
    ]
    if output_errors:
        errors.append(f"saved notebook contains {len(output_errors)} error output(s)")
    phase_positions = [
        source.index(f"Fase E{phase}")
        for phase in range(1, 6)
        if f"Fase E{phase}" in source
    ]
    if len(phase_positions) != 5 or phase_positions != sorted(phase_positions):
        errors.append("evolution phases E1-E5 are missing or out of order")

    output_texts: list[str] = []
    for cell in code_cells:
        for output in cell.get("outputs", []):
            if output.output_type == "stream":
                output_texts.append(str(output.get("text", "")))
            for value in output.get("data", {}).values():
                if isinstance(value, str):
                    output_texts.append(value)
                elif isinstance(value, list) and all(
                    isinstance(item, str) for item in value
                ):
                    output_texts.append("".join(value))
    output_text = "\n".join(output_texts)
    for fragment in FORBIDDEN_FRAGMENTS:
        if fragment in source:
            errors.append(f"forbidden notebook fragment: {fragment}")
        if fragment in output_text:
            errors.append(f"forbidden output fragment: {fragment}")
    if KNOWN_BORROWER_IDENTIFIER in output_text:
        errors.append("known borrower identifier found in notebook outputs")
    if IDENTIFIER_HEADER_PATTERN.search(output_text):
        errors.append("record-level identifier column found in notebook outputs")

    if errors:
        raise EvolvedNotebookValidationError("\n".join(errors))
    return {
        "cells": len(notebook.cells),
        "markdown_cells": sum(cell.cell_type == "markdown" for cell in notebook.cells),
        "code_cells": len(code_cells),
        "executed_code_cells": len(execution_counts),
        "error_outputs": 0,
        "saved_outputs": sum(len(cell.get("outputs", [])) for cell in code_cells),
        "unsafe_output_fragments": 0,
        "derived_from_sha256": SOURCE_SHA256,
    }


def main() -> int:
    try:
        summary = validate_evolved_notebook()
    except (EvolvedNotebookValidationError, OSError, ValueError) as error:
        print(f"ERROR  {error}")
        return 1
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
