"""Confirmatory run for REGISTRATION_004.md. Usage: python3 run4.py OUTDIR ARM SEED [SEED ...]; ARM A (CFG3),
B (CFG4B, answer label) or C (CFG4C, label + position coupling). Fresh case seeds: eval3 offset 30000.
Writes OUTDIR/ARM/seedN.json and weights; resumable. Claude (Anthropic, Opus 5.5), 2026-11-20. SELF-TESTED only."""
import json, sys, time
from pathlib import Path
import torch
from safetensors.torch import save_file
import engine as E
import eval3
torch.set_num_threads(1)
CFGS = {"A": E.CFG3, "B": E.CFG4B, "C": E.CFG4C}
OFFSET = 30000
arm = sys.argv[2]; cfg = CFGS[arm]
out = Path(sys.argv[1]) / arm; out.mkdir(parents=True, exist_ok=True)
for s in map(int, sys.argv[3:]):
    if (out / f"seed{s}.json").exists():
        continue
    t = time.time()
    m = E.train(s, cfg)
    r = dict(E.evaluate(m), **eval3.evaluate3(m, OFFSET))
    # P6 control: the same trained model with coupling switched off at test time (label kept). A and B: unchanged.
    saved = m.couple; m.couple = False
    r["tf_alpha8_k127_uncoupled"] = eval3.tf_acc(m, "alpha8", 127, OFFSET + 8000 + 20 + 127)
    m.couple = saved
    save_file({k: v.contiguous() for k, v in m.state_dict().items()}, out / f"engine4{arm}_seed{s}.safetensors")
    (out / f"seed{s}.json").write_text(json.dumps({"seed": s, "arm": arm, "cfg": cfg, "params": E.n_params(m),
                                                   "scores": r, "train_seconds": round(time.time() - t)}))
    print(f"{arm} seed {s}: {round(time.time()-t)}s", json.dumps({k: round(v, 4) for k, v in r.items()}), flush=True)
