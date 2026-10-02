#!/usr/bin/env python3
"""
note065_reference.py -- can the outcome-source dependency be removed, or only moved?

Prints every number in research_notes/note065_outcome_source_dependency.md. Registration (Q1-Q8) was
committed before this file existed (2c4cb6d). Same world and loop as note064; outcome reports are stored as
EBLL OutcomeRecords, one per source, with the source's declared root in `provenance`.

    python3 scripts/note065_reference.py

Exit 0: the run reproduces the RECORDED outcome (which predictions held + digest of every printed number).
Exit 1: drift. Stdlib only. Deterministic. Bootstrap randomness is seeded by seed and arm, never by condition.
"""
import hashlib
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ebll.records import DecisionRecord, OutcomeRecord  # noqa: E402
from ebll.store import AppendOnlyStore  # noqa: E402

K, C_TRUE, TAU0, EPS, N_CASES, SEEDS, BOOT = 12.0, 0.45, 0.70, 0.2, 2000, range(100), 500
ETA, K_LEARN, K_HELD = 0.05, 100, 50
BAND_MIN, BAND_ALARM = 30, 0.25
GRID = [round(0.05 * i, 2) for i in range(20)]
CONDITIONS = ("CLEAN", "ONE_CORRUPT", "COMMON_DECLARED", "COMMON_HIDDEN", "AUDIT_AWARE", "GOLD_CORRUPT")
ARMS = ("NONE", "R0", "R1f", "R1a", "R2m", "R2r", "R3v", "R3c")
EXTRA = ("R3c_off",)  # anti-vacuity: R3c with the rectifier switched off (gold replaced by the cheap label)


def p_success(s, c=C_TRUE):
    return 1.0 / (1.0 + math.exp(-K * (s - c)))


def utility(tau, c=C_TRUE, n=20001):
    h, tot = 1.0 / (n - 1), 0.0
    for i in range(n):
        s = i * h
        if s > tau:
            tot += (0.5 if i in (0, n - 1) else 1.0) * (2 * p_success(s, c) - 1)
    return tot * h


def corrupted(y, s):
    return True if (0.15 <= s < 0.45 and not y) else y


# ------------------------------------------------------------------------- the world (shared draws)
def world(seed):
    """Same underlying cases as note064 (identical draw order), plus per-source noise and the audit draw."""
    base = random.Random(seed)
    cases = []
    for i in range(N_CASES):
        s = base.random()
        explore = base.random() < EPS
        part = ("dev" if base.random() < 0.5 else "held") if explore else "policy"
        y = base.random() < p_success(s)
        cases.append({"i": i, "s": s, "part": part, "y": y, "acted": explore or s > TAU0})
    acted = [c for c in cases if c["acted"]]
    noise = {j: random.Random(100_000 + 10 * seed + j) for j in (1, 2, 3)}
    for c in acted:
        c["flip"] = {j: noise[j].random() < ETA for j in (1, 2, 3)}
    audit = random.Random(200_000 + seed)
    learn = sorted(c["i"] for c in acted if c["part"] != "held")
    held = sorted(c["i"] for c in acted if c["part"] == "held")
    audited = set(audit.sample(learn, K_LEARN)) | set(audit.sample(held, K_HELD))
    for c in acted:
        c["audited"] = c["i"] in audited
    return cases


