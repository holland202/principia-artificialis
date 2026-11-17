"""Apply REGISTRATION_002.md's bar. Usage: python3 score2.py RESULTS_DIR"""
import json, sys
from pathlib import Path
R = [json.loads(p.read_text()) for p in sorted(Path(sys.argv[1]).glob("seed*.json"), key=lambda p: int(p.stem[4:]))]
BAR = {"Q1": [(f"{t}_L128", .95) for t in ("periodic_heldout", "recall", "copy")],
       "Q2": [(f"{t}_L256", .95) for t in ("periodic_heldout", "recall", "copy")],
       "Q3": [(f"{t}_L512", .95) for t in ("periodic_heldout", "recall", "copy")],
       "Q4": [("periodic_heldout_L1024", .90), ("recall_L1024", .90)]}
cols = [k for q in BAR.values() for k, _ in q]
print("seed " + " ".join(cols))
for r in R:
    print(f"{r['seed']:>4} " + " ".join(f"{r['scores'][k]:.3f}" for k in cols))
for q, rules in BAR.items():
    ok = sum(all(r["scores"][k] >= t for k, t in rules) for r in R)
    print(f"{q}: {'HELD' if ok >= 5 else 'FAILED'} ({ok}/{len(R)} seeds meet every threshold; need 5)")
