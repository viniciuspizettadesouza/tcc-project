#!/usr/bin/env python3
"""Verify immutable reconstruction sources against the provenance manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = Path("provenance/source-manifest.json")
CHUNK_SIZE = 1024 * 1024


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(root: Path) -> dict[str, Any]:
    path = root / MANIFEST_PATH
    with path.open(encoding="utf-8") as source:
        manifest = json.load(source)

    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported source manifest schema")
    if manifest.get("algorithm") != "sha256":
        raise ValueError("unsupported source manifest algorithm")
    return manifest


def verify(root: Path) -> list[str]:
    manifest = load_manifest(root)
    failures: list[str] = []

    for source in manifest["sources"]:
        relative_path = Path(source["path"])
        path = root / relative_path
        if not path.is_file():
            failures.append(f"missing source: {relative_path}")
            continue

        actual_size = path.stat().st_size
        if actual_size != source["size_bytes"]:
            failures.append(
                f"size mismatch: {relative_path} "
                f"(expected {source['size_bytes']}, got {actual_size})"
            )

        actual_hash = sha256(path)
        if actual_hash != source["sha256"]:
            failures.append(
                f"SHA-256 mismatch: {relative_path} "
                f"(expected {source['sha256']}, got {actual_hash})"
            )
        elif actual_size == source["size_bytes"]:
            print(f"OK  {relative_path}  {actual_hash}")

    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="repository root (defaults to the parent of this script directory)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        failures = verify(args.root.resolve())
    except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR  could not verify source manifest: {error}")
        return 1

    if failures:
        for failure in failures:
            print(f"ERROR  {failure}")
        return 1

    print("Source integrity verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
