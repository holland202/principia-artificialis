"""EXPLORATION for TINY-ENGINE-002 (C-EXPLORE), seed 900 only. Arms change one thing each; scores use engine.evaluate."""
import json, sys, time
import torch
import engine as E
ARMS = {"nope_l1": dict(nope_layers=(1,)), "partial_rope": dict(rope_frac=0.5)}
arm = sys.argv[1]
torch.set_num_threads(1)
t = time.time()
m = E.train(900, dict(E.CFG, **ARMS[arm]))
print(arm, f"{time.time()-t:.0f}s", json.dumps({k: round(v, 3) for k, v in E.evaluate(m).items()}), flush=True)
