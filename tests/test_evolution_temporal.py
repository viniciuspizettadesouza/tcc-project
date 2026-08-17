from __future__ import annotations

import unittest

import pandas as pd

from tcc_evolution.temporal import (
    ALL_TERMS_MATURE_SPEC,
    TERM_36_SENSITIVITY_SPEC,
    TemporalBacktestSpec,
    build_temporal_partitions,
)


def temporal_fixture() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    rows = [
        ("2014-12", " 36 months", "Fully Paid", 0),
        ("2014-12", " 60 months", "Charged Off", 1),
        ("2015-02", " 60 months", "Fully Paid", 0),
        ("2015-03", " 36 months", "Default", 1),
        ("2015-04", " 60 months", "Fully Paid", 0),
        ("2015-09", " 60 months", "Charged Off", 1),
        ("2015-10", " 60 months", "Fully Paid", 0),
        ("2016-06", " 36 months", "Fully Paid", 0),
        ("2016-07", " 36 months", "Charged Off", 1),
        ("2017-01", " 36 months", "Fully Paid", 0),
        ("2017-09", " 36 months", "Default", 1),
        ("2017-10", " 36 months", "Fully Paid", 0),
        (None, " 36 months", "Fully Paid", 0),
        ("2014-01", None, "Fully Paid", 0),
        ("2014-02", " 36 months", "Current", 0),
    ]
    frame = pd.DataFrame(
        rows, columns=["issue_d", "term", "loan_status", "target"]
    )
    X = pd.DataFrame({"fico": range(600, 600 + len(frame))}, index=frame.index)
    y = frame.pop("target").astype("int8")
    return frame, X, y


class EvolutionTemporalTests(unittest.TestCase):
    def test_all_term_boundaries_are_inclusive_and_mature(self) -> None:
        frame, X, y = temporal_fixture()
        partitions = build_temporal_partitions(frame, X, y, ALL_TERMS_MATURE_SPEC)
        self.assertEqual(partitions.X_train.index.tolist(), [0, 1])
        self.assertEqual(partitions.X_calibration.index.tolist(), [2, 3])
        self.assertEqual(partitions.X_test.index.tolist(), [4, 5])
        self.assertEqual(
            partitions.population_summary["terms"].tolist(), ["36,60", "36,60", "60"]
        )
        counts = partitions.exclusion_summary.set_index("reason")["rows"]
        self.assertEqual(int(counts["not_mature_by_horizon"]), 2)
        self.assertEqual(int(counts.sum()), len(frame))

    def test_36_month_sensitivity_excludes_sixty_month_terms(self) -> None:
        frame, X, y = temporal_fixture()
        partitions = build_temporal_partitions(
            frame, X, y, TERM_36_SENSITIVITY_SPEC
        )
        self.assertEqual(partitions.X_train.index.tolist(), [0, 3])
        self.assertEqual(partitions.X_calibration.index.tolist(), [7, 8])
        self.assertEqual(partitions.X_test.index.tolist(), [9, 10])
        counts = partitions.exclusion_summary.set_index("reason")["rows"]
        self.assertEqual(int(counts["term_out_of_scope"]), 5)
        self.assertEqual(int(counts["not_mature_by_horizon"]), 1)

    def test_indexes_and_windows_must_be_valid(self) -> None:
        frame, X, y = temporal_fixture()
        with self.assertRaisesRegex(ValueError, "identical ordered indexes"):
            build_temporal_partitions(frame, X.iloc[::-1], y, ALL_TERMS_MATURE_SPEC)
        overlapping = TemporalBacktestSpec(
            name="overlap",
            allowed_terms=(36, 60),
            train_start="2014-01",
            train_end="2015-03",
            calibration_start="2015-03",
            calibration_end="2015-04",
            test_start="2015-04",
            test_end="2015-09",
        )
        with self.assertRaisesRegex(ValueError, "windows overlap"):
            build_temporal_partitions(frame, X, y, overlapping)

    def test_missing_columns_fail_before_partitioning(self) -> None:
        frame, X, y = temporal_fixture()
        with self.assertRaisesRegex(ValueError, "missing temporal columns"):
            build_temporal_partitions(
                frame.drop(columns="term"), X, y, ALL_TERMS_MATURE_SPEC
            )


if __name__ == "__main__":
    unittest.main()
