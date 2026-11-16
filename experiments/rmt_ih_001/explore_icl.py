"""EXPLORATION (C-EXPLORE), not confirmatory: choose the learning rate and checkpoint spacing so the induction jump
is late enough to time. Looks ONLY at the in-context-learning score, never at any spectral statistic. Seed 900 only;
registered seeds are disjoint."""
import sys
import numpy as np
import torch
import torch.nn.functional as F
import tinyih as T

for lr in map(float, sys.argv[1:]):
    cfg = dict(T.CFG, lr=lr)
    torch.manual_seed(900)
    rng = np.random.default_rng(900)
    m = T.TinyAttnOnly(cfg)
    opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=0.0)
    trace = []
    for step in range(1, 1201):
        x = T.batch(rng, "repeat", cfg)
        loss = F.cross_entropy(m(x)[:, :-1].transpose(1, 2), x[:, 1:])
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 20 == 0:
            trace.append((step, round(T.icl(m, "repeat", 900, cfg)["icl"], 2)))
    print(f"lr {lr}:", " ".join(f"{s}:{v}" for s, v in trace if s % 60 == 0), flush=True)
