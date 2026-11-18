"""DESCRIPTIVE, not registered (2026-11-17, from Codex's review in PR #163): free-running evaluation of existing
weights, no retraining. The model writes the whole answer itself (greedy). For each test:
  whole  = share of answers exactly right end to end
  tok    = share of generated tokens equal to the truth at the same position (free-running, errors can cascade)
  first  = median position (1-based) of the first wrong token, over answers that had an error ("-" if none did)
Usage: python3 freegen2.py v1|v2 WEIGHTS..."""
import sys

import numpy as np
import torch
from safetensors.torch import load_file

import engine as E

N = 100


@torch.no_grad()
def gen(m, prefix, n):
    x = torch.tensor(prefix)
    for _ in range(n):
        x = torch.cat([x, m(x)[:, -1:].argmax(-1)], 1)
    return x[:, -n:]


def stats(g, want):
    ok = g == want
    whole = float(ok.all(1).float().mean())
    tok = float(ok.float().mean())
    bad = ~ok.all(1)
    first = "-" if not bad.any() else f"{int(np.median((~ok[bad]).float().argmax(1).numpy() + 1))}"
    return f"whole {whole:.2f} tok {tok:.3f} first {first}"


def run(cfg, path):
    m = E.TinyEngine(cfg)
    m.load_state_dict(load_file(path))
    m.eval()
    rng = np.random.default_rng(11)
    out = []
    for per in (7, 19):                                  # never-trained periods, 300 tokens of context
        segs = [rng.integers(1, 128, size=per) for _ in range(N)]
        g = gen(m, [[E.BOS] + np.resize(s, 300).tolist() for s in segs], 2 * per)
        want = torch.tensor([np.resize(s, 300 + 2 * per)[300:].tolist() for s in segs])
        out.append(f"pattern p{per}: {stats(g, want)}")
    for k in (63, 127):                                  # 63 = longest trained copy, 127 = 2x
        ss = [rng.choice(np.arange(1, 128), k, replace=False) for _ in range(N)]
        g = gen(m, [[E.BOS] + s.tolist() + [E.SEP] for s in ss], k)
        out.append(f"copy k{k}: {stats(g, torch.tensor(np.array(ss)))}")
    return out


if __name__ == "__main__":
    cfg = {"v1": E.CFG, "v2": E.CFG2}[sys.argv[1]]
    for p in sys.argv[2:]:
        print(sys.argv[1], p.split("/")[-1], " | ".join(run(cfg, p)), flush=True)
