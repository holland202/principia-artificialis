"""
Note #045 — THE STUBBORNNESS OF THE OBJECTIVE: redundancy predicts
resistance to deliberate unlearning
====================================================================
Machine unlearning (GDPR erasure, capability removal, safety) asks: how
hard is it to make a network FORGET on purpose? Note #040 showed
Darwinian redundancy predicts survival under RANDOM damage. Unclaimed
consequence: the same number should predict survival under TARGETED
damage — gradient-ascent unlearning. If true: objectivity (in Zurek's
redundancy sense) is precisely the property that resists erasure. What
a network makes objective, it also makes stubborn.

REGISTERED:
  U0  ANTI-VACUITY: spread in steps-to-forget across models >= 2x.
  U1  Spearman rho(redundancy, steps-to-forget) >= +0.7 across 12
      models at matched clean accuracy (>= 0.95).
  U2  Redundancy out-predicts clean accuracy: |rho_R| > |rho_acc|.
  U3  SAFETY COROLLARY (directional): dropout-trained (high-R) models
      require more ascent steps to forget than sparse (low-R) ones,
      mean vs mean.
"""
import numpy as np
rng = np.random.default_rng(31)
H = 20

def data(n, r=rng):
    X = r.normal(0, 1, (n, 4)); return X, (X[:, 0] > 0).astype(int)

def fwd(p, X):
    Hh = np.tanh(X @ p[0] + p[1])
    return Hh, 1/(1+np.exp(-(Hh @ p[2] + p[3]).ravel()))

def train(regime, seed, steps=2600, bs=64, lr=0.3):
    r = np.random.default_rng(seed)
    p = [r.normal(0,.4,(4,H)), np.zeros(H), r.normal(0,.4,(H,1)), np.zeros(1)]
    for s in range(steps):
        X, y = data(bs, r)
        Hh = np.tanh(X @ p[0] + p[1])
        keep = (r.random(H) > 0.4)/0.6 if regime=="dropout" else np.ones(H)
        Hd = Hh*keep
        o = 1/(1+np.exp(-(Hd @ p[2] + p[3]).ravel()))
        g = (o - y)/bs
        gH = np.outer(g, p[2].ravel())*keep*(1-Hh**2)
        p[0] -= lr*(X.T@gH + (0.004*np.sign(p[0]) if regime=="sparse" else 0))
        p[1] -= lr*gH.sum(0)
        p[2] -= lr*(Hd.T@g[:,None] + (0.004*np.sign(p[2]) if regime=="sparse" else 0))
        p[3] -= lr*g.sum()
    return p

def acc(p, n=3000):
    X, y = data(n, np.random.default_rng(999))
    return ((fwd(p, X)[1] > .5) == y).mean()

def mi_bits(y, Hs, fr):
    pat = ((Hs[:, fr] > 0) @ (1 << np.arange(len(fr)))).astype(int)
    I = 0.0
    for s in np.unique(pat):
        m = pat == s; ps = m.mean()
        for c in (0,1):
            pj = (m & (y==c)).mean()
            if pj > 0: I += pj*np.log2(pj/(ps*(y==c).mean()))
    return I

def redundancy(p, n=5000, f=5, reps=40):
    X,_ = data(n, np.random.default_rng(555)); y = (X[:,0]>0).astype(int)
    Hs,_ = fwd(p, X)
    v = [mi_bits(y,Hs,rng.choice(H,f,replace=False)) -
         mi_bits(rng.permutation(y),Hs,rng.choice(H,f,replace=False))
         for _ in range(reps)]
    return max(0.0, float(np.mean(v)))

def steps_to_forget(p, lr=0.05, cap=400):
    """gradient ASCENT on the task loss until accuracy < 0.6"""
    q = [w.copy() for w in p]
    r = np.random.default_rng(77)
    for s in range(cap):
        if acc(q, 1200) < 0.6: return s
        X, y = data(64, r)
        Hh = np.tanh(X @ q[0] + q[1])
        o = 1/(1+np.exp(-(Hh @ q[2] + q[3]).ravel()))
        g = (o - y)/64
        gH = np.outer(g, q[2].ravel())*(1-Hh**2)
        q[0] += lr*X.T@gH; q[1] += lr*gH.sum(0)     # ASCENT
        q[2] += lr*Hh.T@g[:,None]; q[3] += lr*g.sum()
    return cap

