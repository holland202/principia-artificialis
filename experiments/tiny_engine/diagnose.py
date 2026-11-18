"""DIAGNOSIS (exploration, disclosed): where does long-string copying break? Copy accuracy by string length k
(trained up to k = 63). Copy distance = k + 1, so this also measures accuracy against relative distance."""
import sys
import numpy as np, torch
from safetensors.torch import load_file
import engine as E
for s in sys.argv[1:]:
    m = E.TinyEngine(); m.load_state_dict(load_file(f"/root/engine_runs/engine_seed{s}.safetensors")); m.eval()
    row = []
    for k in (40, 56, 63, 72, 80, 96, 112, 127):
        rng = np.random.default_rng(k)
        xs = [np.concatenate([[E.BOS], z, [E.SEP], z]) for z in (rng.choice(np.arange(1, 128), k, replace=False) for _ in range(64))]
        x = torch.tensor(np.array(xs)).long()
        with torch.no_grad():
            p = m(x).argmax(-1)
        row.append(f"k{k}:{float((p[:, k + 1:-1] == x[:, k + 2:]).float().mean()):.2f}")
    print(f"seed {s}", " ".join(row), flush=True)
