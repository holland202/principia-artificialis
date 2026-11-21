"""Find which op differs on the S25's torch build. Usage: python diag_s25.py ~/tiny-engine-v3 ~/tiny-engine-space
Each line compares a torch op with a plain NumPy (float64) computation of the same thing.
Claude (Anthropic, Opus 5.5), 2026-11-20. SELF-TESTED in a Linux container only."""
import json, os, sys
sys.path.insert(0, os.path.expanduser(sys.argv[1])); SP = os.path.expanduser(sys.argv[2])
import numpy as np, torch, torch.nn.functional as F
import engine as E
torch.manual_seed(0); rng = np.random.default_rng(0)
def d(a, b): return float(np.abs(np.asarray(a, np.float64) - np.asarray(b, np.float64)).max())
A = rng.standard_normal((64, 128)).astype(np.float32); W = rng.standard_normal((128, 128)).astype(np.float32)
print(f"matmul (linear)       {d(F.linear(torch.from_numpy(A), torch.from_numpy(W)).numpy(), A.astype(np.float64) @ W.T.astype(np.float64)):.1e}")
x = torch.from_numpy(A); ln = torch.nn.LayerNorm(128)
mu = A.mean(1, keepdims=True); var = A.var(1, keepdims=True)
print(f"layernorm             {d(ln(x).detach().numpy(), (A - mu) / np.sqrt(var + 1e-5)):.1e}")
t = torch.arange(1100, dtype=torch.float32)
print(f"sin/cos (angle<=1100) {max(d(t.sin().numpy(), np.sin(np.arange(1100.))), d(t.cos().numpy(), np.cos(np.arange(1100.)))):.1e}")
q, k, v = (torch.from_numpy(rng.standard_normal((1, 2, 200, 64)).astype(np.float32)) for _ in range(3))
s = q.double() @ k.double().transpose(-1, -2) / 8.0
s = s.masked_fill(torch.ones(200, 200, dtype=torch.bool).triu(1), float("-inf")).softmax(-1) @ v.double()
print(f"sdpa causal (t=200)   {d(F.scaled_dot_product_attention(q, k, v, is_causal=True).numpy(), s.numpy()):.1e}")
q2, k2, v2 = (z[:, :, :5] for z in (q, k, v))
s2 = (q2.double() @ k2.double().transpose(-1, -2) / 8.0).masked_fill(torch.ones(5, 5, dtype=torch.bool).triu(1), float("-inf")).softmax(-1) @ v2.double()
print(f"sdpa causal (t=5)     {d(F.scaled_dot_product_attention(q2, k2, v2, is_causal=True).numpy(), s2.numpy()):.1e}")

man = json.load(open(f"{SP}/weights.json")); flat = np.fromfile(f"{SP}/weights.bin", dtype="<f4")
sd = {t["name"]: torch.from_numpy(flat[t["offset"]:t["offset"] + int(np.prod(t["shape"]))].reshape(t["shape"]).copy()) for t in man["tensors"]}
ref = json.load(open(f"{SP}/space_ref.json"))
def parity(label):
    m = E.TinyEngine(E.CFG3); m.load_state_dict(sd); m.eval(); w = 0.0
    with torch.no_grad():
        for r in ref: w = max(w, d(m(torch.tensor([r["prompt"]]))[0].numpy(), np.array(r["logits"])))
    print(f"model parity, {label:28s} {w:.1e}")
parity(f"default ({torch.get_num_threads()} threads)")
n = torch.get_num_threads(); torch.set_num_threads(1); parity("1 thread"); torch.set_num_threads(n)
def manual(q, k, v, is_causal=True):
    t = q.shape[-2]; s = (q @ k.transpose(-1, -2)) / q.shape[-1] ** 0.5
    return s.masked_fill(torch.ones(t, t, dtype=torch.bool).triu(1), float("-inf")).softmax(-1) @ v
F.scaled_dot_product_attention = manual
parity("manual attention (no SDPA)")
