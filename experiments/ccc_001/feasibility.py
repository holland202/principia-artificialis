"""CCC-001 feasibility counts (C-FEAS). Prints counts only: no model decisions, no probabilities.

Usage: python3 experiments/ccc_001/feasibility.py
"""
import hashlib
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import torch  # noqa: E402

from common import MODEL_DIR, load, n_tokens, option_ids, render, weather_filler  # noqa: E402
from probes import ITEMS, OPTIONS  # noqa: E402

keys = [k for k, _, _ in ITEMS]
print("items", len(ITEMS), {o: keys.count(o) for o in OPTIONS})
print("chance S floor 0.3333; chance G under uniform 0.3333")
w = os.path.join(MODEL_DIR, "model.safetensors")
h = hashlib.sha256(open(w, "rb").read()).hexdigest()
print("weights_sha256", h)
tok, model = load()
print("params", sum(p.numel() for p in model.parameters()))
print("option_token_ids", option_ids(tok))
for n in (16, 64):
    ctx = weather_filler(n)
    print(f"weather_filler_{n}_turns_tokens", n_tokens(tok, ctx))
ids = tok(render(tok, weather_filler(64), gen=False), return_tensors="pt", add_special_tokens=False).input_ids
t = time.time()
with torch.no_grad():
    model(ids)
print("prefill_seconds_64_turn_filler", round(time.time() - t, 1), "threads", torch.get_num_threads())
print("torch", torch.__version__)
