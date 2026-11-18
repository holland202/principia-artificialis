"""DESCRIPTIVE, not registered: free-generation exact-match rate. The registered score checks each next token with the
true earlier tokens in place ("teacher-forced"). Here the model writes the whole answer itself, so one wrong token
can derail everything after it. Usage: python3 freegen.py WEIGHTS... (prints one line per model)."""
import sys

import numpy as np
import torch
from safetensors.torch import load_file

import engine as E

N = 50


@torch.no_grad()
def gen(m, prefix, n):
    x = torch.tensor(prefix)
    for _ in range(n):
        x = torch.cat([x, m(x)[:, -1:].argmax(-1)], 1)
    return x[:, -n:]


def run(path):
    m = E.TinyEngine(E.CFG2)
    m.load_state_dict(load_file(path))
    m.eval()
    rng = np.random.default_rng(7)
    out = {}
    # 1) pattern: held-out period, 300 tokens of context (2.3x the longest training input), write the next 2 periods
    for per in (7, 19):
        segs = [rng.integers(1, 128, size=per) for _ in range(N)]
        pre = [[E.BOS] + np.resize(s, 300).tolist() for s in segs]
        want = torch.tensor([np.resize(s, 300 + 2 * per)[300:].tolist() for s in segs])
        g = gen(m, pre, 2 * per)
        out[f"pattern_p{per}"] = float((g == want).all(1).float().mean())
    # 2) copy: write back a whole string of 63 (longest trained) or 127 tokens
    for k in (63, 127):
        ss = [rng.choice(np.arange(1, 128), k, replace=False) for _ in range(N)]
        g = gen(m, [[E.BOS] + s.tolist() + [E.SEP] for s in ss], k)
        out[f"copy_k{k}"] = float((g == torch.tensor(np.array(ss))).all(1).float().mean())
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        r = run(p)
        print(p.split("/")[-1], " ".join(f"{k}:{v:.2f}" for k, v in r.items()), flush=True)
