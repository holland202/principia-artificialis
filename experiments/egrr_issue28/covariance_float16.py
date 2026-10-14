"""Exploratory float16-aware covariance residual selection.

Calibration-only method. Not a validated compression improvement.
"""
import numpy as np
from egrr import dequantize


def select_covariance_float16(weights, q, k, calibration):
    w = np.asarray(weights, dtype=np.float64)
    x = np.asarray(calibration, dtype=np.float64)

    if w.ndim != 2 or not np.all(np.isfinite(w)):
        raise ValueError("weights must be finite and 2D")
    if w.shape != q.values.shape:
        raise ValueError("quantizer shape mismatch")
    if not isinstance(k, (int, np.integer)) or not 0 <= k <= w.size:
        raise ValueError("invalid correction count")
    if x.ndim != 2 or x.shape[0] == 0 or x.shape[1] != w.shape[0]:
        raise ValueError("invalid calibration shape")
    if not np.all(np.isfinite(x)):
        raise ValueError("non-finite calibration")

    residual = w - dequantize(q)

    with np.errstate(over="ignore", invalid="ignore"):
        correction = residual.astype(np.float16).astype(np.float64)

    if not np.all(np.isfinite(correction)):
        raise ValueError("float16 correction overflow")

    covariance = x.T @ x / len(x)
    remaining = residual.copy()
    selected = np.zeros(w.shape, dtype=bool)
    diagonal = np.diag(covariance)[:, None]

    for _ in range(k):
        interaction = covariance @ remaining
        gains = 2 * correction * interaction - diagonal * correction**2
        gains[selected] = -np.inf

        flat_index = int(np.argmax(gains))
        row, col = np.unravel_index(flat_index, w.shape)

        remaining[row, col] -= correction[row, col]
        selected[row, col] = True

    indices = np.flatnonzero(selected).astype(np.int64)
    values = correction.ravel()[indices]
    return indices, values
