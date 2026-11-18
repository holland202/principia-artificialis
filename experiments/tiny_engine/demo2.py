"""Try TINY-ENGINE-002. Usage: python3 demo2.py weights/engine2_seed1.safetensors
Every test below uses inputs longer than anything the model trained on (its longest training input was 128 tokens)."""
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


m = E.TinyEngine(E.CFG2)
m.load_state_dict(load_file(sys.argv[1] if len(sys.argv) > 1 else "weights/engine2_seed1.safetensors"))
m.eval()
rng = np.random.default_rng(2026)
print(f"TinyEngine-002, {E.n_params(m):,} parameters. Longest training input: 128 tokens.\n")

seg = rng.integers(1, 128, size=19).tolist()                    # period 19 was never trained on
prefix = [E.BOS] + (seg * 60)[:900]                              # 900 tokens of context: 7x the longest training input
out = greedy(m, prefix, 38)
want = (seg * 60)[900:938]
print(f"1) continue a pattern of period 19 (never trained) after 900 tokens: "
      f"{sum(a == b for a, b in zip(out, want))}/38 tokens correct")

keys = rng.choice(np.arange(1, 64), 63, replace=False)
vals = rng.choice(np.arange(64, 128), 63)
ctx = [E.BOS] + [int(t) for kv in zip(keys, vals) for t in kv]
# 700 unrelated tokens between the facts and the questions. They are drawn from the value range only, so no key
# appears again in the filler. (The first version drew filler from all tokens; every key then reappeared next to a
# random token, the question had no single right answer, and the model scored 4-5/63. See RESULTS_002.md.)
filler = rng.integers(64, 128, size=700).tolist()
hits = sum(greedy(m, ctx + filler + [E.QRY, int(keys[j])], 1)[0] == int(vals[j]) for j in range(63))
print(f"\n2) learn 63 key->value facts, read 700 unrelated tokens, then answer all 63: {hits}/63 correct "
      f"(context ~830 tokens)")

s = rng.choice(np.arange(1, 128), 127, replace=False).tolist()  # 127 tokens: twice the longest trained copy
out = greedy(m, [E.BOS] + s + [E.SEP], 127)
print(f"\n3) copy a 127-token string exactly (2x the longest trained): {sum(a == b for a, b in zip(out, s))}/127 correct")
