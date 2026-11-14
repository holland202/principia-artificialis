"""EXPLORATORY, not registered (C-EXPLORE): written after the registered run, because R5's outcome (note037's
pipeline rejects only 0.7% of true GOE(64) spectra) raised the question of its power. How often does the same
pipeline reject the Wigner reference when the spectrum is Poisson (independent uniform levels) of 64 levels?
And, for comparison, how often does a one-sided check on the spacing ratio (pooled over one 64-level spectrum)
fall below the GOE-to-Poisson midpoint 0.458?"""
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rmt037 as r  # noqa: E402

rng = np.random.default_rng(20261115)
rej_pipe = rej_ratio_poi = rej_ratio_goe = 0
for _ in range(1000):
    ev = np.sort(rng.uniform(size=64))
    sp = np.diff(np.poly1d(np.polyfit(ev, np.arange(1, 65), 5))(ev))
    sp = sp[(sp > 0) & (sp < 5)]
    rej_pipe += stats.ks_2samp(sp, rng.rayleigh(scale=np.sqrt(2 / np.pi), size=len(sp))).pvalue < 0.05
    rej_ratio_poi += r.ratios(r.regions(ev)["bulk"])[0].mean() < 0.458
    rej_ratio_goe += r.ratios(r.regions(r.goe_levels(64, rng))["bulk"])[0].mean() < 0.458
print(f"note037 pipeline rejects Wigner on Poisson(64): {rej_pipe / 1000:.3f}")
print(f"ratio < 0.458 on one Poisson(64) spectrum: {rej_ratio_poi / 1000:.3f}; on one GOE(64) spectrum: {rej_ratio_goe / 1000:.3f}")
