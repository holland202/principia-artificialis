"""
Note #040 — THE REDUNDANCY DIVIDEND: radiation-hard AI for free?
=================================================================
Space radiation, cosmic rays at altitude, and silent data corruption in
datacenters all do the same thing to a neural network: they kill neurons
and flip weights at random. Industry answers with HARDWARE (shielding,
ECC, triple modular redundancy). This note asks whether the KNOWLEDGE
can be hardened instead — and measured for hardness BEFORE deployment.

Bridge from Note #039: Quantum Darwinism => a network makes selected
information OBJECTIVE by imprinting it REDUNDANTLY across neuron
fragments, and that redundancy is measurable (fragment mutual info).
Unclaimed consequence: Darwinian redundancy should PREDICT fault
tolerance, and training-time pressure toward redundancy should buy
radiation-hardness with zero extra silicon.

Models: MLP 4->20->1, y = sign(x1), three training regimes spanning a
redundancy spectrum: L1-sparse (concentrates knowledge), plain, dropout
(predicted by #039-D5 to proliferate it). 4 seeds each = 12 models,
matched clean accuracy required (>= 0.95) or the model is excluded.

REGISTERED (before running):
  R0  ANTI-VACUITY: the fault instrument must discriminate — spread of
      p_crit across models >= 1.5x (max/min). If all models are equally
      robust the test is uninformative and NO claim may be made.
  R1  Darwinian redundancy R = shuffle-corrected I(task bit; 25% neuron
      fragment) PREDICTS knockout tolerance: Spearman rank corr(R,
      p_crit) >= +0.7 across models.
  R2  (= #039-D5, an OPEN prediction of this repo, now run): dropout
      training yields HIGHER mean R than plain at matched accuracy.
  R3  R predicts p_crit BETTER than clean accuracy does:
      |rho(R, p_crit)| > |rho(acc, p_crit)|.
  R4  Same ranking holds under a second, different fault model (random
      sign-flips of first-layer weights): rho(R, p_crit_flip) >= +0.7.
"""
import numpy as np
rng = np.random.default_rng(17)
H = 20

def data(n, r=rng):
    X = r.normal(0, 1, (n, 4))
    return X, (X[:, 0] > 0).astype(int)

def fwd(p, X, mask=None):
    Hh = np.tanh(X @ p[0] + p[1])
    if mask is not None: Hh = Hh * mask
    o = 1/(1+np.exp(-(Hh @ p[2] + p[3]).ravel()))
    return Hh, o

def train(regime, seed, steps=2600, bs=64, lr=0.3):
    r = np.random.default_rng(seed)
    p = [r.normal(0,.4,(4,H)), np.zeros(H), r.normal(0,.4,(H,1)), np.zeros(1)]
    for s in range(steps):
        X, y = data(bs, r)
        Hh = np.tanh(X @ p[0] + p[1])
        keep = np.ones(H)
        if regime == "dropout":
            keep = (r.random(H) > 0.4) / 0.6
        Hd = Hh * keep
        o = 1/(1+np.exp(-(Hd @ p[2] + p[3]).ravel()))
        g = (o - y) / bs
        gW2 = Hd.T @ g[:, None]; gb2 = g.sum()
        gH = np.outer(g, p[2].ravel()) * keep * (1 - Hh**2)
        p[0] -= lr * (X.T @ gH + (0.004*np.sign(p[0]) if regime=="sparse" else 0))
        p[1] -= lr * gH.sum(0)
        p[2] -= lr * (gW2 + (0.004*np.sign(p[2]) if regime=="sparse" else 0))
        p[3] -= lr * gb2
    return p

def acc(p, n=3000, mask=None):
    X, y = data(n, np.random.default_rng(999))
    _, o = fwd(p, X, mask)
    return ((o > .5) == y).mean()

