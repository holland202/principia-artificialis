"""TLM-001: train a byte-level GPT on a TinyStories V2 slice. Usage: python3 train.py SEED STEPS OUT_PREFIX [d L h]
Claude (Anthropic, Opus 5.5), 2026-11-21. SELF-TESTED only."""
import json, math, sys, time
import numpy as np, torch, torch.nn.functional as F
from gpt import GPT, n_params
import os; torch.set_num_threads(int(os.environ.get("THREADS", "2")))
SEED, STEPS, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
d, L, h = (int(a) for a in sys.argv[4:7]) if len(sys.argv) > 6 else (128, 5, 4)
B, T, LR, WARM = 32, 256, 1e-3, 100
train = np.memmap("data/v2_train_200MB.txt", dtype=np.uint8, mode="r")
valid = np.fromfile("data/v2_valid.txt", dtype=np.uint8)

def bpb(m, data, n_windows=256, T=256):
    """Bits per byte on fixed non-overlapping windows from the start of `data` (deterministic)."""
    m.eval(); tot, cnt = 0.0, 0
    with torch.no_grad():
        for i in range(0, n_windows, 32):
            x = torch.from_numpy(np.stack([data[(i + j) * T:(i + j) * T + T + 1] for j in range(32)]).astype(np.int64))
            tot += F.cross_entropy(m(x[:, :-1]).reshape(-1, 256), x[:, 1:].reshape(-1), reduction="sum").item(); cnt += x[:, 1:].numel()
    m.train(); return tot / cnt / math.log(2)

torch.manual_seed(SEED); rng = np.random.default_rng(SEED)
m = GPT(d, L, h)
opt = torch.optim.AdamW(m.parameters(), LR, betas=(0.9, 0.95), weight_decay=0.1)
log = {"seed": SEED, "steps": STEPS, "d": d, "L": L, "h": h, "params": n_params(m), "B": B, "T": T, "lr": LR,
       "untrained_valid_bpb": bpb(m, valid), "curve": []}
t0 = time.time()
for step in range(1, STEPS + 1):
    lr = LR * min(1, step / WARM) * 0.5 * (1 + math.cos(math.pi * min(1, step / STEPS)))
    for g in opt.param_groups: g["lr"] = lr
    ix = rng.integers(0, len(train) - T - 1, size=B)
    x = torch.from_numpy(np.stack([train[i:i + T + 1] for i in ix]).astype(np.int64))
    loss = F.cross_entropy(m(x[:, :-1]).reshape(-1, 256), x[:, 1:].reshape(-1))
    opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step()
    if step % 250 == 0 or step == STEPS:
        v = bpb(m, valid); log["curve"].append([step, round(loss.item() / math.log(2), 4), round(v, 4)])
        print(f"step {step} train_bpb {loss.item()/math.log(2):.3f} valid_bpb {v:.4f} {time.time()-t0:.0f}s", flush=True)
log["train_seconds"] = round(time.time() - t0); log["valid_bpb"] = log["curve"][-1][2]
log["tokens_seen"] = STEPS * B * T
torch.save(m.state_dict(), OUT + ".pt"); json.dump(log, open(OUT + ".json", "w"), indent=1)
