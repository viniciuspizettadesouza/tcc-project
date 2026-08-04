from __future__ import annotations

import csv
import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tcc_reconstruction.data import (
    REQUIRED_COLUMNS,
    DataConversionError,
    DataPipelineConfig,
    DatasetPathError,
    SchemaValidationError,
    build_dataset_manifest,
    inspect_schema,
    resolve_dataset_path,
    run_data_pipeline,
    validate_schema,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def base_row(identifier: int) -> dict[str, object]:
    row: dict[str, object] = {column: 1.0 for column in REQUIRED_COLUMNS}
    row.update(
        {
            "id": str(identifier),
            "term": "36 months",
            "int_rate": "10.65%",
            "grade": "B",
            "sub_grade": "B2",
            "emp_length": "10+ years",
            "home_ownership": "MORTGAGE",
            "verification_status": "Verified",
            "issue_d": "Dec-2011",
            "loan_status": "Fully Paid",
            "purpose": "debt_consolidation",
            "addr_state": "CA",
            "earliest_cr_line": "Jan-1985",
            "initial_list_status": "f",
            "application_type": "Individual",
            "fico_range_low": 700,
            "fico_range_high": 704,
        }
    )
    return row


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    columns = sorted(REQUIRED_COLUMNS)
    with path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_gzip_csv(path: Path, rows: list[dict[str, object]]) -> None:
    columns = sorted(REQUIRED_COLUMNS)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


class DatasetPathTests(unittest.TestCase):
    def test_resolution_precedence_and_default_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            default_directory = root / "data" / "raw"
            default_directory.mkdir(parents=True)
            default_path = default_directory / "default.csv"
            environment_path = root / "environment.csv"
            explicit_path = root / "explicit.csv"
            for path in (default_path, environment_path, explicit_path):
                path.write_text("id\n", encoding="utf-8")

            self.assertEqual(
                resolve_dataset_path(repository_root=root, environ={}),
                default_path.resolve(),
            )
            self.assertEqual(
                resolve_dataset_path(
                    environ={"LENDING_CLUB_DATA_PATH": str(environment_path)},
                    repository_root=root,
                ),
                environment_path.resolve(),
            )
            self.assertEqual(
                resolve_dataset_path(
                    explicit_path,
                    environ={"LENDING_CLUB_DATA_PATH": str(environment_path)},
                    repository_root=root,
                ),
                explicit_path.resolve(),
            )

    def test_missing_and_ambiguous_defaults_fail_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            with self.assertRaisesRegex(DatasetPathError, "dataset not found"):
                resolve_dataset_path(repository_root=root, environ={})

            default_directory = root / "data" / "raw"
            default_directory.mkdir(parents=True)
            (default_directory / "first.csv").write_text("id\n", encoding="utf-8")
            (default_directory / "second.csv").write_text("id\n", encoding="utf-8")
            with self.assertRaisesRegex(DatasetPathError, "multiple dataset files"):
                resolve_dataset_path(repository_root=root, environ={})


class SchemaAndManifestTests(unittest.TestCase):
    def test_schema_validation_lists_all_missing_columns(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "incomplete.csv"
            path.write_text("id,loan_status\n1,Fully Paid\n", encoding="utf-8")
            columns = inspect_schema(path)
            with self.assertRaises(SchemaValidationError) as context:
                validate_schema(columns)
            self.assertIn("fico_range_low", str(context.exception))
            self.assertIn("verification_status", str(context.exception))

    def test_manifest_records_metadata_and_optional_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "fixture.csv"
            write_csv(path, [base_row(1)])
            expected_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest = build_dataset_manifest(path, include_sha256=True)
            self.assertEqual(manifest["file_name"], "fixture.csv")
            self.assertEqual(manifest["sha256"], expected_hash)
            self.assertEqual(manifest["column_count"], len(REQUIRED_COLUMNS))
            self.assertNotIn(str(path.parent), str(manifest))


class DataPipelineTests(unittest.TestCase):
    def test_gzip_input_used_by_recovered_notebook_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "fixture.gzip"
            write_gzip_csv(path, [base_row(1)])
            result = run_data_pipeline(
                DataPipelineConfig(dataset_path=path, sample_size=None)
            )
            self.assertEqual(result.data["id"].astype("string").tolist(), ["1"])

    def test_plain_csv_with_gzip_suffix_used_by_real_dataset_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "fixture.gzip"
            write_csv(path, [base_row(1)])
            result = run_data_pipeline(
                DataPipelineConfig(dataset_path=path, sample_size=None)
            )
            self.assertEqual(result.data["id"].astype("string").tolist(), ["1"])

    def test_filters_converts_and_summarizes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "fixture.csv"
            rows = [
                base_row(1),
                {
                    **base_row(2),
                    "loan_status": "Charged Off",
                    "verification_status": "Source Verified",
                    "int_rate": "15.27",
                    "issue_d": "Jan-2012",
                    "fico_range_low": 680,
                    "fico_range_high": 684,
                },
                {
                    **base_row(3),
                    "loan_status": "Default",
                    "verification_status": "Not Verified",
                },
                {**base_row(4), "loan_status": "Current"},
                {**base_row(5), "verification_status": "Not Verified"},
            ]
            write_csv(path, rows)

            result = run_data_pipeline(
                DataPipelineConfig(dataset_path=path, sample_size=None, chunk_size=2)
            )

            self.assertEqual(result.data["id"].astype("string").tolist(), ["1", "2"])
            self.assertEqual(result.data["int_rate"].tolist(), [10.65, 15.27])
            self.assertEqual(result.data["year"].tolist(), [2011, 2012])
            self.assertEqual(result.data["fico"].tolist(), [702.0, 682.0])
            self.assertEqual(result.summary.rows_read, 5)
            self.assertEqual(result.summary.rows_after_status_filter, 4)
            self.assertEqual(result.summary.rows_after_verification_filter, 2)
            self.assertEqual(result.summary.rows_output, 2)
            self.assertEqual(result.summary.minimum_issue_year, 2011)
            self.assertEqual(result.summary.maximum_issue_year, 2012)
            self.assertEqual(result.summary.source_minimum_issue_month, "2011-12")
            self.assertEqual(result.summary.source_maximum_issue_month, "2012-01")
            self.assertEqual(result.summary.status_counts["Current"], 1)
            self.assertEqual(
                result.summary.verification_counts_after_status_filter["Not Verified"],
                2,
            )

    def test_unverified_rows_can_be_retained_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "fixture.csv"
            rows = [
                base_row(1),
                {
                    **base_row(2),
                    "loan_status": "Default",
                    "verification_status": "Not Verified",
                },
            ]
            write_csv(path, rows)
            result = run_data_pipeline(
                DataPipelineConfig(
                    dataset_path=path,
                    sample_size=None,
                    verified_only=False,
                )
            )
            self.assertEqual(len(result.data), 2)

    def test_deterministic_sample_does_not_depend_on_chunk_size(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "fixture.csv"
            write_csv(path, [base_row(identifier) for identifier in range(100)])

            first = run_data_pipeline(
                DataPipelineConfig(
                    dataset_path=path,
                    sample_size=10,
                    random_seed=17,
                    chunk_size=7,
                )
            )
            second = run_data_pipeline(
                DataPipelineConfig(
                    dataset_path=path,
                    sample_size=10,
                    random_seed=17,
                    chunk_size=13,
                )
            )
            different_seed = run_data_pipeline(
                DataPipelineConfig(
                    dataset_path=path,
                    sample_size=10,
                    random_seed=18,
                    chunk_size=13,
                )
            )

            first_ids = first.data["id"].astype("string").tolist()
            second_ids = second.data["id"].astype("string").tolist()
            different_ids = different_seed.data["id"].astype("string").tolist()
            self.assertEqual(first_ids, second_ids)
            self.assertNotEqual(first_ids, different_ids)
            self.assertEqual(first.summary.rows_read, 100)
            self.assertEqual(first.summary.rows_output, 10)
            self.assertTrue(first.summary.to_dict()["sampling"]["applied"])

    def test_conversion_errors_fail_or_are_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "fixture.csv"
            write_csv(
                path,
                [
                    {
                        **base_row(1),
                        "int_rate": "not-a-rate",
                        "issue_d": "not-a-date",
                        "fico_range_low": "not-a-score",
                    }
                ],
            )

            with self.assertRaisesRegex(DataConversionError, "int_rate=1"):
                run_data_pipeline(DataPipelineConfig(dataset_path=path))

            result = run_data_pipeline(
                DataPipelineConfig(
                    dataset_path=path,
                    fail_on_conversion_errors=False,
                    sample_size=None,
                )
            )
            self.assertEqual(result.summary.invalid_interest_rate_values, 1)
            self.assertEqual(result.summary.invalid_issue_date_values, 1)
            self.assertEqual(result.summary.invalid_fico_bound_values, 1)
            self.assertTrue(result.data["int_rate"].isna().all())
            self.assertTrue(result.data["year"].isna().all())
            self.assertTrue(result.data["fico"].isna().all())

    def test_configuration_rejects_non_positive_sizes(self) -> None:
        with self.assertRaisesRegex(ValueError, "sample_size"):
            DataPipelineConfig(sample_size=0)
        with self.assertRaisesRegex(ValueError, "chunk_size"):
            DataPipelineConfig(chunk_size=0)


class CommandLineTests(unittest.TestCase):
    def test_cli_emits_metadata_without_dataset_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "fixture.csv"
            write_csv(path, [base_row(1), base_row(2)])
            completed = subprocess.run(
                [
                    sys.executable,
                    str(REPOSITORY_ROOT / "scripts" / "prepare_dataset.py"),
                    "--dataset",
                    str(path),
                    "--sample-size",
                    "1",
                    "--chunk-size",
                    "1",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            output = json.loads(completed.stdout)
            self.assertEqual(output["summary"]["rows"]["read"], 2)
            self.assertEqual(output["summary"]["rows"]["output"], 1)
            self.assertNotIn(str(path.parent), completed.stdout)
            self.assertNotIn("debt_consolidation", completed.stdout)


if __name__ == "__main__":
    unittest.main()