def mi_bits(y, Hs, frag):
    pat = ((Hs[:, frag] > 0) @ (1 << np.arange(len(frag)))).astype(int)
    I = 0.0
    for s in np.unique(pat):
        m = pat == s; ps = m.mean()
        for c in (0, 1):
            pj = (m & (y == c)).mean()
            if pj > 0: I += pj*np.log2(pj/(ps*(y==c).mean()))
    return I

def redundancy(p, n=5000, f=5, reps=40):
    X, _ = data(n, np.random.default_rng(555))
    y = (X[:, 0] > 0).astype(int)
    Hs, _ = fwd(p, X)
    vals = []
    for _ in range(reps):
        fr = rng.choice(H, f, replace=False)
        vals.append(mi_bits(y, Hs, fr) - mi_bits(rng.permutation(y), Hs, fr))
    return max(0.0, float(np.mean(vals)))

def p_crit_knockout(p, thresh=0.9):
    """largest neuron-death fraction at which mean acc still >= thresh"""
    grid = np.linspace(0, 0.9, 19); last = 0.0
    for q in grid:
        accs = []
        for t in range(24):
            m = (np.random.default_rng(7000+t).random(H) > q).astype(float)
            accs.append(acc(p, 1500, m))
        if np.mean(accs) >= thresh: last = q
        else: break
    return last

def p_crit_flip(p, thresh=0.9):
    """largest fraction of W1 sign-flips (SEU model) with acc >= thresh"""
    grid = np.linspace(0, 0.9, 19); last = 0.0
    for q in grid:
        accs = []
        for t in range(24):
            r2 = np.random.default_rng(9000+t)
            W = p[0].copy()
            f = r2.random(W.shape) < q
            W[f] = -W[f]
            accs.append(acc([W,p[1],p[2],p[3]], 1500))
        if np.mean(accs) >= thresh: last = q
        else: break
    return last

def _midrank(x):
    """Average ranks for ties. Ported verbatim from note054_reference.py,
    where this defect was first found on device 2026-08-09.

    DEFECT IN THIS FILE, found 2026-08-15, kept: the original ranked by
    double-argsort with no tie correction, and this data is heavily tied --
    across 12 runs, KO takes only 6 distinct values (one group of 5), FL
    takes 5 (one group of 5), A takes 8. np.argsort defaults to an UNSTABLE
    sort, so the published statistic depended on which sort path the build
    took: quicksort and heapsort gave R1 = +0.7133, mergesort and stable
    gave +0.7203, against a registered threshold of >= +0.70. The claim
    cleared its bar by 0.013 in one sort path -- a verdict resting on
    NumPy's choice of algorithm.

    Tie-corrected values, and what was published before this fix:
        R1 rho(R, KO)   published +0.71   corrected +0.78
        R3 rho(A, KO)   published +0.40   corrected +0.36
        R4 rho(R, FL)   published +0.56   corrected +0.43
    No verdict changes: R1 still passes, R3 still holds, R4 is still
    REFUTED. Only the numbers were wrong, and R1's margin was a coin flip.
    """
    order = np.argsort(x, kind="stable")
    ranks = np.empty(len(x), float)
    s_, i = x[order], 0
    while i < len(s_):
        j = i
        while j + 1 < len(s_) and s_[j + 1] == s_[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def spearman(a, b):
    ra = _midrank(np.asarray(a, float))
    rb = _midrank(np.asarray(b, float))
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / d) if d > 0 else 0.0

rows = []
print(f"{'regime':>8} {'seed':>4} {'acc':>6} {'R (bits)':>9} "
      f"{'p_crit KO':>10} {'p_crit flip':>11}")
for regime in ("sparse", "plain", "dropout"):
    for seed in range(4):
        p = train(regime, 100+seed)
        a = acc(p)
        if a < 0.95:
            print(f"{regime:>8} {seed:>4}  EXCLUDED (acc {a:.3f})"); continue
        R = redundancy(p)
        ko = p_crit_knockout(p); fl = p_crit_flip(p)
        rows.append((regime, seed, a, R, ko, fl))
        print(f"{regime:>8} {seed:>4} {a:>6.3f} {R:>9.3f} {ko:>10.2f} {fl:>11.2f}")

