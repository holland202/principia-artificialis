"""Apply REGISTRATION.md's bar to the per-seed results. Usage: python3 score.py RESULTS_DIR
2026-11-17: loads results through guard.py (fail-closed: exactly seeds 1-6, distinct, matching config). The bar
itself is unchanged; on the real 001 results the verdicts are identical to the original scorer's."""
import sys
import engine as E
import guard
BAR = {"Q1": [("periodic_heldout_L128", .95), ("recall_L128", .95), ("copy_L128", .95)],
       "Q2": [("periodic_heldout_L256", .95), ("recall_L256", .90), ("copy_L256", .70)],
       "Q3": [("periodic_heldout_L512", .90)]}
R = guard.load_or_exit(sys.argv[1], E.CFG, [k for q in BAR.values() for k, _ in q])
print("seed " + " ".join(k for q in BAR.values() for k, _ in q))
for r in R:
    print(f"{r['seed']:>4} " + " ".join(f"{r['scores'][k]:.3f}" for q in BAR.values() for k, _ in q))
for q, rules in BAR.items():
    ok = sum(all(r["scores"][k] >= t for k, t in rules) for r in R)
    print(f"{q}: {'HELD' if ok >= 5 else 'FAILED'} ({ok}/{len(R)} seeds meet every threshold; need 5)")
