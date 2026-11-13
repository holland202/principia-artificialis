"""MEM-DECAY-001: reversible rank decay vs. destructive TTL/LRU deletion on one frozen synthetic store.

Usage (from the repository root):
    python3 experiments/mem_decay_001/memdecay.py seal  --split test   # build the split, print its SHA-256, score nothing
    python3 experiments/mem_decay_001/memdecay.py run   --split dev    # smoke run on the dev split
    python3 experiments/mem_decay_001/memdecay.py run   --split test   # the registered run (REGISTRATION.md)
    python3 experiments/mem_decay_001/memdecay.py run   --split test --sabotage   # guard disabled: P4 must fail

Design (fixed in REGISTRATION.md before any metric was computed):
  store     synthetic records with unit vectors (d=32), age and access age in days, a critical flag and a status
            (current / superseded / revoked). Synthetic vectors stand in for embeddings; no model is called.
  arms      A0 no decay (similarity) | A1 TTL: delete age > T | A2 LRU: keep the N most recently accessed
            | A3 rank decay: score = sim * exp(-ln2 * age / h), nothing deleted | A4 pinned TTL: A1, critical kept
            T = median record age of the split, N = floor(store / 2), h = T  (rules, not tuned values)
  guard     G0: status ignored at retrieval (soft revocation not enforced) | G1: only status == current returned
  budget    every arm returns the same top-k = 5
Exit codes: 0 ran; 1 --expect-digest given and the digest differs, or a registered control failed;
            2 COULD NOT BUILD (integrity gate failed, seal mismatch, bad arguments).

Written by Claude (Anthropic, Opus 5.5) at Chad Holland's direction, 2026-11-13. SELF-TESTED only.
"""
import argparse
import hashlib
import json
import math
import sys

import numpy as np

D = 32
K = 5
SPLITS = {"dev": {"seed": 20261113, "n": 50, "filler": 500},
          "test": {"seed": 20261114, "n": 200, "filler": 2000}}
CATS = ("current", "stale", "contradictory", "critical", "revoked", "adversarial")
CURRENT, SUPERSEDED, REVOKED = 0, 1, 2
ARMS = ("A0", "A1", "A2", "A3", "A4")
COMPETITORS = 6   # newer, related, different-key records placed around critical and adversarial targets


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- generation
def unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


class Builder:
    def __init__(self, rng):
        self.rng, self.rows, self.queries, self.next_key = rng, [], [], 0

    def key(self):
        self.next_key += 1
        return self.next_key - 1, unit(self.rng.normal(size=D))

    def near(self, base, spread):
        return unit(base + spread * self.rng.normal(size=D) / math.sqrt(D))

    def add(self, vec, key, age, access_age=None, critical=False, status=CURRENT, role=""):
        if access_age is None:
            access_age = float(self.rng.uniform(0, age))
        self.rows.append(dict(vec=vec, key=key, age=float(age), access=float(access_age),
                              critical=bool(critical), status=status, role=role))
        return len(self.rows) - 1

    def u(self, lo, hi):
        return float(self.rng.uniform(lo, hi))


def build(split, shuffle_ages=False, recent_critical=False):
    cfg = SPLITS[split]
    rng = np.random.default_rng(cfg["seed"])
    b = Builder(rng)
    for cat in CATS:
        for i in range(cfg["n"]):
            kid, kv = b.key()
            q = b.near(kv, 0.6)
            qd = dict(cat=cat, qvec=q, i=i)
            if cat == "current":
                qd["target"] = b.add(b.near(kv, 0.6), kid, b.u(0, 365), role="target")
            elif cat == "stale":
                linked = i % 2 == 0
                qd["stale"] = b.add(b.near(q, 0.25), kid, b.u(200, 365),
                                    status=SUPERSEDED if linked else CURRENT, role="stale")
                qd["target"] = b.add(b.near(kv, 0.6), kid, b.u(0, 60), role="target")
                qd["linked"] = linked
            elif cat == "contradictory":
                qd["pair"] = [b.add(b.near(kv, 0.6), kid, b.u(0, 365), role="contra"),
                              b.add(b.near(kv, 0.6), kid, b.u(0, 365), role="contra")]
            elif cat == "critical":
                age = b.u(0, 30) if recent_critical else b.u(220, 365)
                qd["target"] = b.add(b.near(q, 0.25), kid, age, access_age=age, critical=True, role="critical")
                for _ in range(COMPETITORS):
                    ck, _ = b.key()
                    b.add(b.near(q, 0.45), ck, b.u(0, 30), role="competitor")
            elif cat == "revoked":
                qd["revoked"] = b.add(b.near(q, 0.25), kid, b.u(30, 365), status=REVOKED, role="revoked")
                qd["target"] = b.add(b.near(kv, 0.6), kid, b.u(0, 30), role="target")
            elif cat == "adversarial":
                qd["target"] = b.add(b.near(q, 0.25), kid, b.u(150, 365), role="target")
                for _ in range(COMPETITORS):
                    ck, _ = b.key()
                    b.add(b.near(q, 0.45), ck, b.u(0, 30), role="distractor")
            b.queries.append(qd)
    for _ in range(cfg["filler"]):
        fk, fv = b.key()
        b.add(fv, fk, b.u(0, 365), role="filler")
    store = {
        "vec": np.array([r["vec"] for r in b.rows]),
        "age": np.array([r["age"] for r in b.rows]),
        "access": np.array([r["access"] for r in b.rows]),
        "critical": np.array([r["critical"] for r in b.rows]),
        "status": np.array([r["status"] for r in b.rows]),
        "key": np.array([r["key"] for r in b.rows]),
        "role": [r["role"] for r in b.rows],
    }
    if shuffle_ages:
        perm = np.random.default_rng(cfg["seed"] + 1).permutation(len(b.rows))
        store["age"], store["access"] = store["age"][perm], store["access"][perm]
    return store, b.queries


