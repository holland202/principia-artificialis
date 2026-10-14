"""Covariance numerical safety tests; no held-out research data."""
import unittest
import numpy as np

from egrr import Quantized, quantize_symmetric
from covariance_float16 import select_covariance_float16


class CovarianceSafetyTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(28)
        self.w = rng.normal(size=(4, 3))
        self.x = rng.normal(size=(8, 4))
        self.q = quantize_symmetric(self.w, 3)

    def test_normal_selection(self):
        idx, values = select_covariance_float16(
            self.w, self.q, 3, self.x
        )
        self.assertEqual(len(idx), 3)
        self.assertTrue(np.all(np.isfinite(values)))

    def test_nonfinite_calibration_rejected(self):
        x = self.x.copy()
        x[0, 0] = np.nan
        with self.assertRaisesRegex(ValueError, "non-finite calibration"):
            select_covariance_float16(self.w, self.q, 3, x)

    def test_covariance_overflow_rejected(self):
        x = np.full((8, 4), 1e200)
        with self.assertRaisesRegex(ValueError, "non-finite covariance"):
            select_covariance_float16(self.w, self.q, 3, x)

    def test_float16_correction_overflow_rejected(self):
        w = np.array([[100000.0, 0.0], [0.0, 0.0]])
        q = Quantized(np.zeros((2, 2), dtype=np.int16), 1.0, 3)
        with self.assertRaisesRegex(ValueError, "float16 correction overflow"):
            select_covariance_float16(w, q, 1, np.eye(2))

    def test_gain_overflow_rejected(self):
        # Covariance remains finite; gain products overflow float64.
        w = np.full((4, 3), 60000.0)
        q = Quantized(
            np.zeros((4, 3), dtype=np.int16), 1.0, 3
        )
        x = np.full((8, 4), 1e150)
        with self.assertRaisesRegex(ValueError, "non-finite gain"):
            select_covariance_float16(w, q, 1, x)


if __name__ == "__main__":
    unittest.main()
