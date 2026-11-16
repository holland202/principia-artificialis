"""RMT-IH-001 analysis: timing of each statistic's change against the induction jump, by the rules frozen in
REGISTRATION.md. Usage: python3 analyze.py RUN.json. Exit 0 = analysed (verdicts printed); 2 = bad input.
Written by Claude (Anthropic, Opus 5.5), 2026-11-16. SELF-TESTED only."""
import json
import sys

import numpy as np

FRAC, PERSIST, BASE_N, FINAL_N = 0.25, 3, 5, 5
MIN_CHANGE = {"edge_r": 0.02, "top_norm": 0.023, "stable_rank": 0.57, "icl": 1.0}
RIVALS = ("top_norm", "stable_rank")


def t_change(steps, x, frac=FRAC, min_change=0.0, persist=PERSIST):
    """First step at which x has moved `frac` of its total change (baseline = mean of the first BASE_N checkpoints,
    final = mean of the last FINAL_N) and stays there for `persist` consecutive checkpoints. None if the total
    change is smaller than min_change or the condition is never met."""
    x = np.asarray(x, float)
    b, f = x[:BASE_N].mean(), x[-FINAL_N:].mean()
    d = f - b
    if abs(d) < min_change:
        return None
    hit = np.sign(d) * (x - (b + frac * d)) >= 0
    for i in range(len(x) - persist + 1):
        if hit[i:i + persist].all():
            return int(steps[i])
    return None


def change(x):
    x = np.asarray(x, float)
    return float(x[-FINAL_N:].mean() - x[:BASE_N].mean())


def per_run(rows):
    steps = [r["step"] for r in rows]
    col = lambda k: [r[k] for r in rows]
    out = {"t_ih": t_change(steps, col("icl"), 0.5, MIN_CHANGE["icl"]), "final_icl": float(np.mean(col("icl")[-FINAL_N:]))}
    for k in ("edge_r",) + RIVALS:
        out[f"d_{k}"] = change(col(k))
        out[f"t_{k}"] = t_change(steps, col(k), FRAC, MIN_CHANGE[k])
    return out


def before(a, b):
    return a is not None and b is not None and a < b


def verdicts(runs):
    rep = {k.split("/")[1]: per_run(v) for k, v in runs.items() if k.startswith("repeat/")}
    nor = {k.split("/")[1]: per_run(v) for k, v in runs.items() if k.startswith("norepeat/")}
    n = len(rep)
    v = {}
    drops = [-r["d_edge_r"] for r in rep.values()]
    v["P1"] = (float(np.mean(drops)) >= 0.02 and sum(d > 0 for d in drops) >= 4, f"mean edge drop {np.mean(drops):+.4f}; "
               f"{sum(d > 0 for d in drops)}/{n} seeds dropped")
    lead = sum(before(r["t_edge_r"], r["t_ih"]) for r in rep.values())
    v["P2"] = (lead >= 5, f"edge before induction jump in {lead}/{n} seeds")
    beats = sum(all(before(r["t_edge_r"], r[f"t_{k}"]) for k in RIVALS) for r in rep.values())
    v["P3"] = (beats >= 5, f"edge before both rivals in {beats}/{n} seeds")
    nd = float(np.mean([-r["d_edge_r"] for r in nor.values()])) if nor else float("nan")
    v["P4"] = (nd < 0.5 * float(np.mean(drops)), f"no-repeat mean edge drop {nd:+.4f} vs half the repeat drop "
               f"{0.5 * np.mean(drops):+.4f}")
    v["C3"] = (all(r["final_icl"] < 0.1 for r in nor.values()) and all(r["final_icl"] > 3.0 for r in rep.values()),
               "no-repeat final icl " + ", ".join(f"{r['final_icl']:.3f}" for r in nor.values()) +
               "; repeat final icl " + ", ".join(f"{r['final_icl']:.2f}" for r in rep.values()))
    return rep, nor, v


if __name__ == "__main__":
    try:
        data = json.load(open(sys.argv[1]))
    except Exception as e:  # noqa: BLE001
        print("cannot read", e)
        sys.exit(2)
    rep, nor, v = verdicts(data["runs"])
    print("seed  t_ih  t_edge  t_top  t_srank  d_edge   d_top   d_srank  final_icl   (repeat arm)")
    for s, r in rep.items():
        print(f"{s:>4}  {r['t_ih']}  {r['t_edge_r']}  {r['t_top_norm']}  {r['t_stable_rank']}  {r['d_edge_r']:+.4f}  "
              f"{r['d_top_norm']:+.4f}  {r['d_stable_rank']:+.3f}  {r['final_icl']:.3f}")
    print("no-repeat arm:")
    for s, r in nor.items():
        print(f"{s:>4}  t_ih {r['t_ih']}  d_edge {r['d_edge_r']:+.4f}  d_top {r['d_top_norm']:+.4f}  "
              f"d_srank {r['d_stable_rank']:+.3f}  final_icl {r['final_icl']:.3f}")
    # Post-run fix (2026-11-16): REGISTRATION.md says P2 and P3 are NOT TESTABLE when P1 fails; the frozen script
    # did not enforce that gate and printed P2 HELD. The gate is applied here; the raw counts are still printed.
    for k, (ok, why) in v.items():
        label = "HELD" if ok else "FAILED"
        if k in ("P2", "P3") and not v["P1"][0]:
            label = "NOT TESTABLE (P1 failed; raw count shown)"
        print(f"{k}: {label}  ({why})")
    print("DIGEST", data.get("digest"))
