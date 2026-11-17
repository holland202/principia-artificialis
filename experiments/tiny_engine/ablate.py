"""EXPLORATION (C-EXPLORE), seed 900: periodic task only, 1500 steps, length 64; one factor per arm."""
import json, sys, time
import numpy as np, torch, torch.nn.functional as F
import engine as E
ARMS = {"rope_d256": dict(d_model=256), "rope_d128_untied": dict(tied=False),
        "learned_d256_untied": dict(d_model=256, pos="learned", tied=False), "rope_d256_untied": dict(d_model=256, tied=False)}
arm = sys.argv[1]
cfg = dict(E.CFG, **ARMS[arm])
torch.manual_seed(900); torch.set_num_threads(1); rng = np.random.default_rng(900)
m = E.TinyEngine(cfg); opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=0.0)
t = time.time(); tr = []
for step in range(1, 1501):
    x, mask = E.make_batch(rng, 64, 64, "periodic")
    loss = F.cross_entropy(m(x)[:, :-1].transpose(1, 2), x[:, 1:])
    opt.zero_grad(); loss.backward(); opt.step()
    if step % 250 == 0:
        m.eval(); tr.append(f"{step}:{E.accuracy(m, 'periodic', 64, 7, 128):.2f}"); m.train()
print(arm, E.n_params(m), f"{time.time()-t:.0f}s", " ".join(tr), flush=True)