def _midrank(x):
    """Average ranks for ties. Ported from note054_reference.py.

    Measured here 2026-08-15: unlike note040, this data is only mildly
    tied -- R is 12/12 distinct, S has one tied pair, A has two small
    groups -- and the statistic is NOT sort-path dependent (quicksort,
    heapsort, mergesort and stable all give U1 = +0.6014). So the untied
    version was a latent hazard here, not an active bug. Corrected anyway,
    for consistency with note040 and note054 and because the hazard is
    real if the data ever ties harder. Published -> corrected:
    U1 +0.60 -> +0.61, U2's accuracy term -0.16 -> -0.11. No verdict
    changes: U0 and U1 still FAIL, U2 and U3 still PASS.
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
    ra = _midrank(np.asarray(a, float)); rb = _midrank(np.asarray(b, float))
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra**2).sum()*(rb**2).sum())
    return float((ra*rb).sum()/d) if d > 0 else 0.0

rows=[]
print(f"{'regime':>8} {'seed':>4} {'acc':>6} {'R(bits)':>8} {'steps2forget':>13}")
for regime in ("sparse","plain","dropout"):
    for seed in range(4):
        p = train(regime, 200+seed); a = acc(p)
        if a < 0.95: print(f"{regime:>8} {seed:>4}  EXCLUDED"); continue
        R = redundancy(p); S = steps_to_forget(p)
        rows.append((regime,a,R,S))
        print(f"{regime:>8} {seed:>4} {a:>6.3f} {R:>8.3f} {S:>13}")
reg=np.array([r[0] for r in rows]); A=np.array([r[1] for r in rows])
R=np.array([r[2] for r in rows]); S=np.array([r[3] for r in rows],float)
u0 = S.max()/max(S.min(),1) >= 2
rho_R, rho_A = spearman(R,S), spearman(A,S)
mS = {g: S[reg==g].mean() for g in ("sparse","plain","dropout")}
print(f"\nU0 spread {S.max()/max(S.min(),1):.1f}x >= 2x: {u0}")
print(f"U1 rho(redundancy, steps-to-forget) = {rho_R:+.2f} (>=+0.7): {rho_R>=0.7}")
print(f"U2 beats accuracy: |{rho_R:+.2f}| > |{rho_A:+.2f}|: {abs(rho_R)>abs(rho_A)}")
print(f"U3 mean steps — sparse {mS['sparse']:.0f} | plain {mS['plain']:.0f} | "
      f"dropout {mS['dropout']:.0f}: {mS['dropout']>mS['sparse']}")

# ---------------------------------------------------------------------------
# VERDICT GATE, added 2026-08-15.
#
# DESIGN NOTE, because this note is the awkward case. U0 is the registered
# anti-vacuity control AND IT FAILED (spread 1.64x against a 2x bar) -- that
# failure is published in note045.md's Status line and kept. Wiring U0 as a
# prereg gate() would suppress every prediction and exit 1 on every run,
# turning a published, deliberate finding into permanent CI red. That is the
# opposite of keeping a refutation: it would make the honest outcome
# indistinguishable from a regression.
#
# So U0 is recorded as a registered claim that FAILED, alongside U1. The
# gate is a separate, genuine harness check: did the experiment actually
# run? If training collapsed or every model fell below the 0.95 accuracy
# filter, there would be nothing to correlate and no claim admissible in
# either direction. That gate CAN fail, and it is what the report depends on.
from prereg import Study

st = Study("note045 -- Stubbornness of the Objective")
st.gate("experiment produced a usable panel (models survived the >=0.95 "
        "accuracy filter, and steps-to-forget is not constant)",
        lambda: len(rows) >= 9 and S.max() > S.min(),
        expect=f"n={len(rows)} models, steps range "
               f"{S.min():.0f}-{S.max():.0f}")
st.predict("U0", "anti-vacuity: steps-to-forget spread >= 2x across models",
           lambda: u0, value=f"spread {S.max()/max(S.min(),1):.2f}x (>= 2x)")
st.predict("U1", "redundancy predicts unlearning resistance",
           lambda: rho_R >= 0.7, value=f"rho = {rho_R:+.4f} (>= +0.70)")
st.predict("U2", "redundancy out-predicts clean accuracy for erasability",
           lambda: abs(rho_R) > abs(rho_A),
           value=f"|{rho_R:+.4f}| > |{rho_A:+.4f}|")
st.predict("U3", "dropout-trained models resist unlearning longer than "
                 "sparse-trained ones", lambda: mS["dropout"] > mS["sparse"],
           value=f"sparse {mS['sparse']:.0f} | plain {mS['plain']:.0f} | "
                 f"dropout {mS['dropout']:.0f}")
st.open_question("U4", "widen the spread: harder tasks, bigger nets, "
                       "per-example unlearning (forget one datum, not the "
                       "whole task) -- the industrially real case. Unrun.")
raise SystemExit(st.report())
