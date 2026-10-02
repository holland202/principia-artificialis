#!/usr/bin/env python3
"""
note064_reference.py -- which separations in an outcome-feedback loop prevent which false improvements?

Prints every number in research_notes/note064_governed_outcome_feedback.md. Registration (P1-P10) was
committed before this file existed (99e666d). Records are built with EBLL's own AppendOnlyStore,
DecisionRecord and OutcomeRecord (note063); arms B2/B3 read decision-time records only.

    python3 scripts/note064_reference.py

Exit 0: the run reproduces the RECORDED outcome (which predictions held, and a digest of every printed
number), including the registered failures. Exit 1: anything drifted. Stdlib only. Deterministic.
"""
import hashlib
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ebll.records import DecisionRecord, OutcomeRecord  # noqa: E402
from ebll.store import AppendOnlyStore  # noqa: E402

K, C_FEEDBACK, C_DRIFT = 12.0, 0.45, 0.75
TAU0, EPS, N_CASES, SEEDS, BOOT = 0.70, 0.2, 2000, range(100), 500
GRID = [round(0.05 * i, 2) for i in range(20)]  # 0.00 .. 0.95
CONDITIONS = ("TRUE", "NC1_RANDOM", "NC2_CORRUPTED", "NC3_MISSING", "NC6_LEAKAGE", "DRIFT")
ARMS = ("B0", "B1", "B1s", "B2", "B3")
AVAILABLE_GAIN_TRUE = None  # filled in main()


def p_success(s, c):
    return 1.0 / (1.0 + math.exp(-K * (s - c)))


def utility(tau, c, n=20001):
    """Exact-by-quadrature expected utility per new case of 'act iff s > tau', s ~ U(0,1)."""
    h, tot = 1.0 / (n - 1), 0.0
    for i in range(n):
        s = i * h
        if s > tau:
            tot += (0.5 if i in (0, n - 1) else 1.0) * (2 * p_success(s, c) - 1)
    return tot * h


# ------------------------------------------------------------------ feedback period -> EBLL store
def feedback_batch(seed, cond):
    """Same underlying cases for every condition (base stream); corruption uses its own stream."""
    base, corrupt = random.Random(seed), random.Random(10_000 + 97 * seed + CONDITIONS.index(cond))
    store, current_score = AppendOnlyStore(), {}
    for i in range(N_CASES):
        s = base.random()
        explore = base.random() < EPS
        part = ("dev" if base.random() < 0.5 else "held") if explore else "policy"
        y = base.random() < p_success(s, C_FEEDBACK)
        acted = explore or s > TAU0
        did = f"d{i}"
        store.append_decision(DecisionRecord(
            decision_id=did, agent_version=f"tau={TAU0}", proposal="act",
            available_evidence=(f"s={s!r}", f"slice={part}"),
            gate_decision="ALLOW" if acted else "DEFER", constraints=(),
            action="act" if acted else "defer", decision_timestamp=f"t{i:05d}",
            provenance="note064-synthetic"))
        current_score[did] = s
        if not acted:
            continue
        rec = y
        if cond == "NC1_RANDOM":
            rec = corrupt.random() < 0.5
        elif cond == "NC2_CORRUPTED" and 0.15 <= s < 0.45 and not y:
            rec = True
        elif cond == "NC3_MISSING" and not y and corrupt.random() < 0.6:
            rec = None
        elif cond == "NC6_LEAKAGE" and y:
            current_score[did] = min(1.0, s + 0.3)  # the system re-scores a case after it succeeds
        store.append_outcome(OutcomeRecord(
            outcome_id=f"o{i}", decision_id=did,
            observed_outcome="unrecorded" if rec is None else ("success" if rec else "failure"),
            outcome_timestamp=f"t{i:05d}+", success=rec, provenance="note064-synthetic"))
    return store, current_score


def decision_time(case):
    ev = dict(e.split("=", 1) for e in case.decision.available_evidence)
    return float(ev["s"]), ev["slice"]


# ------------------------------------------------------------------------------------ learners
def argmax_tau(pairs, score):
    """Best tau on the grid; ties go to the tau closest to TAU0 (prefer no change), then the smaller."""
    best = None
    for tau in sorted(GRID, key=lambda t: (abs(t - TAU0), t)):
        v = score(tau, pairs)
        if best is None or v > best[0]:
            best = (v, tau)
    return best[1]


