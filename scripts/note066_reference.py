#!/usr/bin/env python3
"""note066_reference.py - Note #066, the Ambiguity Engine.

  python scripts/note066_reference.py              # every number in the note: explore table + AMB-2
  python scripts/note066_reference.py --explore    # the exploratory chain check only
  python scripts/note066_reference.py --sabotage   # AMB-2 with the surrogate = full grid (B2 must fail, exit 1)

1-D mass-spring chain between two uniform leads; transmission of a plane wave by transfer matrices.
Lossless: scattering only.
"""
import hashlib, json, sys

import numpy as np

K, M0 = 1.0, 2.0


def transmission(masses, ws):
    """Plane-wave power transmission through the chain at each frequency in ws (lead mass M0, spring K)."""
    ws = np.asarray(ws, dtype=float)
    q = np.arccos(1 - M0 * ws ** 2 / (2 * K))
    M = np.tile(np.eye(2, dtype=complex), (len(ws), 1, 1))
    for m in masses:
        A = np.zeros((len(ws), 2, 2), dtype=complex)
        A[:, 0, 0] = (2 * K - m * ws ** 2) / K
        A[:, 0, 1] = -1
        A[:, 1, 0] = 1
        M = A @ M
    P = np.zeros((len(ws), 2, 2), dtype=complex)
    P[:, 0, 0], P[:, 0, 1], P[:, 1, :] = np.exp(1j * q), np.exp(-1j * q), 1
    W = np.linalg.solve(P, M @ P)
    return np.abs(1 / W[:, 1, 1]) ** 2


def explore():
    n = 200
    ws = np.linspace(0.05, np.sqrt(4 * K / M0) - 0.05, 400)
    rng = np.random.default_rng(0)
    arms = {"uniform (control)": [np.full(n, 2.0)],
            "periodic 1,3,1,3": [np.tile([1.0, 3.0], n // 2)],
            "random U[1,3]": [rng.uniform(1, 3, n) for _ in range(30)],
            "graded 1->3": [np.linspace(1, 3, n)]}
    for name, chains in arms.items():
        t = np.mean([transmission(c, ws) for c in chains], axis=0)
        lo, hi = t[ws < 0.5].mean(), t[ws >= 0.5].mean()
        print(f"{name:20s} mean T {t.mean():.3f}   low band(w<0.5) {lo:.3f}   high band {hi:.3f}")


# ---- AMB-2 (registered in note066 at 62334da, before this code existed) ----
N, GENS, MUT, SIGMA, ROUNDS, SEEDS = 100, 500, 5, 0.3, 6, range(10)
GRID = np.linspace(0.05, 0.5, 200)
S0 = [0.1, 0.2, 0.3, 0.4]
RECORDED = (("B1", "B2", "B4"), "2db69064d8a970c9ceff2167826626d683674fbb238d68721ab19cac0d382592")


def optimise(S, seed):
    """Hill climbing from all masses = 2 against the surrogate mean T over S. Fresh generator per call."""
    rng = np.random.default_rng(seed)
    m = np.full(N, 2.0)
    best = transmission(m, S).mean()
    for _ in range(GENS):
        c = m.copy()
        idx = rng.choice(N, MUT, replace=False)
        c[idx] = np.clip(c[idx] + rng.normal(0, SIGMA, MUT), 1, 3)
        v = transmission(c, S).mean()
        if v <= best:
            m, best = c, v
    return m


def score(m, S):
    full = transmission(m, GRID)
    return float(full.mean()), float(transmission(m, S).mean()), full


def amb2(sabotage):
    s0 = list(GRID) if sabotage else S0
    b1 = round(float(transmission(np.full(N, 2.0), GRID).mean()), 3)
    out = {"B1_uniform_T_full": b1, "seeds": []}
    for seed in SEEDS:
        m0 = optimise(s0, seed)
        f0, g0, full0 = score(m0, s0)
        row = {"seed": seed, "round0": {"T_full": f0, "T_S": g0}}
        rr = np.random.default_rng(1000 + seed)
        for arm in ("ENGINE", "RANDOM", "NONE"):
            S, m, full = list(s0), m0, full0
            for _ in range(ROUNDS):
                if arm == "ENGINE":
                    S.append(float(GRID[int(np.argmax(full))]))
                elif arm == "RANDOM":
                    S.append(float(rr.uniform(0.05, 0.5)))
                m = optimise(S, seed)
                f, g, full = score(m, S)
            row[arm] = {"T_full": f, "T_S": g, "gap": f - g, "S_added": [round(x, 4) for x in S[len(s0):]]}
        out["seeds"].append(row)
        print(f"  seed {seed}: round0 T_full {f0:.4f} T_S {g0:.4f} | final T_full ENGINE {row['ENGINE']['T_full']:.4f}"
              f"  RANDOM {row['RANDOM']['T_full']:.4f}  NONE {row['NONE']['T_full']:.4f}"
              f" | ENGINE gap {row['ENGINE']['gap']:.4f}")
    sd = out["seeds"]
    mean = lambda arm, k: float(np.mean([r[arm][k] for r in sd]))  # noqa: E731
    r0f, r0s = float(np.mean([r["round0"]["T_full"] for r in sd])), float(np.mean([r["round0"]["T_S"] for r in sd]))
    r0gap = r0f - r0s
    wins = sum(r["ENGINE"]["T_full"] < r["RANDOM"]["T_full"] for r in sd)
    print(f"  mean round0 T_full {r0f:.4f}  T_S {r0s:.4f}  gap {r0gap:.4f}")
    print(f"  mean final T_full  ENGINE {mean('ENGINE','T_full'):.4f}  RANDOM {mean('RANDOM','T_full'):.4f}"
          f"  NONE {mean('NONE','T_full'):.4f};  ENGINE lower than RANDOM in {wins} of 10 seeds")
    print(f"  mean final gap     ENGINE {mean('ENGINE','gap'):.4f}  RANDOM {mean('RANDOM','gap'):.4f}"
          f"  NONE {mean('NONE','gap'):.4f};  B1 uniform T_full {b1:.3f}")
    v = {"B1": b1 == 1.0, "B2": r0s <= 0.5 * r0f,
         "B3": mean("ENGINE", "T_full") < mean("RANDOM", "T_full") and wins >= 7,
         "B4": mean("ENGINE", "gap") <= r0gap / 3}
    for k, x in v.items():
        print(f"  {k}  {'HELD' if x else 'REFUTED'}")
    held = tuple(k for k, x in v.items() if x)
    print(f"VERDICT {len(held)} of {len(v)} as registered (B5 is --sabotage; B6 is the door)")
    rounded = json.loads(json.dumps(out), parse_float=lambda x: round(float(x), 4))
    dg = hashlib.sha256(json.dumps({"r": rounded, "v": v}, sort_keys=True).encode()).hexdigest()
    print(f"DIGEST {dg}")
    if sabotage or RECORDED is None:
        return 0 if all(v.values()) else 1
    return 0 if (held, dg) == RECORDED else 1


def main():
    if "--explore" in sys.argv:
        explore()
        return 0
    sabotage = "--sabotage" in sys.argv
    if not sabotage:
        print("== exploratory chain check (unregistered)")
        explore()
    print(f"== AMB-2 ({'SABOTAGE: surrogate = full grid' if sabotage else 'registered run'})")
    return amb2(sabotage)


if __name__ == "__main__":
    sys.exit(main())