def batch(cases, cond):
    """Write decisions and every source's report into an EBLL store; return per-case report tables."""
    store = AppendOnlyStore()
    a_corrupt = cond != "CLEAN"
    roots = {1: "A", 2: "A" if cond == "COMMON_DECLARED" else "B", 3: "C"}
    for c in cases:
        did = f"d{c['i']}"
        store.append_decision(DecisionRecord(
            decision_id=did, agent_version=f"tau={TAU0}", proposal="act",
            available_evidence=(f"s={c['s']!r}", f"slice={c['part']}"),
            gate_decision="ALLOW" if c["acted"] else "DEFER", constraints=(),
            action="act" if c["acted"] else "defer", decision_timestamp=f"t{c['i']:05d}",
            provenance="note065-synthetic"))
        if not c["acted"]:
            continue
        y, s = c["y"], c["s"]
        up_a = corrupted(y, s) if a_corrupt else y
        # what src1 reports when it can see which cases are audited (only R3v's world exposes that)
        up_a_vis = (y if c["audited"] else corrupted(y, s)) if cond == "AUDIT_AWARE" else up_a
        up = {1: up_a, 2: up_a if cond in ("COMMON_DECLARED", "COMMON_HIDDEN") else y, 3: y}
        reps = {f"src{j}": up[j] != c["flip"][j] for j in (1, 2, 3)}
        reps["src1v"] = up_a_vis != c["flip"][1]
        for name, val in reps.items():
            store.append_outcome(OutcomeRecord(
                outcome_id=f"o{c['i']}{name}", decision_id=did, observed_outcome="success" if val else "failure",
                outcome_timestamp=f"t{c['i']:05d}+", success=val,
                provenance=f"root={roots[int(name[3])]}", source=name))
        if c["audited"]:
            g = corrupted(y, s) if cond == "GOLD_CORRUPT" else y
            store.append_outcome(OutcomeRecord(
                outcome_id=f"o{c['i']}gold", decision_id=did, observed_outcome="success" if g else "failure",
                outcome_timestamp=f"t{c['i']:05d}++", success=g, provenance="root=GOLD", source="gold"))
    # read everything back from the store: decision-time score and slice, every source's report and root
    rows, root_of = {}, {}
    for lc in store.make_learning_cases():
        d, o = lc.decision, lc.outcome
        ev = dict(e.split("=", 1) for e in d.available_evidence)
        row = rows.setdefault(d.decision_id, {"s": float(ev["s"]), "part": ev["slice"], "rep": {}})
        row["rep"][o.source] = o.success
        root_of[o.source] = o.provenance.split("=", 1)[1]
    return list(rows.values()), root_of


# ------------------------------------------------------------------------------------- the loop
def argmax_tau(score):
    best = None
    for tau in sorted(GRID, key=lambda t: (abs(t - TAU0), t)):
        v = score(tau)
        if best is None or v > best[0]:
            best = (v, tau)
    return best[1]


def learn(pairs):
    return argmax_tau(lambda tau: sum(2 * y - 1 for s, y in pairs if s > tau))


def diffs(tau, pairs):
    return [((s > tau) - (s > TAU0)) * (2 * y - 1) for s, y in pairs]


def boot_lb(rng, a, b=None):
    """Lower 2.5% bootstrap bound of mean(a) - mean(b) (b resampled independently; b=None -> mean(a))."""
    vals = []
    for _ in range(BOOT):
        v = sum(rng.choices(a, k=len(a))) / len(a)
        if b:
            v -= sum(rng.choices(b, k=len(b))) / len(b)
        vals.append(v)
    return sorted(vals)[int(0.025 * BOOT)]


def run_labels(rows, label, seed, arm_index):
    """Learn on learning slices, evaluate on held-out, deploy only if the bootstrap lower bound > 0."""
    learn_pairs, held_pairs = [], []
    for r in rows:
        y = label(r)
        if y is None:
            continue
        (held_pairs if r["part"] == "held" else learn_pairs).append((r["s"], y))
    tau = learn(learn_pairs)
    if tau == TAU0 or not held_pairs:
        return TAU0
    return tau if boot_lb(random.Random(300_000 + 1000 * seed + arm_index), diffs(tau, held_pairs)) > 0 else TAU0


def alarm(rows, a, b):
    bands = {}
    for r in rows:
        n_dis = bands.setdefault(min(int(r["s"] * 10), 9), [0, 0])
        n_dis[0] += 1
        n_dis[1] += r["rep"][a] != r["rep"][b]
    return any(n >= BAND_MIN and dis / n >= BAND_ALARM for n, dis in bands.values())


def agree(a, b):
    return lambda r: r["rep"][a] if r["rep"][a] == r["rep"][b] else None


def majority(r):
    return (r["rep"]["src1"] + r["rep"]["src2"] + r["rep"]["src3"]) >= 2


def run_pair_with_alarm(rows, a, b, seed, idx):
    return TAU0 if alarm(rows, a, b) else run_labels(rows, agree(a, b), seed, idx)


