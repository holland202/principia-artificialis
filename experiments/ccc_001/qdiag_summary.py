"""Re-report stage Q's arms from the uncached path recorded by qdiag.py (QDIAG P1 refuted; M12, M6).

Reads results/ccc_001/qdiag.json and prints, per arm, mean S, mean G and modal-letter counts for the
uncached read-out (pi0) next to the cached read-out. No model is loaded; nothing is re-run.
Usage: python3 experiments/ccc_001/qdiag_summary.py [path/to/qdiag.json]
"""
import json
import os
import sys

O = "ABC"
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "../../results/ccc_001/qdiag.json")
d = json.load(open(path))
assert not d["sabotage"], "summary is for the unsabotaged run"
for label, block in (("cached", d["cached_pi0"]), ("uncached", d["uncached_pi0"])):
    for n, rows in block.items():
        S = sum(max(r["p"]) for r in rows) / len(rows)
        G = sum(r["G"] for r in rows) / len(rows)
        m = {o: sum(1 for r in rows if O[r["p"].index(max(r["p"]))] == o) for o in O}
        print(f"{label:8s} arm {n:5s} S {S:.4f} G {G:.4f} modal {m}")
