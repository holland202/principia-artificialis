"""Apply REGISTRATION_002.md's bar. Usage: python3 score2.py RESULTS_DIR
2026-11-17: loads results through guard.py (fail-closed: exactly seeds 1-6, distinct, matching config). The bar
itself is unchanged."""
import sys
import engine as E
import guard
BAR = {"Q1": [(f"{t}_L128", .95) for t in ("periodic_heldout", "recall", "copy")],
       "Q2": [(f"{t}_L256", .95) for t in ("periodic_heldout", "recall", "copy")],
       "Q3": [(f"{t}_L512", .95) for t in ("periodic_heldout", "recall", "copy")],
       "Q4": [("periodic_heldout_L1024", .90), ("recall_L1024", .90)]}
cols = [k for q in BAR.values() for k, _ in q]
R = guard.load_or_exit(sys.argv[1], E.CFG2, cols)
print("seed " + " ".join(cols))
for r in R:
    print(f"{r['seed']:>4} " + " ".join(f"{r['scores'][k]:.3f}" for k in cols))
for q, rules in BAR.items():
    ok = sum(all(r["scores"][k] >= t for k, t in rules) for r in R)
    print(f"{q}: {'HELD' if ok >= 5 else 'FAILED'} ({ok}/{len(R)} seeds meet every threshold; need 5)")