def run_ppi(rows, cheap, seed, idx, rectify=True):
    """Prediction-powered: cheap labels everywhere, gold on the audited subset rectifies the bias."""
    learn_rows = [r for r in rows if r["part"] != "held"]
    held_rows = [r for r in rows if r["part"] == "held"]
    gold = lambda r: r["rep"]["gold"] if rectify else r["rep"][cheap]
    aud_learn = [r for r in learn_rows if "gold" in r["rep"]]
    scale = len(learn_rows) / len(aud_learn)

    def score(tau):
        tot = sum(2 * r["rep"][cheap] - 1 for r in learn_rows if r["s"] > tau)
        rect = sum((2 * r["rep"][cheap] - 1) - (2 * gold(r) - 1) for r in aud_learn if r["s"] > tau)
        return tot - scale * rect

    tau = argmax_tau(score)
    if tau == TAU0:
        return TAU0
    d_cheap = diffs(tau, [(r["s"], r["rep"][cheap]) for r in held_rows])
    aud_held = [r for r in held_rows if "gold" in r["rep"]]
    rect = [dc - dg for dc, dg in zip(diffs(tau, [(r["s"], r["rep"][cheap]) for r in aud_held]),
                                      diffs(tau, [(r["s"], gold(r)) for r in aud_held]))]
    lb = boot_lb(random.Random(300_000 + 1000 * seed + idx), d_cheap, rect)
    return tau if lb > 0 else TAU0


def run_arm(arm, rows, root_of, seed):
    idx = (ARMS + EXTRA).index(arm)
    if arm == "NONE":
        return TAU0
    if arm == "R0":
        return run_labels(rows, lambda r: r["rep"]["src1"], seed, idx)
    if arm == "R1f":
        return run_labels(rows, agree("src1", "src2"), seed, idx)
    if arm == "R1a":
        return run_pair_with_alarm(rows, "src1", "src2", seed, idx)
    if arm == "R2m":
        return run_labels(rows, majority, seed, idx)
    if arm == "R2r":
        reps = {}
        for src in ("src1", "src2", "src3"):
            reps.setdefault(root_of[src], src)  # one representative (lowest-numbered source) per root
        if len(reps) >= 3:
            return run_labels(rows, majority, seed, idx)
        a, b = sorted(reps.values())[:2]
        return run_pair_with_alarm(rows, a, b, seed, idx)
    if arm == "R3v":
        return run_ppi(rows, "src1v", seed, idx)
    if arm == "R3c":
        return run_ppi(rows, "src1", seed, idx)
    if arm == "R3c_off":
        return run_ppi(rows, "src1", seed, idx, rectify=False)
    raise ValueError(arm)


def observations(arm, rows):
    n = len(rows)
    gold = sum(1 for r in rows if "gold" in r["rep"])
    return {"NONE": 0, "R0": n, "R1f": 2 * n, "R1a": 2 * n, "R2m": 3 * n, "R2r": 3 * n,
            "R3v": n + gold, "R3c": n + gold, "R3c_off": n}[arm]


