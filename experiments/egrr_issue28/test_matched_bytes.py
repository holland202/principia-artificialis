"""Structural EGR2 regression checks; not a held-out hypothesis test."""
import unittest
import numpy as np

from egrr import quantize_symmetric, select_corrections, reconstruct
from covariance_float16 import select_covariance_float16
from storage import serialize, deserialize


class MatchedByteTests(unittest.TestCase):
    def test_four_arm_serialized_size_and_reconstruction(self):
        rng = np.random.default_rng(28)
        weights = rng.normal(size=(64, 32))
        calibration = rng.normal(size=(256, 64))
        quantized = quantize_symmetric(weights, 3)
        sizes = {}

        for method in ("magnitude", "sensitivity", "random", "covariance"):
            with self.subTest(method=method):
                if method == "covariance":
                    indices, corrections = select_covariance_float16(
                        weights, quantized, 128, calibration
                    )
                else:
                    indices, corrections = select_corrections(
                        weights, quantized, 128, method,
                        calibration=calibration, seed=28,
                    )

                payload = serialize(quantized, indices, corrections)
                decoded_q, decoded_indices, decoded_values = deserialize(payload)

                np.testing.assert_array_equal(decoded_indices, indices)
                expected = reconstruct(
                    quantized, indices,
                    np.asarray(corrections, dtype=np.float16).astype(np.float64),
                )
                actual = reconstruct(
                    decoded_q, decoded_indices, decoded_values
                )
                np.testing.assert_array_equal(actual, expected)

                sizes[method] = len(payload)
                self.assertEqual(len(payload), 1311)

        self.assertEqual(len(set(sizes.values())), 1)


if __name__ == "__main__":
    unittest.main()
