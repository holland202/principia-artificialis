"""TLM-006 diagnostic (not part of the frozen experiment): why did train_tok.py diverge on the S25 (step 500 at
8.069 bits/token vs TLM-004's 4.844, then nan by step 1000) with the pinned data and tokenizer?
Claude (Anthropic, Opus 5.5), 2026-11-26. Imports gpt.py unchanged; changes no frozen file.

Part A compares PyTorch's fused attention (F.scaled_dot_product_attention, causal) with a plain written-out version
on fixed random inputs: forward outputs and the gradient they send back.
Part B replays train_tok.py's first N steps exactly (seed 41, same batches, optimiser, schedule, clipping), printing
the loss every step, once with the fused attention and once with the plain version.

Registered before the device run (the server reference was run first and is committed beside this file):
  D1: on the S25, Part A's forward max|diff| exceeds 1e-3 OR some output is non-finite, while the server stays under 1e-5.
  D2: on the S25, Part B with --attn plain tracks the server's losses within 0.05 bits at every step,
      while --attn sdpa drifts away from them.
  D0 (control, must hold or nothing above means anything): the server's sdpa and plain runs agree within 0.01 bits
      at every step, and step-1 loss is within 0.05 of log2(1024) = 10 on both machines.
Deviation, recorded before the device run: D0's second clause is REFUTED on the server and kept: step-1 loss is
  154.1691 bits, not ~10, because the tied embedding starts at N(0,1) and the first logits are large. TLM-004's own
  curve starts there too. D0's first clause held: sdpa and plain agree to 4 decimals at all 40 steps.
Server reference (diag_server.txt, diag_server_500.txt): torch 2.11.0+cpu on x86_64 reaches 4.8444 bits/token at
  step 500, TLM-004's logged 4.844, so the torch version alone does not explain the S25 divergence.
Usage: THREADS=2 python diag_tlm006.py [--steps N] [--only sdpa|plain]
"""
import math, os, platform, sys, time
import numpy as np, torch, torch.nn.functional as F
from gpt import GPT

torch.set_num_threads(int(os.environ.get("THREADS", "2")))
STEPS = int(sys.argv[sys.argv.index("--steps") + 1]) if "--steps" in sys.argv else 40
V, B, T, LR, WARM, TOTAL = 1024, 32, 256, 1e-3, 100, 6250   # train_tok.py's constants; TOTAL sets the cosine schedule
SDPA = F.scaled_dot_product_attention


def plain_attn(q, k, v, is_causal=True, **_):
    t = q.shape[-2]
    w = (q @ k.transpose(-2, -1)) / math.sqrt(q.shape[-1])
    w = w.masked_fill(torch.triu(torch.ones(t, t, dtype=torch.bool), 1), float("-inf"))
    return torch.softmax(w, -1) @ v


print(f"env python={sys.version.split()[0]} torch={torch.__version__} numpy={np.__version__} "
      f"machine={platform.machine()} threads={torch.get_num_threads()}")

# Part A
g = torch.Generator().manual_seed(0)
q, k, v = (torch.randn(2, 4, 256, 30, generator=g, requires_grad=True) for _ in range(3))
y1 = SDPA(q, k, v, is_causal=True); y2 = plain_attn(q, k, v)
gr = torch.randn(y1.shape, generator=g)
g1 = torch.autograd.grad(y1, (q, k, v), gr); g2 = torch.autograd.grad(y2, (q, k, v), gr)
print(f"A forward max|sdpa-plain| = {(y1 - y2).abs().max().item():.3e}  finite sdpa={bool(torch.isfinite(y1).all())}")
print("A grad    max|sdpa-plain| q,k,v = " + ", ".join(f"{(a - b).abs().max().item():.3e}" for a, b in zip(g1, g2)))

# Part B
train = np.fromfile("data/train_tok1024.u16", dtype=np.uint16)
MODES = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else ["sdpa", "plain"]
for mode in MODES:
    F.scaled_dot_product_attention = SDPA if mode == "sdpa" else plain_attn
    torch.manual_seed(41); rng = np.random.default_rng(41)
    m = GPT(120, 5, 4, V)
    opt = torch.optim.AdamW(m.parameters(), LR, betas=(0.9, 0.95), weight_decay=0.1)
    t0, line = time.time(), []
    for step in range(1, STEPS + 1):
        lr = LR * min(1, step / WARM) * 0.5 * (1 + math.cos(math.pi * min(1, step / TOTAL)))
        for pg in opt.param_groups: pg["lr"] = lr
        ix = rng.integers(0, len(train) - T - 1, size=B)
        x = torch.from_numpy(np.stack([train[i:i + T + 1] for i in ix]).astype(np.int64))
        loss = F.cross_entropy(m(x[:, :-1]).reshape(-1, V), x[:, 1:].reshape(-1))
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step()
        line.append(f"{loss.item() / math.log(2):.4f}")
    print(f"B {mode:5s} {time.time() - t0:.0f}s bits/token by step: " + " ".join(line))
F.scaled_dot_product_attention = SDPA
