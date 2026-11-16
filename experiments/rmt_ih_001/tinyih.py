"""RMT-IH-001: a tiny attention-only transformer trained from scratch on an induction task, with the QK spectrum
measured at every checkpoint. See REGISTRATION.md. No pretrained weights are used.

Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-16. SELF-TESTED only.
"""
import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "rmt_037"))
from rmt037 import ratios, qk_levels  # noqa: E402  (the same statistic RMT-037 used)

CFG = dict(vocab=64, seg=32, d_model=256, n_heads=2, n_layers=2, batch=64, lr=3e-5, steps=2000, every=20)


# ---------------------------------------------------------------- data
def batch(rng, arm, cfg=CFG):
    """BOS + segment A + segment B. arm 'repeat': B = A (induction possible). arm 'norepeat': B independent."""
    v, s, n = cfg["vocab"], cfg["seg"], cfg["batch"]
    a = rng.integers(1, v, size=(n, s))
    b = a.copy() if arm == "repeat" else rng.integers(1, v, size=(n, s))
    x = np.concatenate([np.zeros((n, 1), int), a, b], axis=1)
    return torch.from_numpy(x).long()


# ---------------------------------------------------------------- model
class Attn(nn.Module):
    def __init__(self, d, h):
        super().__init__()
        self.h, self.dh = h, d // h
        self.q, self.k, self.v, self.o = (nn.Linear(d, d, bias=False) for _ in range(4))

    def forward(self, x):
        b, t, d = x.shape
        sh = lambda z: z.view(b, t, self.h, self.dh).transpose(1, 2)
        y = F.scaled_dot_product_attention(sh(self.q(x)), sh(self.k(x)), sh(self.v(x)), is_causal=True)
        return self.o(y.transpose(1, 2).reshape(b, t, d))


class TinyAttnOnly(nn.Module):
    """Token + position embedding, n_layers of pre-LayerNorm attention with residuals, no MLPs, unembedding."""

    def __init__(self, cfg=CFG):
        super().__init__()
        d, t = cfg["d_model"], 2 * cfg["seg"] + 1
        self.emb, self.pos = nn.Embedding(cfg["vocab"], d), nn.Embedding(t, d)
        self.lns = nn.ModuleList(nn.LayerNorm(d) for _ in range(cfg["n_layers"]))
        self.attn = nn.ModuleList(Attn(d, cfg["n_heads"]) for _ in range(cfg["n_layers"]))
        self.lnf, self.out = nn.LayerNorm(d), nn.Linear(d, cfg["vocab"], bias=False)

    def forward(self, x):
        h = self.emb(x) + self.pos(torch.arange(x.shape[1]))
        for ln, at in zip(self.lns, self.attn):
            h = h + at(ln(h))
        return self.out(self.lnf(h))


# ---------------------------------------------------------------- measurements
def head_qk_levels(model, cfg=CFG):
    """Per layer, per head: singular values of W_Q,h W_K,h^T (d_model x d_model, rank d_head), via thin QR."""
    dh = cfg["d_model"] // cfg["n_heads"]
    out = []
    for li, at in enumerate(model.attn):
        wq = at.q.weight.detach().double().numpy().T  # d_model x d_model, columns = output features
        wk = at.k.weight.detach().double().numpy().T
        for h in range(cfg["n_heads"]):
            out.append((li, h, qk_levels(wq[:, h * dh:(h + 1) * dh], wk[:, h * dh:(h + 1) * dh])))
    return out


def spectral_stats(levels_list):
    """Pooled edge <r~> (top 10% of each head's levels), plus the rivals: mean normalised top singular value
    (sigma_max / mean sigma) and mean stable rank (sum s^2 / s_max^2), all over every head."""
    edge, top, srank = [], [], []
    for _, _, lv in levels_list:
        lv = np.sort(lv)
        r, _ = ratios(lv[int(0.9 * len(lv)):])
        edge.extend(r.tolist())
        top.append(lv[-1] / lv.mean())
        srank.append(float((lv ** 2).sum() / lv[-1] ** 2))
    return {"edge_r": float(np.mean(edge)), "edge_n": len(edge), "top_norm": float(np.mean(top)),
            "stable_rank": float(np.mean(srank))}


@torch.no_grad()
def icl(model, arm, seed, cfg=CFG):
    """Held-out loss on segment A positions vs segment B positions; ICL score = loss_A - loss_B."""
    x = batch(np.random.default_rng(10_000 + seed), arm, dict(cfg, batch=256))
    lp = F.cross_entropy(model(x)[:, :-1].transpose(1, 2), x[:, 1:], reduction="none").mean(0)
    s = cfg["seg"]
    la, lb = float(lp[1:s].mean()), float(lp[s + 1:2 * s].mean())   # predict A[1..], B[1..]
    return {"loss_A": la, "loss_B": lb, "icl": la - lb}


# ---------------------------------------------------------------- run
def train(seed, arm, cfg=CFG, log=print):
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    rng = np.random.default_rng(seed)
    model = TinyAttnOnly(cfg)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=0.0)
    rows = []

    def record(step):
        row = {"step": step, **icl(model, arm, seed, cfg), **spectral_stats(head_qk_levels(model, cfg))}
        rows.append(row)
        return row

    record(0)
    for step in range(1, cfg["steps"] + 1):
        x = batch(rng, arm, cfg)
        loss = F.cross_entropy(model(x)[:, :-1].transpose(1, 2), x[:, 1:])
        opt.zero_grad()
        loss.backward()
        opt.step()
        if step % cfg["every"] == 0:
            r = record(step)
            if step % (cfg["every"] * 10) == 0:
                log(f"  seed {seed} {arm} step {step}: icl {r['icl']:.3f}")
    return model, rows


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", required=True)
    ap.add_argument("--arms", nargs="+", default=["repeat", "norepeat"])
    ap.add_argument("--steps", type=int, default=CFG["steps"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--save-model", default=None, help="directory: save final state_dict per seed/arm")
    a = ap.parse_args()
    cfg = dict(CFG, steps=a.steps)
    out = {"cfg": cfg, "torch": torch.__version__, "numpy": np.__version__, "runs": {}}
    for seed in a.seeds:
        for arm in a.arms:
            t0 = time.time()
            model, rows = train(seed, arm, cfg)
            out["runs"][f"{arm}/{seed}"] = rows
            print(f"seed {seed} {arm}: {time.time() - t0:.0f}s, final icl {rows[-1]['icl']:.3f}", flush=True)
            if a.save_model:
                Path(a.save_model).mkdir(parents=True, exist_ok=True)
                torch.save(model.state_dict(), Path(a.save_model) / f"{arm}_seed{seed}.pt")
    out["digest"] = digest(out["runs"])
    Path(a.out).write_text(json.dumps(out))
    print("DIGEST", out["digest"])
