"""Betting e-process for H0: success rate <= p0 (anytime-valid).
Validity (analytic): for lam in [0, 1/p0], every factor is >= 0 and
E[factor | p <= p0] = 1 + lam*(p - p0) <= 1, so wealth is a nonnegative
supermartingale; Ville gives P(ever >= 1/alpha) <= alpha.
Gate (simulation): implementation check only, not the proof."""
import random, sys

def check_domain(p0, lam):
    if not (0 < p0 < 1 and 0 <= lam <= 1 / p0):
        raise ValueError(f"lam={lam} outside [0, 1/p0] for H0: p <= p0={p0}")

def e_process(xs, p0, lam=0.5):
    check_domain(p0, lam)            # eager: fires on call, not on first iteration
    def run():
        w = 1.0
        for x in xs:                 # x in {0,1}
            w *= 1 + lam * (x - p0)
            yield w
    return run()

def rejects(xs, p0, alpha=0.05, lam=0.5):
    return any(w >= 1 / alpha for w in e_process(xs, p0, lam))  # peek every step

def rate(p_true, p0=0.5, n=200, trials=2000, seed=0):
    rng = random.Random(seed)
    hits = sum(rejects([rng.random() < p_true for _ in range(n)], p0)
               for _ in range(trials))
    return hits / trials

def guard_fires(p0, lam):
    try:
        e_process([], p0, lam)
        return False
    except ValueError:
        return True

print("python:", sys.version.split()[0])
if "--sabotage" in sys.argv:          # must exit 1: bad lam has to be refused
    ok = not guard_fires(0.5, -0.5)
    print("sabotage lam=-0.5 accepted:", ok)
    print("GATE:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

null = rate(0.5)   # anti-vacuity: H0 true, peeking at all 200 steps
alt  = rate(0.7)   # real effect
guard = guard_fires(0.5, -0.5) and guard_fires(0.5, 2.5) and not guard_fires(0.5, 0.5)
print(f"null rejection rate (must be <= 0.05): {null:.4f}")
print(f"alt  rejection rate (must be high):    {alt:.4f}")
print(f"domain guard (bad lam refused, good lam accepted): {guard}")
ok = null <= 0.05 and alt >= 0.8 and guard
print("GATE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
