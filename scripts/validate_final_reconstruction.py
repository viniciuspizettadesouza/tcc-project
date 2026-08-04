#!/usr/bin/env python3
"""Audit the final reconstructed notebook and tracked repository artifacts."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import subprocess
from typing import Any

import nbformat

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = REPOSITORY_ROOT / "notebooks" / "tcc-reconstructed.ipynb"
README_PATH = REPOSITORY_ROOT / "README.md"
RESULT_COMPARISON_PATH = REPOSITORY_ROOT / "docs" / "result-comparison.md"

MAIN_SECTIONS = (
    "## 1. Descrição do projeto",
    "## 2. Notas de reprodutibilidade",
    "## 3. Aquisição do dataset",
    "## 4. Imports e configuração",
    "## 5. Carregamento e populações analíticas",
    "## 6. Análise exploratória dos dados",
    "## 7. Limpeza e pré-processamento",
    "## 8. PoC 1",
    "## 9. PoC 2",
    "## 10. Score e taxa personalizada",
    "## 11. Resultados",
    "## 12. Comparação com a tese",
    "## 13. Limitações",
    "## 14. Conclusões",
    "## 15. Proveniência e notas de reconstrução",
)

FORBIDDEN_NOTEBOOK_FRAGMENTS = (
    "/content/",
    "/home/",
    "C:\\Users\\",
    "kaggle.json",
)
FORBIDDEN_TRACKED_NAMES = {".env", "kaggle.json"}
MODEL_BINARY_SUFFIXES = {
    ".bin",
    ".joblib",
    ".model",
    ".onnx",
    ".pickle",
    ".pkl",
    ".ubj",
}
FINAL_RESULT_STATUSES = {
    "reproduzido",
    "parcial",
    "divergente",
    "conflitante",
    "irreproduzível",
}
FIGURE_SECTION_MARKERS = (
    "### Figura 9",
    "### Figuras 10–12",
    "### Figura 13",
    "### Figura 14",
    "### Figura 15",
    "### Figuras 16–17",
    "### Figuras 18–19",
    "### Figura 20",
    "### Figuras 21–22",
    "### Figura 23",
    "### Figura 24",
    "### Figura 25",
    "### Figuras 26–29",
)


class FinalValidationError(RuntimeError):
    """Raised when one or more final reconstruction checks fail."""


def validate_notebook(path: Path = NOTEBOOK_PATH) -> dict[str, Any]:
    """Validate narrative, saved execution, outputs, and portable paths."""

    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    source = "\n".join(cell.source for cell in notebook.cells)
    code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    errors: list[str] = []

    section_positions: list[int] = []
    for heading in MAIN_SECTIONS:
        try:
            section_positions.append(source.index(heading))
        except ValueError:
            errors.append(f"missing main section: {heading}")
    if section_positions and section_positions != sorted(section_positions):
        errors.append("main sections are not in the required order")

    for heading in MAIN_SECTIONS:
        matching_cells = [
            cell
            for cell in notebook.cells
            if cell.cell_type == "markdown" and heading in cell.source
        ]
        if matching_cells and "**Tipo:**" not in matching_cells[0].source:
            errors.append(f"main section does not declare type: {heading}")

    execution_counts = [cell.execution_count for cell in code_cells]
    expected_counts = list(range(1, len(code_cells) + 1))
    if execution_counts != expected_counts:
        errors.append("code cells do not have a complete sequential saved execution")

    output_errors = [
        output
        for cell in code_cells
        for output in cell.get("outputs", [])
        if output.output_type == "error"
    ]
    if output_errors:
        errors.append(f"saved notebook contains {len(output_errors)} error output(s)")

    png_outputs = 0
    plotly_outputs = 0
    for cell in code_cells:
        for output in cell.get("outputs", []):
            data = output.get("data", {})
            png_outputs += int("image/png" in data)
            plotly_outputs += int("application/vnd.plotly.v1+json" in data)
    if png_outputs != 20 or plotly_outputs != 1:
        errors.append(
            "expected 20 raster figure outputs and one Plotly output for Figures 9–29; "
            f"found {png_outputs} and {plotly_outputs}"
        )

    missing_figure_sections = [
        marker for marker in FIGURE_SECTION_MARKERS if marker not in source
    ]
    if missing_figure_sections:
        errors.append(
            "missing figure sections: " + ", ".join(missing_figure_sections)
        )
    if source.count("figsize=") < 15 or "height=550" not in source:
        errors.append("figure dimensions are not explicit for the saved visualizations")
    if source.count("xlabel") < 17 or source.count("ylabel") < 13:
        errors.append("figure axis labels are incomplete")

    if "## 8. PoC 1" not in source or "## 9. PoC 2" not in source:
        errors.append("both proofs of concept must be present")
    if "SEED = 42" not in source or "PHASE5_RANDOM_SEED" not in source:
        errors.append("documented deterministic seeds are missing")
    if "requirements.txt" not in source:
        errors.append("dependency-version provenance is missing")

    for fragment in FORBIDDEN_NOTEBOOK_FRAGMENTS:
        if fragment in source:
            errors.append(f"forbidden notebook fragment: {fragment}")

    if errors:
        raise FinalValidationError("\n".join(errors))
    return {
        "cells": len(notebook.cells),
        "markdown_cells": sum(
            cell.cell_type == "markdown" for cell in notebook.cells
        ),
        "code_cells": len(code_cells),
        "executed_code_cells": len(execution_counts),
        "error_outputs": 0,
        "png_figure_outputs": png_outputs,
        "plotly_figure_outputs": plotly_outputs,
        "figure_sections": len(FIGURE_SECTION_MARKERS),
        "explicit_figure_dimensions": True,
        "figure_axes_labeled": True,
        "main_sections": len(MAIN_SECTIONS),
    }


def repository_candidate_files(repository_root: Path = REPOSITORY_ROOT) -> list[Path]:
    """Return tracked and unignored candidate paths without inspecting ignored data."""

    output = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repository_root,
    ).decode("utf-8")
    return [Path(item) for item in output.split("\0") if item]


def validate_tracked_artifacts(
    repository_root: Path = REPOSITORY_ROOT,
) -> dict[str, Any]:
    """Reject tracked datasets, credentials, and serialized model binaries."""

    paths = repository_candidate_files(repository_root)
    violations: list[str] = []
    for relative_path in paths:
        lowered = relative_path.as_posix().lower()
        if lowered.startswith("data/raw/") or lowered.startswith("data/interim/"):
            violations.append(f"tracked dataset path: {relative_path}")
        if relative_path.name.lower() in FORBIDDEN_TRACKED_NAMES:
            violations.append(f"tracked credential file: {relative_path}")
        if relative_path.suffix.lower() in MODEL_BINARY_SUFFIXES:
            violations.append(f"tracked model binary: {relative_path}")
    if violations:
        raise FinalValidationError("\n".join(violations))
    return {
        "tracked_files": len(paths),
        "tracked_dataset_files": 0,
        "tracked_credential_files": 0,
        "tracked_model_binaries": 0,
    }


def validate_requirements(
    path: Path = REPOSITORY_ROOT / "requirements.txt",
) -> dict[str, Any]:
    """Ensure every direct runtime dependency is exactly pinned."""

    dependencies = []
    unpinned = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-e "):
            continue
        dependencies.append(line)
        if "==" not in line:
            unpinned.append(line)
    if unpinned:
        raise FinalValidationError("unpinned dependencies: " + ", ".join(unpinned))
    return {"pinned_direct_dependencies": len(dependencies)}


def validate_result_comparison(
    path: Path = RESULT_COMPARISON_PATH,
) -> dict[str, Any]:
    """Require every result-table row to have one final classification."""

    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 6 or cells[0] == "Item" or set(cells[0]) == {"-"}:
            continue
        rows.append(cells)
    invalid = [cells[0] for cells in rows if cells[-1] not in FINAL_RESULT_STATUSES]
    if invalid:
        raise FinalValidationError(
            "result rows without final classification: " + ", ".join(invalid)
        )
    counts = Counter(cells[-1] for cells in rows)
    return {
        "classified_items": len(rows),
        "status_counts": dict(sorted(counts.items())),
        "pending_items": 0,
    }


def validate_readme(path: Path = README_PATH) -> dict[str, Any]:
    """Check that local and Colab execution instructions are complete and current."""

    source = path.read_text(encoding="utf-8")
    required = (
        "## Instalação local do projeto",
        "## Execução local completa",
        "## Execução no Google Colab",
        "notebooks/tcc-reconstructed.ipynb",
        "scripts/validate_final_reconstruction.py",
        "LENDING_CLUB_DATA_PATH",
        "--ExecutePreprocessor.timeout=1800",
    )
    missing = [fragment for fragment in required if fragment not in source]
    if missing:
        raise FinalValidationError("README is missing: " + ", ".join(missing))
    stale = (
        "Notebook reconstruído | ainda não criado",
        "somente o notebook recuperado está disponível",
    )
    found_stale = [fragment for fragment in stale if fragment in source]
    if found_stale:
        raise FinalValidationError(
            "README contains stale text: " + ", ".join(found_stale)
        )
    return {"local_instructions": True, "colab_instructions": True}


def run_final_validation() -> dict[str, Any]:
    """Run all final checks and return a machine-readable summary."""

    return {
        "notebook": validate_notebook(),
        "repository": validate_tracked_artifacts(),
        "environment": validate_requirements(),
        "result_comparison": validate_result_comparison(),
        "readme": validate_readme(),
    }


def main() -> int:
    print(json.dumps(run_final_validation(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