reg = np.array([r[0] for r in rows]); A = np.array([r[2] for r in rows])
R = np.array([r[3] for r in rows]); KO = np.array([r[4] for r in rows])
FL = np.array([r[5] for r in rows])
r0 = KO.max()/max(KO.min(),1e-9) >= 1.5
rho_R  = spearman(R, KO); rho_A = spearman(A, KO); rho_F = spearman(R, FL)
mR = {g: R[reg==g].mean() for g in ("sparse","plain","dropout")}
print(f"\nR0 instrument discriminates (spread {KO.max()/max(KO.min(),1e-9):.1f}x "
      f">= 1.5x): {r0}")
print(f"R1 redundancy predicts knockout tolerance: rho = {rho_R:+.2f} "
      f"(>= +0.7): {rho_R >= 0.7}")
print(f"R2 (#039-D5 CLOSED) mean R — sparse {mR['sparse']:.3f} | plain "
      f"{mR['plain']:.3f} | dropout {mR['dropout']:.3f} : "
      f"{mR['dropout'] > mR['plain']}")
print(f"R3 R beats accuracy as predictor: |{rho_R:+.2f}| > |{rho_A:+.2f}| : "
      f"{abs(rho_R) > abs(rho_A)}")
print(f"R4 transfers to SEU sign-flip faults: rho = {rho_F:+.2f} "
      f"(>= +0.7): {rho_F >= 0.7}")
np.savez("n40.npz", R=R, KO=KO, FL=FL, A=A,
         reg=np.array([r[0] for r in rows]))

# ---------------------------------------------------------------------------
# VERDICT GATE, added 2026-08-15. This script computed r0/R1/R2/R3/R4 and
# printed them; nothing consumed the values and the exit code was always 0.
# One of 14 ungated reference scripts found in the 2026-08-14 estate audit.
#
# R0 is the GATE, not a prediction: it is the anti-vacuity control this note
# registered -- if the fault instrument cannot discriminate, no claim about
# R1-R4 is admissible in either direction.
#
# R4 is REFUTED and stays refuted. note040.md publishes it as a kept
# refutation; prereg reports REFUTED without failing the build, which is the
# correct behavior. A gate that failed on R4 would delete a published finding.
from prereg import Study

st = Study("note040 -- Redundancy Dividend")
st.gate("fault instrument discriminates across regimes",
        lambda: r0, expect=f"knockout spread >= 1.5x (measured "
                           f"{KO.max()/max(KO.min(),1e-9):.1f}x)")
st.predict("R1", "redundancy predicts neuron-knockout tolerance",
           lambda: rho_R >= 0.7, value=f"rho = {rho_R:+.4f} (>= +0.70)")
st.predict("R2", "dropout raises mean redundancy above plain (closes "
                 "note039's open D5)", lambda: mR["dropout"] > mR["plain"],
           value=f"sparse {mR['sparse']:.3f} | plain {mR['plain']:.3f} | "
                 f"dropout {mR['dropout']:.3f}")
st.predict("R3", "redundancy out-predicts clean accuracy as a hardness "
                 "proxy", lambda: abs(rho_R) > abs(rho_A),
           value=f"|{rho_R:+.4f}| > |{rho_A:+.4f}|")
st.predict("R4", "the ranking transfers to SEU sign-flip faults",
           lambda: rho_F >= 0.7, value=f"rho = {rho_F:+.4f} (>= +0.70)")
st.open_question("R5", "the lying-observer gap closes if redundancy is "
                       "measured over sign-stable fragments "
                       "(weight-perturbation-aware redundancy): a corrected "
                       "metric should recover rho >= +0.7 on sign-flip "
                       "faults. Unrun.")
raise SystemExit(st.report())
