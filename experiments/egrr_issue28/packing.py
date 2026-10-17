"""EGRR experimental bit-packing. No compression claims."""
import numpy as np


def pack_signed(values, bits):
    if not 2 <= bits <= 8:
        raise ValueError("bits must be 2..8")
    a = np.asarray(values)
    if not np.issubdtype(a.dtype, np.integer):
        raise ValueError("integer values required")
    lo, hi = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
    if np.any(a < lo) or np.any(a > hi):
        raise ValueError("value out of range")
    flat = a.ravel()
    out = bytearray((flat.size * bits + 7) // 8)
    mask = (1 << bits) - 1
    for i, val in enumerate(flat):
        v = int(val) & mask
        offset = i * bits
        byte, shift = divmod(offset, 8)
        out[byte] |= (v << shift) & 255
        if shift + bits > 8:
            out[byte + 1] |= v >> (8 - shift)
    return bytes(out)


def unpack_signed(payload, bits, shape):
    if not 2 <= bits <= 8:
        raise ValueError("bits must be 2..8")
    count = int(np.prod(shape))
    if len(payload) != (count * bits + 7) // 8:
        raise ValueError("payload length mismatch")
    values = np.empty(count, dtype=np.int16)
    mask = (1 << bits) - 1
    for i in range(count):
        offset = i * bits
        byte, shift = divmod(offset, 8)
        word = payload[byte] >> shift
        if shift + bits > 8:
            word |= payload[byte + 1] << (8 - shift)
        v = word & mask
        values[i] = v - (1 << bits) if v & (1 << (bits - 1)) else v
    return values.reshape(shape)
