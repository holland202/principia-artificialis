"""EGRR phase-1 reference scaffold. Not a preregistered research experiment."""
from dataclasses import dataclass
import math
import numpy as np


@dataclass(frozen=True)
class Quantized:
    values: np.ndarray
    scale: float
    bits: int


def quantize_symmetric(weights: np.ndarray, bits: int) -> Quantized:
    w = np.asarray(weights, dtype=np.float64)
    if w.ndim != 2 or not np.all(np.isfinite(w)):
        raise ValueError('weights must be a finite 2D array')
    if bits < 2 or bits > 8:
        raise ValueError('bits must be between 2 and 8')
    qmax = 2 ** (bits - 1) - 1
    scale = float(np.max(np.abs(w))) / qmax if np.any(w) else 1.0
    values = np.rint(w / scale).clip(-qmax, qmax).astype(np.int16)
    return Quantized(values, scale, bits)


def dequantize(q: Quantized) -> np.ndarray:
    return q.values.astype(np.float64) * q.scale


def select_corrections(weights: np.ndarray, q: Quantized, k: int, method: str,
                       calibration: np.ndarray | None = None, seed: int = 0):
    w = np.asarray(weights, dtype=np.float64)
    if w.shape != q.values.shape:
        raise ValueError('quantizer shape mismatch')
    if not 0 <= k <= w.size:
        raise ValueError('invalid correction count')
    if method not in {'magnitude', 'sensitivity', 'random', 'none'}:
        raise ValueError('unknown method')
    residual = w - dequantize(q)
    if method == 'none' or k == 0:
        return np.array([], dtype=np.int64), np.array([], dtype=np.float64)
    if method == 'sensitivity':
        if calibration is None:
            raise ValueError('calibration data required')
        x = np.asarray(calibration, dtype=np.float64)
        if x.ndim != 2 or x.shape[1] != w.shape[0] or not len(x) or not np.all(np.isfinite(x)):
            raise ValueError('calibration must be finite [samples, input_features]')
        # A candidate heuristic, NOT a validated model importance score.
        input_rms = np.sqrt(np.mean(x * x, axis=0))
        scores = np.abs(residual) * input_rms[:, None]
    elif method == 'magnitude':
        scores = np.abs(residual)
    else:
        indices = np.sort(np.random.default_rng(seed).choice(w.size, k, replace=False))
        return indices.astype(np.int64), residual.ravel()[indices]
    # Stable tie break by flattened weight index; avoids score-dependent nondeterminism.
    indices = np.argsort(-scores.ravel(), kind='stable')[:k]
    return np.sort(indices).astype(np.int64), residual.ravel()[np.sort(indices)]


def reconstruct(q: Quantized, indices: np.ndarray, residual_values: np.ndarray) -> np.ndarray:
    flat = dequantize(q).ravel().copy()
    if len(indices) != len(residual_values):
        raise ValueError('length mismatch')
    if len(np.unique(indices)) != len(indices) or np.any(indices < 0) or np.any(indices >= flat.size):
        raise ValueError('invalid indices')
    flat[indices] += residual_values
    return flat.reshape(q.values.shape)


def modeled_bits(q: Quantized, k: int, correction_bits: int = 16, scale_bits: int = 32) -> int:
    """Idealized bit-accounting model, not measured storage or runtime RAM."""
    n = q.values.size
    index_bits = math.ceil(math.log2(n)) if n > 1 else 0
    return n * q.bits + scale_bits + k * (index_bits + correction_bits)


def heldout_mse(weights: np.ndarray, approx: np.ndarray, inputs: np.ndarray) -> float:
    x = np.asarray(inputs, dtype=np.float64)
    if x.ndim != 2 or x.shape[1] != weights.shape[0] or not np.all(np.isfinite(x)):
        raise ValueError('invalid held-out inputs')
    target = x @ weights
    output = x @ approx
    return float(np.mean((target - output) ** 2))
