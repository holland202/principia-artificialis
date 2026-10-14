"""EGRR structural anti-vacuity gate. No held-out quality experiment."""
import argparse
import sys
from pathlib import Path

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--sabotage", action="store_true")
args = parser.parse_args()

# Import the versioned reference modules beside this script.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from egrr import quantize_symmetric, select_corrections, reconstruct
from storage import HEADER_SIZE, serialize, deserialize

rng = np.random.default_rng(28)
w = rng.normal(size=(16, 8))
q = quantize_symmetric(w, 3)
idx, residuals = select_corrections(w, q, 8, "magnitude")
payload = bytearray(serialize(q, idx, residuals))

if args.sabotage:
    payload[HEADER_SIZE] ^= 1

try:
    q2, idx2, values2 = deserialize(bytes(payload))
    if args.sabotage:
        print("GATE: FAIL — corrupted payload accepted")
        sys.exit(1)

    expected = reconstruct(
        q, idx, residuals.astype(np.float16).astype(np.float64)
    )
    actual = reconstruct(q2, idx2, values2)

    if not np.array_equal(expected, actual):
        print("GATE: FAIL — reconstruction mismatch")
        sys.exit(1)

    print("GATE: PASS — benign payload")
    sys.exit(0)

except ValueError as exc:
    if args.sabotage and "CRC32 checksum mismatch" in str(exc):
        print("GATE: FAIL — planted corruption detected")
        sys.exit(1)

    print(f"GATE: FAIL — unexpected error: {exc}")
    sys.exit(1)
