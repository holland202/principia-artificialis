"""TLM-006 deviation wrapper: run train_tok.py UNCHANGED, with F.scaled_dot_product_attention replaced by the plain
written-out causal attention from diag_tlm006.py. Reason: on the S25 (Termux aarch64, torch 2.11.0) the fused
attention diverges in training from step 1, while the plain version reproduces the server's losses to 4 decimals at
all 40 diagnostic steps (results/tiny_lm/006/diag/). On the server the two agree to 4 decimals. Same arguments as
train_tok.py. Claude (Anthropic, Opus 5.5), 2026-11-26.
Gate before trusting a run: step 500 must print within 0.01 of TLM-004's 4.844; otherwise stop it."""
import math, runpy, sys
import torch, torch.nn.functional as F


def plain_attn(q, k, v, is_causal=True, **_):
    t = q.shape[-2]
    w = (q @ k.transpose(-2, -1)) / math.sqrt(q.shape[-1])
    w = w.masked_fill(torch.triu(torch.ones(t, t, dtype=torch.bool), 1), float("-inf"))
    return torch.softmax(w, -1) @ v


F.scaled_dot_product_attention = plain_attn
print("attention: plain (deviation wrapper)", flush=True)
sys.argv = ["train_tok.py"] + sys.argv[1:]
runpy.run_path("train_tok.py", run_name="__main__")
