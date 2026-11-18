"""Confirmatory run for REGISTRATION_002.md: train TINY-ENGINE-002 (CFG2) seeds; save weights and scores (resumable).
Usage: python3 run2.py OUTDIR SEED [SEED ...]"""
import json, sys, time
from pathlib import Path
import torch
from safetensors.torch import save_file
import engine as E
torch.set_num_threads(1)
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
for s in map(int, sys.argv[2:]):
    if (out / f"seed{s}.json").exists():
        continue
    t = time.time()
    m = E.train(s, E.CFG2)
    r = E.evaluate(m)
    save_file({k: v.contiguous() for k, v in m.state_dict().items()}, out / f"engine2_seed{s}.safetensors")
    (out / f"seed{s}.json").write_text(json.dumps({"seed": s, "cfg": E.CFG2, "params": E.n_params(m), "scores": r,
                                                   "train_seconds": round(time.time() - t)}))
    print(f"seed {s}: {round(time.time()-t)}s", json.dumps({k: round(v, 3) for k, v in r.items()}), flush=True)
