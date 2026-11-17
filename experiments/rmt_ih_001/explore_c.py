"""EXPLORATION for part C (C-EXPLORE), not confirmatory. Seed 900 only. Looks ONLY at copying accuracy, never at any
spectral statistic. Question: with the repeat at varying offsets, does the tiny model learn content-based copying
(induction) that works at offsets it never saw, and how long does it take?

Data 'varrepeat': BOS + random tokens (64 total), with a segment of length L in [8, 16] placed at a random start and
copied again after a random gap, so the copy distance varies. Offsets (L + gap) seen in training: 10..40 except a
held-out set {17, 23, 29, 35}; generalisation is tested on exactly the held-out offsets."""
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

import tinyih as T

HELD = {17, 23, 29, 35}


def varbatch(rng, n, held_only=False, cfg=T.CFG):
    t, v = 2 * cfg["seg"] + 1, cfg["vocab"]
    x = rng.integers(1, v, size=(n, t))
    x[:, 0] = 0
    mask = np.zeros((n, t), bool)            # positions whose token is predictable by copying (second copy, after its first)
    offs = np.zeros(n, int)
    for i in range(n):
        while True:
            L = int(rng.integers(8, 17))
            off = int(rng.integers(max(L, 10), 41))
            if (off in HELD) == held_only:
                break
        s = int(rng.integers(1, t - off - L + 1))
        x[i, s + off:s + off + L] = x[i, s:s + L]
        mask[i, s + off + 1:s + off + L] = True
        offs[i] = off
    return torch.from_numpy(x).long(), torch.from_numpy(mask)


@torch.no_grad()
def copy_acc(m, rng, held_only):
    x, mask = varbatch(rng, 512, held_only)
    pred = m(x)[:, :-1].argmax(-1)
    ok = (pred == x[:, 1:])[mask[:, 1:]]
    return float(ok.float().mean())


if __name__ == "__main__":
    for lr in map(float, sys.argv[1:]):
        cfg = dict(T.CFG, lr=lr)
        torch.manual_seed(900)
        rng = np.random.default_rng(900)
        m = T.TinyAttnOnly(cfg)
        opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=0.0)
        t0, trace = time.time(), []
        for step in range(1, 4001):
            x, _ = varbatch(rng, cfg["batch"])
            loss = F.cross_entropy(m(x)[:, :-1].transpose(1, 2), x[:, 1:])
            opt.zero_grad(); loss.backward(); opt.step()
            if step % 250 == 0:
                e = np.random.default_rng(5)
                trace.append(f"{step}:{copy_acc(m, e, False):.2f}/{copy_acc(m, e, True):.2f}")
        print(f"lr {lr} ({time.time() - t0:.0f}s) step:seen/held-out copy acc ->", " ".join(trace), flush=True)
