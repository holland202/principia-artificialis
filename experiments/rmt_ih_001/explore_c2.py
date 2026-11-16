"""EXPLORATION for part C, attempt 2 (C-EXPLORE). Seed 900. Copying accuracy only, no spectral statistics.
Data 'periodic': BOS + a random segment of length L repeated to fill 64 tokens, so most positions are predictable by
looking back L tokens. L is drawn from 6..24 in training except the held-out set {9, 13, 17, 21}. A fixed-offset
shortcut cannot work (L varies); only content-based copying (induction) generalises to the held-out L."""
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

import tinyih as T

HELD = (9, 13, 17, 21)
SEEN = tuple(L for L in range(6, 25) if L not in HELD)


def periodic(rng, n, lengths, cfg=T.CFG):
    t, v = 2 * cfg["seg"] + 1, cfg["vocab"]
    x = np.zeros((n, t), int)
    mask = np.zeros((n, t), bool)
    for i in range(n):
        L = int(rng.choice(lengths))
        seg = rng.integers(1, v, size=L)
        body = np.resize(seg, t - 1)
        x[i, 1:] = body
        mask[i, 1 + L:] = True                # positions predictable by copying from L back
    return torch.from_numpy(x).long(), torch.from_numpy(mask)


@torch.no_grad()
def copy_acc(m, lengths, seed=5):
    x, mask = periodic(np.random.default_rng(seed), 512, lengths)
    pred = m(x)[:, :-1].argmax(-1)
    return float((pred == x[:, 1:])[mask[:, 1:]].float().mean())


if __name__ == "__main__":
    for lr in map(float, sys.argv[1:]):
        cfg = dict(T.CFG, lr=lr)
        torch.manual_seed(900)
        rng = np.random.default_rng(900)
        m = T.TinyAttnOnly(cfg)
        opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=0.0)
        t0, trace = time.time(), []
        for step in range(1, 3001):
            x, _ = periodic(rng, cfg["batch"], SEEN)
            loss = F.cross_entropy(m(x)[:, :-1].transpose(1, 2), x[:, 1:])
            opt.zero_grad(); loss.backward(); opt.step()
            if step % 250 == 0:
                trace.append(f"{step}:{copy_acc(m, SEEN):.2f}/{copy_acc(m, HELD):.2f}")
        print(f"lr {lr} ({time.time() - t0:.0f}s) step:seen/held-out ->", " ".join(trace), flush=True)
        torch.save(m.state_dict(), f"/root/explore_c2_lr{lr}.pt")
