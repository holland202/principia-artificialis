"""CCC-001 LADDER post-hoc shares (NOT REGISTERED; written after the run at b173d31). Descriptive only.

Recomputes the fits with ladder.py's own functions (same numbers as results/ccc_001/ladder_run.txt) and prints the
share of the total sum of squares of y each rung explains in-sample, and each rung's share of the R0 -> R3 gap.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ladder import design, evaluate, load, rows_of, split_rss  # noqa: E402

rows = rows_of([p for p in load() if p["src"] == "Q"])
y = np.array([r[5] for r in rows])
items = np.array([r[1] for r in rows])
Xs = [design(rows, k) for k in range(4)]
ev = evaluate(Xs, y, items)
T = float(np.sum(y ** 2))
lay = [split_rss(e["res_in"], rows)[0] for e in ev]
mse = [e["mse"] for e in ev]
print(f"POSTHOC total sum of squares of y {T:.9f}")
for k in range(4):
    print(f"POSTHOC R{k} in-sample share of total SS explained {(T - float(np.sum(ev[k]['res_in'] ** 2))) / T:.4f}")
for k in (1, 2):
    print(f"POSTHOC R{k} share of the R0 -> R3 gap: in-sample layout part {(lay[0] - lay[k]) / (lay[0] - lay[3]):.4f}; "
          f"held-out MSE {(mse[0] - mse[k]) / (mse[0] - mse[3]):.4f}")
