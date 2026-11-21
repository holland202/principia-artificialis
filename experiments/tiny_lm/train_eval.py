"""bits-per-byte evaluator shared by train.py and shufcheck.py."""
import math
import numpy as np, torch, torch.nn.functional as F

def bpb(m, data, n_windows=256, T=256):
    """Bits per byte on fixed non-overlapping windows from the start of `data` (deterministic)."""
    m.eval(); tot, cnt = 0.0, 0
    with torch.no_grad():
        for i in range(0, n_windows, 32):
            x = torch.from_numpy(np.stack([data[(i + j) * T:(i + j) * T + T + 1] for j in range(32)]).astype(np.int64))
            tot += F.cross_entropy(m(x[:, :-1]).reshape(-1, 256), x[:, 1:].reshape(-1), reduction="sum").item(); cnt += x[:, 1:].numel()
    m.train(); return tot / cnt / math.log(2)

