from __future__ import annotations

import hashlib
import copy
import tempfile
import unittest
from pathlib import Path

import nbformat

from scripts.create_evolved_notebook import (
    BASE_COMMIT,
    SOURCE_PATH,
    SOURCE_SHA256,
    create_evolved_notebook,
)
from scripts.validate_evolved_notebook import (
    NOTEBOOK_PATH,
    EvolvedNotebookValidationError,
    validate_evolved_notebook,
)
from tcc_evolution import BASE_RECONSTRUCTION_SHA256, EVOLUTION_SCHEMA_VERSION


class EvolutionFoundationTests(unittest.TestCase):
    def test_historical_reconstruction_matches_evolution_baseline(self) -> None:
        with SOURCE_PATH.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        self.assertEqual(digest, SOURCE_SHA256)
        self.assertEqual(BASE_RECONSTRUCTION_SHA256, SOURCE_SHA256)
        self.assertEqual(EVOLUTION_SCHEMA_VERSION, 1)

    def test_evolved_notebook_has_valid_provenance_and_saved_execution(self) -> None:
        summary = validate_evolved_notebook(NOTEBOOK_PATH)
        self.assertEqual(summary["derived_from_sha256"], SOURCE_SHA256)
        self.assertEqual(summary["code_cells"], summary["executed_code_cells"])
        self.assertEqual(summary["error_outputs"], 0)
        self.assertEqual(summary["unsafe_output_fragments"], 0)
        self.assertGreater(summary["saved_outputs"], 0)

    def test_evolved_validator_rejects_sensitive_output_text(self) -> None:
        notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
        unsafe = copy.deepcopy(notebook)
        code_cell = next(cell for cell in unsafe.cells if cell.cell_type == "code")
        code_cell.outputs.append(
            nbformat.v4.new_output("stream", name="stdout", text="/home/user/data.csv")
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsafe.ipynb"
            nbformat.write(unsafe, path)
            with self.assertRaisesRegex(
                EvolvedNotebookValidationError,
                "forbidden output fragment",
            ):
                validate_evolved_notebook(path)

    def test_derivation_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evolved.ipynb"
            create_evolved_notebook(output)
            notebook = nbformat.read(output, as_version=4)
            self.assertEqual(notebook.metadata.tcc_evolution.base_commit, BASE_COMMIT)
            self.assertEqual(
                notebook.metadata.tcc_evolution.derived_from_sha256,
                SOURCE_SHA256,
            )
            with self.assertRaises(FileExistsError):
                create_evolved_notebook(output)


if __name__ == "__main__":
    unittest.main()
