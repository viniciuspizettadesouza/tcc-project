#!/usr/bin/env python3
"""Reexecute the reconstructed notebook only through a disposable copy."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile

try:
    from scripts.create_evolved_notebook import SOURCE_PATH, SOURCE_SHA256, sha256
except ModuleNotFoundError:  # Support direct execution from the scripts directory.
    from create_evolved_notebook import (  # type: ignore[no-redef]
        SOURCE_PATH,
        SOURCE_SHA256,
        sha256,
    )
from tcc_reconstruction.data import DATA_PATH_ENV


def main() -> int:
    dataset = os.environ.get(DATA_PATH_ENV)
    if not dataset:
        print(f"ERROR  {DATA_PATH_ENV} is required")
        return 2
    dataset_path = Path(dataset).resolve()
    if not dataset_path.is_file():
        print(f"ERROR  dataset not found: {dataset_path}")
        return 2
    if sha256(SOURCE_PATH) != SOURCE_SHA256:
        print("ERROR  immutable reconstructed notebook does not match its baseline")
        return 1

    with tempfile.TemporaryDirectory(prefix="tcc-reconstructed-") as temporary:
        disposable = Path(temporary) / SOURCE_PATH.name
        shutil.copy2(SOURCE_PATH, disposable)
        environment = os.environ.copy()
        environment[DATA_PATH_ENV] = str(dataset_path)
        result = subprocess.run(
            [
                os.sys.executable,
                "-m",
                "jupyter",
                "nbconvert",
                "--to",
                "notebook",
                "--execute",
                "--inplace",
                str(disposable),
                "--ExecutePreprocessor.timeout=1800",
            ],
            check=False,
            env=environment,
        )
        if result.returncode:
            return result.returncode
        print("Historical reconstruction executed successfully in a disposable copy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