def utility_score(tau, pairs):
    return sum(2 * y - 1 for s, y in pairs if s > tau)


def precision_score(tau, pairs):
    sel = [y for s, y in pairs if s > tau]
    return sum(sel) / len(sel) if sel else -1.0


def naive_pairs(store, current_score):
    """B1/B1s: every acted case, CURRENT system score, missing outcome counted as success."""
    return [(current_score[c.decision.decision_id], True if c.outcome.success is None else c.outcome.success)
            for c in store.make_learning_cases()]


def evaluated_parts(store):
    """B2/B3: decision-time score from the immutable DecisionRecord; unknown outcomes excluded."""
    learn, held = [], []
    for c in store.make_learning_cases():
        if c.outcome.success is None:
            continue
        s, part = decision_time(c)
        (held if part == "held" else learn).append((s, c.outcome.success))
    return learn, held


def completeness(store):
    acted = [d for d in store.list_decisions() if d.gate_decision == "ALLOW"]
    known = sum(1 for o in store.list_outcomes() if o.success is not None)
    return known / len(acted)


def run_arm(arm, store, current_score, seed, cond, governance=True):
    if arm == "B0":
        return TAU0
    if arm in ("B1", "B1s"):
        pairs = naive_pairs(store, current_score)
        return argmax_tau(pairs, precision_score if arm == "B1s" else utility_score)
    if arm == "B3" and governance and completeness(store) < 0.95:
        return TAU0  # completeness contract: this batch is not admissible as learning evidence
    learn, held = evaluated_parts(store)
    tau = argmax_tau(learn, utility_score)
    if tau == TAU0:
        return TAU0
    d = [((s > tau) - (s > TAU0)) * (2 * y - 1) for s, y in held]
    gain = sum(d) / len(d)
    if arm == "B2" or not governance:
        return tau if gain > 0 else TAU0
    rng = random.Random(50_000 + 97 * seed + CONDITIONS.index(cond))
    boots = sorted(sum(rng.choices(d, k=len(d))) / len(d) for _ in range(BOOT))
    return tau if boots[int(0.025 * BOOT)] > 0 else TAU0


