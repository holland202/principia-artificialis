"""Anti-vacuity for bits per byte: the same model on the same 65,537 valid bytes in a fixed random order (seed 0).
A model that has learned the text's structure must do far worse on shuffled bytes. Usage: python3 shufcheck.py RUN_PREFIX
Claude (Anthropic, Opus 5.5), 2026-11-21. SELF-TESTED only."""
import json, sys
import numpy as np, torch
from gpt import GPT
from train_eval import bpb
m = GPT(128, 5, 4); m.load_state_dict(torch.load(sys.argv[1] + ".pt", weights_only=True))
v = np.fromfile("data/v2_valid.txt", dtype=np.uint8)[:65537]
s = v[np.random.default_rng(0).permutation(len(v))]
print(json.dumps({"valid_bpb": round(bpb(m, v), 4), "shuffled_valid_bpb": round(bpb(m, s), 4)}))
