"""Apply REGISTRATION.md's bar to the per-seed results. Usage: python3 score.py RESULTS_DIR"""
import json, sys
from pathlib import Path
R = [json.loads(p.read_text()) for p in sorted(Path(sys.argv[1]).glob("seed*.json"), key=lambda p: int(p.stem[4:]))]
BAR = {"Q1": [("periodic_heldout_L128", .95), ("recall_L128", .95), ("copy_L128", .95)],
       "Q2": [("periodic_heldout_L256", .95), ("recall_L256", .90), ("copy_L256", .70)],
       "Q3": [("periodic_heldout_L512", .90)]}
print("seed " + " ".join(k for q in BAR.values() for k, _ in q))
for r in R:
    print(f"{r['seed']:>4} " + " ".join(f"{r['scores'][k]:.3f}" for q in BAR.values() for k, _ in q))
for q, rules in BAR.items():
    ok = sum(all(r["scores"][k] >= t for k, t in rules) for r in R)
    print(f"{q}: {'HELD' if ok >= 5 else 'FAILED'} ({ok}/{len(R)} seeds meet every threshold; need 5)")
