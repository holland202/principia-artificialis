"""Package RMT-IH-001's trained tiny models for a Hugging Face model repo (no upload here).

Usage: python3 export_hf.py MODELS_DIR RESULTS_DIR OUT_DIR
Writes: weights/<arm>_seed<k>.safetensors, config.json, tinyih.py (the model code), metrics/*.json,
SHA256SUMS. The model card (README.md) is written by hand from RESULTS.md.
Written by Claude (Anthropic, Opus 5.5), 2026-11-16."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import torch
from safetensors.torch import save_file

src, res, out = map(Path, sys.argv[1:4])
(out / "weights").mkdir(parents=True, exist_ok=True)
(out / "metrics").mkdir(exist_ok=True)
for pt in sorted(src.glob("*.pt")):
    sd = torch.load(pt, map_location="cpu", weights_only=True)
    save_file({k: v.contiguous() for k, v in sd.items()}, out / "weights" / (pt.stem + ".safetensors"))
here = Path(__file__).resolve().parent
shutil.copy(here / "tinyih.py", out / "tinyih.py")
cfg = json.loads(next(res.glob("run_seed*.json")).read_text())["cfg"]
(out / "config.json").write_text(json.dumps({"architecture": "TinyAttnOnly (attention-only, pre-LN, no MLP)", **cfg},
                                            indent=2))
for j in sorted(res.glob("run_seed*.json")):
    shutil.copy(j, out / "metrics" / j.name)
lines = []
for f in sorted(p for p in out.rglob("*") if p.is_file() and p.name != "SHA256SUMS"):
    lines.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(out)}")
(out / "SHA256SUMS").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
