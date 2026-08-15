"""
Note #038 reference experiment — The Free-Physics Principle
============================================================
CLAIM: if the truth lies in a known closed convex set K, projecting any
estimator onto K never increases error (projection onto convex sets is
nonexpansive), and the SIZE of the benefit is governed by ESTIMATION
VARIANCE (data scarcity), not by how often the raw estimator violates K.

Deliberately NOT quantum: ordinary linear regression, w* in the simplex
(nonneg, sum=1). Raw OLS vs OLS projected onto K, across sample sizes.

REGISTERED:
  P1  projected MSE <= raw MSE at every n (paired, 200 trials each)
  P2  the benefit DECAYS with n (regularizer of scarcity, no-op at
      convergence) — monotone decreasing across the n-grid
  P3  DISSOCIATION: violation frequency stays high even where the
      benefit has become negligible -> violation rate does not govern
      the benefit. (This is the surprising part; it is what F14
      measured in channel space and N1-c's refutation predicted.)
"""
import numpy as np
rng = np.random.default_rng(7)
d = 8
w_true = rng.dirichlet(np.ones(d))          # truth strictly inside K

def project_simplex(v):
    """Euclidean projection onto {w >= 0, sum w = 1} (Held et al.)."""
    u = np.sort(v)[::-1]
    css = np.cumsum(u)
    rho = np.max(np.where(u + (1 - css) / (np.arange(d) + 1) > 0)[0])
    theta = (1 - css[rho]) / (rho + 1)
    return np.maximum(v + theta, 0)

print(f"{'n':>6} {'raw MSE':>10} {'proj MSE':>10} {'benefit':>10} "
      f"{'violate%':>9}")
rows = []
for n in [10, 20, 40, 80, 160, 320, 640, 1280]:
    raw_e, prj_e, viol = [], [], 0
    for t in range(200):
        X = rng.normal(0, 1, (n, d))
        y = X @ w_true + rng.normal(0, 0.5, n)
        w_ols = np.linalg.lstsq(X, y, rcond=None)[0]
        w_prj = project_simplex(w_ols)
        raw_e.append(np.sum((w_ols - w_true) ** 2))
        prj_e.append(np.sum((w_prj - w_true) ** 2))
        viol += (w_ols.min() < -1e-9) or (abs(w_ols.sum() - 1) > 1e-9)
    r, p = np.mean(raw_e), np.mean(prj_e)
    rows.append((n, r, p, r - p, 100 * viol / 200))
    print(f"{n:>6} {r:>10.4f} {p:>10.4f} {r-p:>10.4f} {rows[-1][4]:>8.0f}%")

ben = [r[3] for r in rows]
vio = [r[4] for r in rows]
p1 = all(r[2] <= r[1] + 1e-12 for r in rows)
p2 = all(ben[i] >= ben[i+1] - 1e-9 for i in range(len(ben)-1))
p3 = vio[-1] > 90 and ben[-1] < 0.02 * ben[0]
print(f"\nP1 projection never hurts (200 paired trials/n): {p1}")
print(f"P2 benefit decays monotonically with n:           {p2}  "
      f"({ben[0]:.4f} -> {ben[-1]:.5f})")
print(f"P3 DISSOCIATION — violation still {vio[-1]:.0f}% at n=1280 while "
      f"benefit fell {ben[0]/max(ben[-1],1e-9):.0f}x: {p3}")

# ---------------------------------------------------------------------------
# Added 2026-08-15: this script computed p1/p2/p3 and printed them, but
# nothing ever consumed the values -- exit code was always 0 regardless of
# what they said. One of the 14 reference scripts found ungated in the
# 2026-08-14 estate audit (Principia note057's own kind of finding, one
# level up: not a check with no fail path, a check with no path from its
# result to anything at all).
#
# P1 is treated as the GATE, not a prediction: it is a mathematical
# guarantee (projection onto a convex set containing the truth is
# nonexpansive), so if it is ever False the projection code itself is
# broken and no claim about P2/P3 is possible. P2 and P3 are the genuine
# empirical predictions this note registers.
from prereg import Study

s = Study("note038 -- Free-Physics Principle")
s.gate("projection never increases error (nonexpansive property)",
       lambda: p1, expect="True at every n, 200 paired trials each")
s.predict("P2", "benefit decays monotonically with n", lambda: p2,
          value=f"{ben[0]:.4f} -> {ben[-1]:.5f}")
s.predict("P3", "dissociation: violation rate stays high while the "
                "benefit becomes negligible", lambda: p3,
          value=f"viol={vio[-1]:.0f}% at n=1280, benefit fell "
                f"{ben[0]/max(ben[-1],1e-9):.0f}x")
raise SystemExit(s.report())