def canonical(store, queries):
    """Rounded, ordered bytes of the whole split, for sealing."""
    payload = {
        "vec": np.round(store["vec"], 9).tolist(), "age": np.round(store["age"], 9).tolist(),
        "access": np.round(store["access"], 9).tolist(), "critical": store["critical"].tolist(),
        "status": store["status"].tolist(), "key": store["key"].tolist(), "role": store["role"],
        "queries": [{k: (np.round(v, 9).tolist() if isinstance(v, np.ndarray) else v) for k, v in q.items()}
                    for q in queries],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def integrity_gate(store, queries, split):
    """Checker-free facts about the generated split. Any failure stops the run (exit 2)."""
    n = SPLITS[split]["n"]
    counts = {c: sum(q["cat"] == c for q in queries) for c in CATS}
    problems = [f"{c}: {counts[c]} queries, expected {n}" for c in CATS if counts[c] != n]
    T = float(np.median(store["age"]))
    crit = store["critical"]
    if not crit.any() or not (store["age"][crit] > T).all():
        problems.append("not every critical record is older than T, so A1 could keep one by accident")
    if not ((store["status"] == REVOKED).sum() == n):
        problems.append("revoked count differs from n")
    if np.abs(np.linalg.norm(store["vec"], axis=1) - 1).max() > 1e-9:
        problems.append("vectors are not unit length")
    return T, counts, problems


# ---------------------------------------------------------------- retrieval
def candidates(store, arm, T):
    n = len(store["age"])
    if arm in ("A0", "A3"):
        return np.ones(n, bool)
    if arm == "A1":
        return store["age"] <= T
    if arm == "A4":
        return (store["age"] <= T) | store["critical"]
    if arm == "A2":
        keep = np.zeros(n, bool)
        keep[np.argsort(store["access"], kind="stable")[: n // 2]] = True
        return keep
    raise ValueError(arm)


def topk(store, q, arm, guard, T, h, alive):
    sim = store["vec"] @ q
    score = sim * np.exp(-math.log(2) * store["age"] / h) if arm == "A3" else sim.copy()
    mask = alive.copy()
    if guard == "G1":
        mask &= store["status"] == CURRENT
    score = np.where(mask, score, -np.inf)
    order = np.lexsort((np.arange(len(score)), -score))[:K]
    return [int(i) for i in order if np.isfinite(score[i])]


def evaluate(store, queries, T, h, guard_override=None):
    out = {}
    for arm in ARMS:
        alive = candidates(store, arm, T)
        for guard in ("G0", "G1"):
            g = guard_override(guard) if guard_override else guard
            hits = {c: [] for c in CATS}
            for qd in queries:
                top = topk(store, qd["qvec"], arm, g, T, h, alive)
                c = qd["cat"]
                if c in ("current", "critical", "adversarial"):
                    ok = qd["target"] in top
                elif c == "stale":
                    t, s = qd["target"], qd["stale"]
                    ok = t in top and (s not in top or top.index(t) < top.index(s))
                elif c == "contradictory":
                    ok = all(r in top for r in qd["pair"])
                elif c == "revoked":
                    ok = qd["revoked"] in top          # a leak; lower is better
                hits[c].append(bool(ok))
            out[(arm, guard)] = {c: (sum(v), len(v)) for c, v in hits.items()}
            out[(arm, guard)]["keep"] = (int(alive.sum()), len(alive))
    return out


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    w = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    # Exact ends: at k = 0 the lower bound is 0 and at k = n the upper bound is 1. Floating-point rounding
    # otherwise gives about 5.6e-17 at k = 0 (found by the property test before any registered run).
    lo = 0.0 if k == 0 else max(0.0, c - w)
    hi = 1.0 if k == n else min(1.0, c + w)
    return (min(lo, p), max(hi, p))


def rate(res, arm, guard, cat):
    k, n = res[(arm, guard)][cat]
    return k / n


# ---------------------------------------------------------------- predictions and controls
def predictions(res):
    r = lambda a, c, g="G1": rate(res, a, g, c)
    p = {}
    p["P1"] = r("A1", "critical") <= 0.05 and r("A4", "critical") >= 0.95
    p["P2"] = r("A3", "stale") >= r("A1", "stale") - 0.05
    p["P3"] = r("A3", "critical") < r("A4", "critical") - 0.05
    p["P4"] = (r("A0", "revoked", "G0") > 0.5 and r("A3", "revoked", "G0") > 0.5
               and all(r(a, "revoked", "G1") == 0 for a in ARMS))
    p["P5"] = r("A0", "adversarial") >= 0.95 and r("A3", "adversarial") < r("A0", "adversarial") - 0.05
    return p


def controls(split, res, T, h, sabotage):
    out = {}
    s_store, s_q = build(split, shuffle_ages=True)
    sT = float(np.median(s_store["age"]))
    sres = evaluate(s_store, s_q, sT, sT)
    gap_real = rate(res, "A3", "G1", "stale") - rate(res, "A0", "G1", "stale")
    gap_shuf = rate(sres, "A3", "G1", "stale") - rate(sres, "A0", "G1", "stale")
    out["NC1 shuffled ages remove A3's stale advantage over A0"] = (
        abs(gap_shuf) <= 0.05, f"A3-A0 stale: real {gap_real:+.4f}, shuffled {gap_shuf:+.4f}")
    store, queries = build(split)
    alive = candidates(store, "A0", T)
    same = all(topk(store, q["qvec"], "A3", "G1", T, float("inf"), alive)
               == topk(store, q["qvec"], "A0", "G1", T, float("inf"), alive) for q in queries)
    out["NC2 h = inf gives rankings identical to A0"] = (same, f"identical top-k on {len(queries)} queries: {same}")
    bres = evaluate(store, queries, T, h, guard_override=lambda g: "G0")
    eq = all(bres[(a, "G1")]["revoked"] == res[(a, "G0")]["revoked"] for a in ARMS)
    out["NC3 a guard that passes everything leaks exactly like G0"] = (eq, f"G1-sabotaged == G0 on revoked: {eq}")
    r_store, r_q = build(split, recent_critical=True)
    rT = float(np.median(r_store["age"]))
    rres = evaluate(r_store, r_q, rT, rT)
    a1 = rate(rres, "A1", "G1", "critical")
    out["NC4 recent critical records survive TTL"] = (a1 >= 0.95, f"A1 critical with recent criticals: {a1:.4f}")
    return out


def digest(res):
    rows = {f"{a}/{g}": {c: list(v) for c, v in res[(a, g)].items()} for a in ARMS for g in ("G0", "G1")}
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


# ---------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description="MEM-DECAY-001")
    ap.add_argument("cmd", choices=("seal", "run"))
    ap.add_argument("--split", choices=tuple(SPLITS), required=True)
    ap.add_argument("--expect-seal")
    ap.add_argument("--expect-digest")
    ap.add_argument("--sabotage", action="store_true", help="G1 passes everything (P4 and NC3 must fail)")
    args = ap.parse_args(argv)

    store, queries = build(args.split)
    seal = hashlib.sha256(canonical(store, queries)).hexdigest()
    T, counts, problems = integrity_gate(store, queries, args.split)
    print(f"MEM-DECAY-001 | split={args.split} seed={SPLITS[args.split]['seed']} | python "
          f"{sys.version.split()[0]} numpy {np.__version__}")
    print(f"store {len(store['age'])} records, {len(queries)} queries "
          f"({', '.join(f'{c} {counts[c]}' for c in CATS)}); T = h = {T:.4f} days; N = {len(store['age']) // 2}; k = {K}")
    print(f"SEAL {seal}")
    if problems:
        print("COULD NOT BUILD: integrity gate failed: " + "; ".join(problems))
        return 2
    if args.expect_seal and args.expect_seal != seal:
        print(f"COULD NOT BUILD: seal mismatch (expected {args.expect_seal})")
        return 2
    if args.cmd == "seal":
        print("sealed; nothing scored")
        return 0

    h = T
    res = evaluate(store, queries, T, h, guard_override=(lambda g: "G0") if args.sabotage else None)
    print(f"\n{'arm/guard':9} " + " ".join(f"{c:>21}" for c in CATS) + "   kept")
    for a in ARMS:
        for g in ("G0", "G1"):
            cells = []
            for c in CATS:
                k, n = res[(a, g)][c]
                lo, hi = wilson(k, n)
                cells.append(f"{k:>4}/{n} {k / n:.3f} [{lo:.2f},{hi:.2f}]")
            kk, kn = res[(a, g)]["keep"]
            print(f"{a}/{g:6} " + " ".join(f"{x:>21}" for x in cells) + f"   {kk / kn:.3f}")
    print("(revoked column = leak rate: lower is better)")
    rc = 0
    if args.split == "test":
        print()
        for name, held in predictions(res).items():
            print(f"{name}  {'HELD' if held else 'REFUTED'}")
        print()
        for name, (held, detail) in controls(args.split, res, T, h, args.sabotage).items():
            print(f"{'HELD  ' if held else 'FAILED'} {name}: {detail}")
            if not held:
                rc = 1
    dg = digest(res)
    print(f"DIGEST {dg}")
    if args.expect_digest and args.expect_digest != dg:
        print(f"DIGEST MISMATCH (expected {args.expect_digest})")
        rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
