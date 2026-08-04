#!/usr/bin/env python3
"""Validate and prepare Lending Club data without exposing dataset rows."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tcc_reconstruction.data import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_RANDOM_SEED,
    DEFAULT_SAMPLE_SIZE,
    DataPipelineConfig,
    DataPipelineError,
    run_data_pipeline,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        type=Path,
        help="dataset path; otherwise use LENDING_CLUB_DATA_PATH or data/raw/",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help=(
            f"deterministic development sample size (default: {DEFAULT_SAMPLE_SIZE}); "
            "use 0 only to request a full in-memory result"
        ),
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED)
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument(
        "--include-unverified",
        action="store_true",
        help="retain income statuses beyond Verified and Source Verified",
    )
    parser.add_argument(
        "--allow-conversion-errors",
        action="store_true",
        help="record invalid non-null values as missing instead of failing",
    )
    parser.add_argument(
        "--hash-source",
        action="store_true",
        help="compute the complete dataset SHA-256 (slow for a multi-GB file)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sample_size = None if args.sample_size == 0 else args.sample_size
    try:
        result = run_data_pipeline(
            DataPipelineConfig(
                dataset_path=args.dataset,
                sample_size=sample_size,
                random_seed=args.seed,
                chunk_size=args.chunk_size,
                verified_only=not args.include_unverified,
                fail_on_conversion_errors=not args.allow_conversion_errors,
                include_source_hash=args.hash_source,
            )
        )
    except (DataPipelineError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(result.metadata_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
