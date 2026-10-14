"""EGR2 reserved-code validation; structural test only."""
import struct
import unittest
import zlib

import numpy as np

from egrr import quantize_symmetric
from storage import HEADER_SIZE, serialize, deserialize


class ReservedCodeTests(unittest.TestCase):
    def test_forged_valid_crc_rejects_reserved_minus_four(self):
        rng = np.random.default_rng(28)
        weights = rng.normal(size=(16, 8))
        q = quantize_symmetric(weights, 3)

        payload = bytearray(serialize(
            q,
            np.array([], dtype=np.int64),
            np.array([], dtype=np.float64),
        ))

        # Replace the first signed 3-bit code with binary 100 = -4.
        payload[HEADER_SIZE] = (
            (payload[HEADER_SIZE] & 0b11111000) | 0b00000100
        )

        # Forge a matching CRC32 so integrity checking alone passes.
        payload[-4:] = struct.pack(
            "<I", zlib.crc32(payload[:-4])
        )

        with self.assertRaisesRegex(
            ValueError, "invalid reserved quantization code"
        ):
            deserialize(bytes(payload))


if __name__ == "__main__":
    unittest.main()
