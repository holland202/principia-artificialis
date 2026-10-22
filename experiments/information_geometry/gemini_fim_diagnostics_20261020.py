"""Exploratory diagnostic of a Gemini-proposed Fisher instrument (2026-10-20).

Run from any directory with:
    python experiments/information_geometry/gemini_fim_diagnostics_20261020.py

Not a preregistered study, independent replication, or proof of a phase transition.
"""
import contextlib
import io
from pathlib import Path
import runpy
import sys

import numpy as np

SOURCE = Path(__file__).resolve().parents[2] / "docs" / "external" / "gemini_fim_redesign_20261020.py"
with contextlib.redirect_stdout(io.StringIO()) as captured:
    demo = runpy.run_path(str(SOURCE))
print("EXACT GEMINI SCRIPT STDOUT:")
print(captured.getvalue(), end="")
print("PYTHON:", sys.version.split()[0])
print("NUMPY:", np.__version__)

x, y = demo["X"], demo["Y_true"]
w1, w2 = demo["W1"], demo["W2"]
forward = demo["forward_pass"]
step = demo["run_gradient_descent_step"]
fisher = demo["compute_exact_softmax_fim"]
positive_eigenvalues = demo["get_nonzero_eigenvalues"]
base_spectrum = positive_eigenvalues(fisher(w1, w2, x))
base_condition = float(base_spectrum.max() / base_spectrum.min())
_, probability = forward(w1, w2, x)
base_loss = float(-np.sum(y * np.log(probability)) / len(x))
print(f"base_condition={base_condition:.14f}")
print(f"base_loss={base_loss:.14f}")
print(f"base_rank={len(base_spectrum)}")

for rate in (0.01, 0.1, 0.5):
    next_w1, next_w2, before_loss = step(w1, w2, x, y, rate)
    next_spectrum = positive_eigenvalues(fisher(next_w1, next_w2, x))
    next_condition = float(next_spectrum.max() / next_spectrum.min())
    _, next_probability = forward(next_w1, next_w2, x)
    after_loss = float(-np.sum(y * np.log(next_probability)) / len(x))
    print(
        f"lr={rate:.2f} rank={len(next_spectrum)} "
        f"initial_cond={base_condition:.14f} next_cond={next_condition:.14f} "
        f"ratio={next_condition / base_condition:.14f} "
        f"loss_before={before_loss:.14f} loss_after={after_loss:.14f} "
        f"loss_reduction_pct={(before_loss - after_loss) / before_loss * 100:.14f}"
    )
