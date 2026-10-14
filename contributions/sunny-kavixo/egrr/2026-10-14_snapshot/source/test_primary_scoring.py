"""Primary ratio numerical safety tests; no confirmatory data."""
import unittest

from primary_scoring import (
    PrimaryScoringError,
    paired_relative_improvement,
)


class PrimaryScoringTests(unittest.TestCase):
    def test_valid_positive_improvement(self):
        self.assertAlmostEqual(
            paired_relative_improvement(0.8, 1.0), 0.2
        )

    def test_valid_negative_improvement(self):
        self.assertAlmostEqual(
            paired_relative_improvement(1.2, 1.0), -0.2
        )

    def test_zero_baseline_rejected(self):
        with self.assertRaisesRegex(
            PrimaryScoringError, "zero or near-zero"
        ):
            paired_relative_improvement(0.1, 0.0)

    def test_near_zero_baseline_rejected(self):
        with self.assertRaises(PrimaryScoringError):
            paired_relative_improvement(0.1, 1e-13)

    def test_nonfinite_mse_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaises(PrimaryScoringError):
                    paired_relative_improvement(value, 1.0)
                with self.assertRaises(PrimaryScoringError):
                    paired_relative_improvement(1.0, value)

    def test_negative_mse_rejected(self):
        with self.assertRaises(PrimaryScoringError):
            paired_relative_improvement(-0.1, 1.0)
        with self.assertRaises(PrimaryScoringError):
            paired_relative_improvement(0.1, -1.0)

    def test_ratio_overflow_rejected(self):
        with self.assertRaisesRegex(
            PrimaryScoringError, "non-finite improvement ratio"
        ):
            paired_relative_improvement(1e308, 1e-11)

    def test_invalid_type_rejected(self):
        with self.assertRaises(PrimaryScoringError):
            paired_relative_improvement("invalid", 1.0)


if __name__ == "__main__":
    unittest.main()