def main():
    lines = []

    def out(line=""):
        print(line)
        lines.append(line)

    u = {t: utility(t) for t in GRID}
    base_u = u[TAU0]
    avail = u[0.45] - base_u
    out("note065_reference.py -- outcome-source dependency (synthetic; note064 world; one learned parameter)")
    out(f"world as note064: U(0.70)={base_u:.4f} U(0.45)={u[0.45]:.4f} available gain {avail:.4f}; "
        f"source noise eta={ETA}; gold audits {K_LEARN}+{K_HELD}; alarm band>={BAND_MIN} cases, "
        f"disagreement>={BAND_ALARM}; {len(SEEDS)} seeds; bootstrap {BOOT}")
    # Added after the first run (diagnostic only; no computation changed): where harm begins on the grid.
    out("utility by tau: " + "  ".join(f"U({t:.2f})={u[t]:.4f}" for t in (0.15, 0.20, 0.25, 0.30, 0.45)) +
        f"  (harmful = below U(0.70)={base_u:.4f})")
    worlds = {seed: world(seed) for seed in SEEDS}
    taus, res, obs = {}, {}, {}
    for cond in CONDITIONS:
        for arm in ARMS + EXTRA:
            taus[(cond, arm)] = []
            obs[(cond, arm)] = []
        for seed in SEEDS:
            rows, root_of = batch(worlds[seed], cond)
            for arm in ARMS + EXTRA:
                taus[(cond, arm)].append(run_arm(arm, rows, root_of, seed))
                obs[(cond, arm)].append(observations(arm, rows))
        out()
        out(f"[{cond}]")
        out(f"  {'arm':<8} {'deploy':>7} {'harmful':>8} {'mean gain':>10}  {'tau (median)':>12}  observations/batch")
        for arm in ARMS + EXTRA:
            ts = taus[(cond, arm)]
            gains = [u[t] - base_u for t in ts]
            deploy = sum(t != TAU0 for t in ts) / len(ts)
            harm = sum(g < -1e-12 for g in gains) / len(ts)
            mg = sum(gains) / len(gains)
            res[(cond, arm)] = (deploy, harm, mg)
            mo = sum(obs[(cond, arm)]) / len(obs[(cond, arm)])
            out(f"  {arm:<8} {deploy:>7.2f} {harm:>8.2f} {mg:>10.4f}  {sorted(ts)[len(ts) // 2]:>12.2f}  {mo:.1f}")

    d = lambda c, a: res[(c, a)][0]
    h = lambda c, a: res[(c, a)][1]
    g = lambda c, a: res[(c, a)][2]
    same = lambda c1, c2, a: taus[(c1, a)] == taus[(c2, a)]
    learners = [a for a in ARMS if a != "NONE"]
    preds = [
        ("Q1 CLEAN: every learning arm gain > 0 and harm <= 0.05; NONE gain 0",
         all(g("CLEAN", a) > 0 and h("CLEAN", a) <= 0.05 for a in learners) and g("CLEAN", "NONE") == 0),
        ("Q2 ONE_CORRUPT: R0, R1f harm >= 0.90; R1a deploy <= 0.05; R2m, R2r harm <= 0.05 and gain >= 0.8 x own CLEAN; "
         "R3v, R3c harm <= 0.05 and gain > 0",
         h("ONE_CORRUPT", "R0") >= 0.90 and h("ONE_CORRUPT", "R1f") >= 0.90 and d("ONE_CORRUPT", "R1a") <= 0.05
         and all(h("ONE_CORRUPT", a) <= 0.05 and g("ONE_CORRUPT", a) >= 0.8 * g("CLEAN", a) for a in ("R2m", "R2r"))
         and all(h("ONE_CORRUPT", a) <= 0.05 and g("ONE_CORRUPT", a) > 0 for a in ("R3v", "R3c"))),
        ("Q3 COMMON_DECLARED: R2m harm >= 0.90; R2r deploy <= 0.05; R3c identical to ONE_CORRUPT",
         h("COMMON_DECLARED", "R2m") >= 0.90 and d("COMMON_DECLARED", "R2r") <= 0.05
         and same("COMMON_DECLARED", "ONE_CORRUPT", "R3c")),
        ("Q4 COMMON_HIDDEN (registered FAIL of root counting): R2r harm >= 0.90; R3c identical to ONE_CORRUPT",
         h("COMMON_HIDDEN", "R2r") >= 0.90 and same("COMMON_HIDDEN", "ONE_CORRUPT", "R3c")),
        ("Q5 AUDIT_AWARE: R3v harm >= 0.90; R3c identical to ONE_CORRUPT",
         h("AUDIT_AWARE", "R3v") >= 0.90 and same("AUDIT_AWARE", "ONE_CORRUPT", "R3c")),
        ("Q6 GOLD_CORRUPT (registered FAIL of auditing): R3c harm >= 0.90; R2m identical to ONE_CORRUPT",
         h("GOLD_CORRUPT", "R3c") >= 0.90 and same("GOLD_CORRUPT", "ONE_CORRUPT", "R2m")),
        ("Q7 CLEAN: gain R3c <= gain R0 (price of the audit)", g("CLEAN", "R3c") <= g("CLEAN", "R0")),
        ("Q8 ONE_CORRUPT: R3c_off harm >= 0.90; NONE gain 0 and harm 0 everywhere",
         h("ONE_CORRUPT", "R3c_off") >= 0.90
         and all(g(c, "NONE") == 0 and h(c, "NONE") == 0 for c in CONDITIONS)),
    ]
    out()
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


RECORDED = ((True, False, True, True, True, True, True, True),
            "bfa4d689c2e3429b45eb71d3b95c3e205e26e2bab0baa1aad19a33b16cbfd3c3")

if __name__ == "__main__":
    sys.exit(main())
