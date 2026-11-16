"""RMT-IH-001 part C: train the tiny transformer on repeating patterns of varying period, so that only real
in-context copying (induction) works. See REGISTRATION_C.md. Saves weights and a metrics trace per seed.
Written by Claude (Anthropic, Opus 5.5), 2026-11-16. SELF-TESTED only."""
import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

import explore_c as C
import explore_c2 as P
import tinyih as T

CFG_C = dict(T.CFG, lr=1e-3, steps=3000, every=50)


@torch.no_grad()
def evaluate(m):
    m.eval()
    out = {"acc_seen": P.copy_acc(m, P.SEEN, seed=5), "acc_heldout_period": P.copy_acc(m, P.HELD, seed=6),
           "acc_noise_unseen_dist": C.copy_acc(m, np.random.default_rng(7), True),
           "acc_noise_seen_dist": C.copy_acc(m, np.random.default_rng(8), False)}
    m.train()
    return out


def train(seed, cfg=CFG_C):
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    rng = np.random.default_rng(seed)
    m = T.TinyAttnOnly(cfg)
    opt = torch.optim.AdamW(m.parameters(), lr=cfg["lr"], weight_decay=0.0)
    rows = [{"step": 0, **T.spectral_stats(T.head_qk_levels(m))}]
    for step in range(1, cfg["steps"] + 1):
        x, _ = P.periodic(rng, cfg["batch"], P.SEEN)
        loss = F.cross_entropy(m(x)[:, :-1].transpose(1, 2), x[:, 1:])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % cfg["every"] == 0:
            rows.append({"step": step, "loss": float(loss), **T.spectral_stats(T.head_qk_levels(m))})
    return m, rows, evaluate(m)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    for s in a.seeds:
        t0 = time.time()
        m, rows, ev = train(s)
        torch.save(m.state_dict(), out / f"induction_seed{s}.pt")
        (out / f"partC_seed{s}.json").write_text(json.dumps({"cfg": CFG_C, "seed": s, "final": ev, "trace": rows}))
        print(f"seed {s}: {time.time() - t0:.0f}s", json.dumps({k: round(v, 3) for k, v in ev.items()}), flush=True)
