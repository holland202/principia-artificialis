"""Descriptive on-device measurement of tiny-engine-165k v3 (seed 12), no safetensors needed.
Usage (Termux): python bench_s25.py ~/tiny-engine-v3 ~/tiny-engine-space
Predictions written before any phone run (2026-11-20): D1 logits match the x86 PyTorch reference within 1e-4;
D2 the three demo answers are exactly right (38/38, 63/63, 127/127, as in the container); D3 a 127-token copy
generates in under 5 seconds. Claude (Anthropic, Opus 5.5). SELF-TESTED in a Linux container only."""
import json, os, platform, resource, sys, time
t0 = time.time()
sys.path.insert(0, os.path.expanduser(sys.argv[1]))
SP = os.path.expanduser(sys.argv[2])
import numpy as np
import torch
import engine as E
t_import = time.time() - t0

man = json.load(open(f"{SP}/weights.json"))
flat = np.fromfile(f"{SP}/weights.bin", dtype="<f4")
sd = {t["name"]: torch.from_numpy(flat[t["offset"]:t["offset"] + int(np.prod(t["shape"]))].reshape(t["shape"]).copy())
      for t in man["tensors"]}
m = E.TinyEngine(E.CFG3)
m.load_state_dict(sd)
m.eval()
print(f"device: {platform.machine()} | python {platform.python_version()} | torch {torch.__version__} | "
      f"threads {torch.get_num_threads()} | import {t_import:.2f}s | params {E.n_params(m)}")

# D1: parity with the x86 PyTorch reference shipped with the Space
worst = 0.0
with torch.no_grad():
    for r in json.load(open(f"{SP}/space_ref.json")):
        lg = m(torch.tensor([r["prompt"]]))[0].numpy()
        worst = max(worst, float(np.abs(lg - np.array(r["logits"])).max()))
print(f"D1 parity: max |logit diff| vs x86 reference = {worst:.2e} -> {'HELD' if worst < 1e-4 else 'FAILED'}")


@torch.no_grad()
def gen(prefix, n):
    x = torch.tensor([prefix])
    for _ in range(n):
        x = torch.cat([x, m(x)[:, -1:].argmax(-1)], 1)
    return x[0, len(prefix):].tolist()


rng = np.random.default_rng(3)
seg = rng.integers(1, 128, size=19).tolist()
ctx = [E.BOS] + [seg[i % 19] for i in range(900)]
want_p = [seg[(900 + i) % 19] for i in range(38)]
keys = rng.choice(np.arange(1, 64), 63, replace=False); vals = rng.integers(64, 128, size=63)
kv = [E.BOS] + [int(t) for k, v in zip(keys, vals) for t in (k, v)] + rng.integers(64, 128, size=700).tolist()
src = rng.choice(np.arange(1, 128), 127, replace=False).tolist()
res = []
t = time.time(); got = gen(ctx, 38); tp = time.time() - t
res.append(sum(a == b for a, b in zip(got, want_p)) == 38)
print(f"pattern p19 after 900 tokens: {sum(a == b for a, b in zip(got, want_p))}/38 in {tp:.2f}s")
right = 0; t = time.time()
with torch.no_grad():
    for k, v in zip(keys, vals):
        right += int(m(torch.tensor([kv + [E.QRY, int(k)]]))[0, -1].argmax()) == int(v)
tk = time.time() - t; res.append(right == 63)
print(f"look up 63 facts after 700 filler tokens: {right}/63 in {tk:.2f}s")
times = []
for _ in range(5):
    t = time.time(); got = gen([E.BOS] + src + [E.SEP], 127); times.append(time.time() - t)
ok = sum(a == b for a, b in zip(got, src)); res.append(ok == 127)
med = sorted(times)[2]
print(f"copy 127 tokens: {ok}/127, median of 5 = {med:.2f}s ({127 / med:.0f} tokens/s, no cache)")
print(f"D2 demo answers exact: {'HELD' if all(res) else 'FAILED'} | D3 copy under 5 s: {'HELD' if med < 5 else 'FAILED'}")
print(f"peak memory (max RSS): {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024:.0f} MB")
