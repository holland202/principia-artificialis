"""EGRR experimental binary storage. Not a performance result."""
import io
import struct
import zlib
import numpy as np
from egrr import Quantized
from packing import pack_signed, unpack_signed

MAGIC = b"EGR2"
VERSION = 1
HEADER = "<4sBBBII d I"
HEADER_SIZE = struct.calcsize(HEADER)


def _serialize_unchecked(q, indices, residuals):
    idx = np.asarray(indices, dtype=np.int64)
    val = np.asarray(residuals, dtype=np.float64)

    if q.values.ndim != 2:
        raise ValueError("2D weights required")
    rows, cols = q.values.shape
    n = rows * cols

    if idx.ndim != 1 or val.ndim != 1 or len(idx) != len(val):
        raise ValueError("invalid corrections")
    if np.any(idx < 0) or np.any(idx >= n):
        raise ValueError("invalid correction index")
    if len(np.unique(idx)) != len(idx):
        raise ValueError("duplicate correction index")
    if not np.all(np.isfinite(val)):
        raise ValueError("non-finite residual")

    packed = pack_signed(q.values, q.bits)
    index_width = 2 if n <= 65536 else 4 if n <= 2**32 else 8
    index_dtype = {2: "<u2", 4: "<u4", 8: "<u8"}[index_width]

    residual16 = val.astype("<f2")
    if not np.all(np.isfinite(residual16)):
        raise ValueError("residual overflows float16")

    header = struct.pack(
        HEADER, MAGIC, VERSION, q.bits, index_width,
        rows, cols, float(q.scale), len(idx)
    )
    return (
        header
        + packed
        + idx.astype(index_dtype).tobytes()
        + residual16.tobytes()
    )


def _deserialize_unchecked(payload):
    if len(payload) < HEADER_SIZE:
        raise ValueError("truncated header")
    magic, version, bits, width, rows, cols, scale, k = struct.unpack(
        HEADER, payload[:HEADER_SIZE]
    )
    if magic != MAGIC or version != VERSION or not 2 <= bits <= 8:
        raise ValueError("invalid format")
    if width not in (2, 4, 8) or not rows or not cols:
        raise ValueError("invalid metadata")
    n = rows * cols
    if k > n:
        raise ValueError("invalid correction count")
    expected_width = 2 if n <= 65536 else 4 if n <= 2**32 else 8
    if width != expected_width:
        raise ValueError("invalid index width")
    packed_length = (n * bits + 7) // 8
    expected = HEADER_SIZE + packed_length + k * (width + 2)
    if len(payload) != expected:
        raise ValueError("payload length mismatch")

    offset = HEADER_SIZE
    values = unpack_signed(
        payload[offset:offset + packed_length], bits, (rows, cols)
    )
    offset += packed_length

    index_dtype = {2: "<u2", 4: "<u4", 8: "<u8"}[width]
    indices = np.frombuffer(
        payload, dtype=index_dtype, count=k, offset=offset
    ).astype(np.int64)
    offset += k * width

    residuals = np.frombuffer(
        payload, dtype="<f2", count=k, offset=offset
    ).astype(np.float64)

    if len(np.unique(indices)) != k or np.any(indices >= n):
        raise ValueError("corrupt correction indices")
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("invalid scale")
    if not np.all(np.isfinite(residuals)):
        raise ValueError("invalid residual values")

    return Quantized(values, scale, bits), indices, residuals


def serialize(q, indices, residuals):
    """Store payload with CRC32; experimental EGRR container."""
    data = _serialize_unchecked(q, indices, residuals)
    checksum = zlib.crc32(data)
    return data + struct.pack("<I", checksum)


def deserialize(payload):
    """Reject accidental byte corruption before decoding."""
    if len(payload) < HEADER_SIZE + 4:
        raise ValueError("truncated checksummed payload")
    data = payload[:-4]
    stored_checksum = struct.unpack("<I", payload[-4:])[0]
    if zlib.crc32(data) != stored_checksum:
        raise ValueError("CRC32 checksum mismatch")
    return _deserialize_unchecked(data)
