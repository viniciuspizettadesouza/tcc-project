#!/usr/bin/env python3
"""Create the evolutive notebook from the immutable reconstruction snapshot."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import nbformat

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPOSITORY_ROOT / "notebooks" / "tcc-reconstructed.ipynb"
DEFAULT_OUTPUT_PATH = REPOSITORY_ROOT / "notebooks" / "tcc-evolved.ipynb"
SOURCE_SHA256 = "4b9f385dd51a798248dd6bfcbf0ad2e8815f90de7bc5fb59cd98a7431057d044"
BASE_COMMIT = "467a623a0e992363c6d3207d9e427973b751af8e"
DERIVATION_DATE = "2026-08-17"

PROVENANCE_MARKDOWN = f"""# Evolução metodológica do TCC

**Tipo:** extensão nova derivada da reconstrução concluída.

Este é o notebook ativo para melhorias posteriores às Fases 0–8. O target da
PoC preditiva permanece inadimplência; novos resultados não demonstram adesão
ou conversão de campanhas e não são atribuídos ao autor ou à execução original
do TCC.

**Proveniência da derivação**

- fonte imutável: `notebooks/tcc-reconstructed.ipynb`;
- SHA-256 da fonte: `{SOURCE_SHA256}`;
- commit-base: `{BASE_COMMIT}`;
- data da derivação: {DERIVATION_DATE};
- destino de novas fases: E0, E1 e posteriores.

Os notebooks recuperado e reconstruído permanecem registros históricos e não
devem ser alterados ou reexecutados in-place.
"""


def sha256(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def create_evolved_notebook(
    output_path: Path = DEFAULT_OUTPUT_PATH,
    *,
    source_path: Path = SOURCE_PATH,
) -> Path:
    """Derive one new notebook while refusing source drift or overwrite."""

    if sha256(source_path) != SOURCE_SHA256:
        raise ValueError("immutable reconstructed notebook does not match its baseline")
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite evolutive notebook: {output_path}")

    notebook = nbformat.read(source_path, as_version=4)
    notebook.cells.insert(0, nbformat.v4.new_markdown_cell(PROVENANCE_MARKDOWN))
    notebook.metadata["tcc_evolution"] = {
        "schema_version": 1,
        "derived_from": "notebooks/tcc-reconstructed.ipynb",
        "derived_from_sha256": SOURCE_SHA256,
        "base_commit": BASE_COMMIT,
        "derivation_date": DERIVATION_DATE,
        "active_notebook": True,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, output_path)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output = create_evolved_notebook(args.output.resolve())
    except (FileExistsError, OSError, ValueError) as error:
        print(f"ERROR  {error}")
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
