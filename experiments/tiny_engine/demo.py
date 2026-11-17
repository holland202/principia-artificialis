"""Try the tiny in-context engine. Usage: python3 demo.py weights/engine_seed1.safetensors
Shows the three skills on fresh random inputs, including inputs longer than any it trained on."""
import sys

import numpy as np
import torch
from safetensors.torch import load_file

import engine as E


def greedy(m, prefix, n):
    x = torch.tensor([prefix])
    with torch.no_grad():
        for _ in range(n):
            x = torch.cat([x, m(x)[:, -1:].argmax(-1)], 1)
    return x[0, len(prefix):].tolist()


m = E.TinyEngine()
m.load_state_dict(load_file(sys.argv[1] if len(sys.argv) > 1 else "weights/engine_seed1.safetensors"))
m.eval()
rng = np.random.default_rng(2026)
print(f"TinyEngine, {E.n_params(m):,} parameters\n")

seg = rng.integers(1, 128, size=11).tolist()                     # period 11 was never trained on
prefix = [E.BOS] + (seg * 30)[:300]                              # 300 tokens: longer than any training input
out = greedy(m, prefix, 22)
want = (seg * 40)[300:322]
print("1) continue a pattern of period 11 (never trained), after 300 tokens of context")
print("   model :", out); print("   truth :", want, "->", "OK" if out == want else "DIFF")

keys = rng.choice(np.arange(1, 64), 40, replace=False); vals = rng.choice(np.arange(64, 128), 40)
ctx = [E.BOS] + [int(t) for kv in zip(keys, vals) for t in kv]
hits = 0
for j in range(40):
    hits += greedy(m, ctx + [E.QRY, int(keys[j])], 1)[0] == int(vals[j])
print(f"\n2) look up 40 values from 40 key-value pairs given earlier: {hits}/40 correct")

s = rng.choice(np.arange(1, 128), 50, replace=False).tolist()
out = greedy(m, [E.BOS] + s + [E.SEP], 50)
print(f"\n3) copy a 50-token string exactly: {sum(a == b for a, b in zip(out, s))}/50 tokens correct")
