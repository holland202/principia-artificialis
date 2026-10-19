"""Scoring safety regression tests; no confirmatory data."""
import unittest
import numpy as np

from egrr import heldout_mse


class ScoringSafetyTests(unittest.TestCase):
    def test_valid_zero_error(self):
        w = np.eye(2)
        self.assertEqual(heldout_mse(w, w.copy(), np.eye(2)), 0.0)

    def test_empty_evaluation_rejected(self):
        with self.assertRaisesRegex(ValueError, "empty evaluation"):
            heldout_mse(np.eye(2), np.zeros((2, 2)), np.empty((0, 2)))

    def test_nonfinite_inputs_rejected(self):
        for value in (np.nan, np.inf, -np.inf):
            with self.subTest(value=value):
                x = np.eye(2)
                x[0, 0] = value
                with self.assertRaises(ValueError):
                    heldout_mse(np.eye(2), np.zeros((2, 2)), x)

    def test_nonfinite_reconstruction_rejected(self):
        a = np.eye(2)
        a[0, 0] = np.nan
        with self.assertRaises(ValueError):
            heldout_mse(np.eye(2), a, np.eye(2))

    def test_overflow_rejected(self):
        with self.assertRaises(ValueError):
            heldout_mse(
                np.full((2, 2), 1e308),
                np.zeros((2, 2)),
                np.full((2, 2), 1e308),
            )

    def test_underflow_rejected(self):
        with self.assertRaises(ValueError):
            heldout_mse(
                np.full((2, 2), 1e-200),
                np.zeros((2, 2)),
                np.eye(2),
            )


if __name__ == "__main__":
    unittest.main()