# --------------------------------------------------------------------------------------- main
def main():
    u_cache = {}

    def U(tau, c):
        if (tau, c) not in u_cache:
            u_cache[(tau, c)] = utility(tau, c)
        return u_cache[(tau, c)]

    lines = []

    def out(line=""):
        print(line)
        lines.append(line)

    out("note064_reference.py -- governed outcome feedback (synthetic; one learned parameter: tau)")
    out(f"world: p(s)=1/(1+exp(-12(s-c))), c={C_FEEDBACK}; tau0={TAU0}; {N_CASES} feedback cases, "
        f"exploration {EPS}; {len(SEEDS)} seeds; bootstrap {BOOT}")
    out(f"U(0.70)={U(0.70, C_FEEDBACK):.4f}  U(0.45)={U(0.45, C_FEEDBACK):.4f}  available gain "
        f"{U(0.45, C_FEEDBACK) - U(0.70, C_FEEDBACK):.4f}  |  drift world c={C_DRIFT}: "
        f"U(0.70)={U(0.70, C_DRIFT):.4f} U(0.45)={U(0.45, C_DRIFT):.4f}")
    res, taus, b3_off = {}, {}, {}
    for cond in CONDITIONS:
        c_dep = C_DRIFT if cond == "DRIFT" else C_FEEDBACK
        for arm in ARMS:
            taus[(cond, arm)] = []
        b3_off[cond] = []
        comp = []
        for seed in SEEDS:
            store, cur = feedback_batch(seed, cond)
            comp.append(completeness(store))
            for arm in ARMS:
                taus[(cond, arm)].append(run_arm(arm, store, cur, seed, cond))
            b3_off[cond].append(run_arm("B3", store, cur, seed, cond, governance=False))
        base = U(TAU0, c_dep)
        out()
        out(f"[{cond}]  mean outcome completeness {sum(comp) / len(comp):.4f}  "
            f"(deployment world c={c_dep}, U(tau0)={base:.4f})")
        out(f"  {'arm':<4} {'deploy':>7} {'harmful':>8} {'mean gain':>10}  tau deployed (median)")
        for arm in ARMS:
            ts = taus[(cond, arm)]
            gains = [U(t, c_dep) - base for t in ts]
            deploy = sum(t != TAU0 for t in ts) / len(ts)
            harm = sum(g < -1e-12 for g in gains) / len(ts)
            mg = sum(gains) / len(gains)
            res[(cond, arm)] = (deploy, harm, mg)
            out(f"  {arm:<4} {deploy:>7.2f} {harm:>8.2f} {mg:>10.4f}  {sorted(ts)[len(ts) // 2]:.2f}")

    avail = U(0.45, C_FEEDBACK) - U(0.70, C_FEEDBACK)
    g = lambda c, a: res[(c, a)][2]
    h = lambda c, a: res[(c, a)][1]
    d = lambda c, a: res[(c, a)][0]
    preds = [
        ("P1  TRUE: B1, B2, B3 mean gain > 0; B3 deploys >= 0.80",
         g("TRUE", "B1") > 0 and g("TRUE", "B2") > 0 and g("TRUE", "B3") > 0 and d("TRUE", "B3") >= 0.80),
        ("P2  TRUE: |gain B1 - gain B2| <= 0.1 x available gain",
         abs(g("TRUE", "B1") - g("TRUE", "B2")) <= 0.1 * avail),
        ("P3  NC1: harm B3 <= 0.05, B1 >= 0.20, B1 >= B2 >= B3",
         h("NC1_RANDOM", "B3") <= 0.05 and h("NC1_RANDOM", "B1") >= 0.20
         and h("NC1_RANDOM", "B1") >= h("NC1_RANDOM", "B2") >= h("NC1_RANDOM", "B3")),
        ("P4  NC3: harm B1 >= 0.90; B3 deploys 0; 0 < gain B2 < its TRUE gain",
         h("NC3_MISSING", "B1") >= 0.90 and d("NC3_MISSING", "B3") == 0
         and 0 < g("NC3_MISSING", "B2") < g("TRUE", "B2")),
        ("P5  NC6: gain B1 <= 0; B2 and B3 identical to TRUE, seed by seed",
         g("NC6_LEAKAGE", "B1") <= 0 and taus[("NC6_LEAKAGE", "B2")] == taus[("TRUE", "B2")]
         and taus[("NC6_LEAKAGE", "B3")] == taus[("TRUE", "B3")]),
        ("P6  NC2 (registered FAIL of governance): harm B3 >= 0.50", h("NC2_CORRUPTED", "B3") >= 0.50),
        ("P7  DRIFT (registered FAIL of governance): harm B3 >= 0.50", h("DRIFT", "B3") >= 0.50),
        ("P8  TRUE: gain B3 <= gain B2 (price of the confidence gate)", g("TRUE", "B3") <= g("TRUE", "B2")),
        ("P9  TRUE: harm B1s (self-graded) >= 0.90", h("TRUE", "B1s") >= 0.90),
        ("P10 B0 gain 0, harm 0 everywhere; B3 with governance off == B2, seed by seed",
         all(res[(c, "B0")][1] == 0 and res[(c, "B0")][2] == 0 for c in CONDITIONS)
         and all(b3_off[c] == taus[(c, "B2")] for c in CONDITIONS)),
    ]
    out()
    out(f"price of governance (TRUE): B2 gain {g('TRUE', 'B2'):.4f} - B3 gain {g('TRUE', 'B3'):.4f} = "
        f"{g('TRUE', 'B2') - g('TRUE', 'B3'):.4f} per case ({(g('TRUE', 'B2') - g('TRUE', 'B3')) / avail:.4f}"
        f" of the available gain)")
    for name, ok in preds:
        out(f"{'AS REGISTERED' if ok else 'NOT AS REGISTERED':<18} {name}")
    held = [ok for _, ok in preds]
    out(f"VERDICT  {sum(held)} of {len(held)} as registered")

    digest = hashlib.sha256("\n".join(lines).encode()).hexdigest()
    print(f"output digest {digest}")
    if RECORDED is None:
        print("RECORDED outcome not yet pinned")
        return 0
    if (tuple(held), digest) != RECORDED:
        print("DRIFT FROM RECORDED OUTCOME: the note's numbers no longer match this run")
        return 1
    print("reproduces the recorded outcome")
    return 0


RECORDED = ((True, True, True, True, False, True, True, True, True, True),
            "04d52f1c6a146aebbd7988ae9c0cca28123ec8dca69122fa85aa59b81f3f3b1f")

if __name__ == "__main__":
    sys.exit(main())
