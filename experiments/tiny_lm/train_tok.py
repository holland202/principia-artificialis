"""TLM-004: train a GPT on BPE-1024 tokens of the same train slice. Usage: python3 train_tok.py SEED STEPS OUT d L h
Same optimiser, batch (32 x 256 units), schedule and clipping as train.py; only the units change (tokens, not bytes).
Final score: eval_common.bpb on the common valid text. Claude (Anthropic, Opus 5.5), 2026-11-21. SELF-TESTED only."""
import json, math, os, sys, time
import numpy as np, torch, torch.nn.functional as F
from tokenizers import Tokenizer
from gpt import GPT, n_params
import eval_common as EC
torch.set_num_threads(int(os.environ.get("THREADS", "2")))
SEED, STEPS, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
d, L, h = (int(a) for a in sys.argv[4:7])
V, B, T, LR, WARM = 1024, 32, 256, 1e-3, 100
train = np.fromfile("data/train_tok1024.u16", dtype=np.uint16)
tk = Tokenizer.from_file("tok1024.json"); U = EC.units(tk)
torch.manual_seed(SEED); rng = np.random.default_rng(SEED)
m = GPT(d, L, h, V)
opt = torch.optim.AdamW(m.parameters(), LR, betas=(0.9, 0.95), weight_decay=0.1)
log = {"seed": SEED, "steps": STEPS, "d": d, "L": L, "h": h, "vocab": V, "params": n_params(m), "B": B, "T": T, "lr": LR,
       "curve": []}
t0 = time.time()
for step in range(1, STEPS + 1):
    lr = LR * min(1, step / WARM) * 0.5 * (1 + math.cos(math.pi * min(1, step / STEPS)))
    for g in opt.param_groups: g["lr"] = lr
    ix = rng.integers(0, len(train) - T - 1, size=B)
    x = torch.from_numpy(np.stack([train[i:i + T + 1] for i in ix]).astype(np.int64))
    loss = F.cross_entropy(m(x[:, :-1]).reshape(-1, V), x[:, 1:].reshape(-1))
    opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step()
    if step % 500 == 0 or step == STEPS:
        print(f"step {step} train_bits_per_token {loss.item()/math.log(2):.3f} {time.time()-t0:.0f}s", flush=True)
        log["curve"].append([step, round(loss.item() / math.log(2), 4)])
log["train_seconds"] = round(time.time() - t0); log["tokens_seen"] = STEPS * B * T
log["valid_bpb_common"], log["predicted_units"] = EC.bpb(m, U)
log["valid_bpb_common"] = round(log["valid_bpb_common"], 4)
print(f"valid bpb (common evaluator) {log['valid_bpb_common']}")
torch.save(m.state_dict(), OUT + ".pt"); json.dump(log, open(OUT + ".json", "w"), indent=1)
