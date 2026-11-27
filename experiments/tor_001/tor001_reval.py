"""TOR-001 re-evaluation (deviation, disclosed): apply decide() from tor001.py to the error table saved by the approved
run at 36d5d4a (results/tor_001/tor001_results_36d5d4a.json). Gates are read from that run's own log
(results/tor_001/run_36d5d4a.txt): "G1 HELD" and three "interface: ... True" lines. Nothing is trained or scored here.
Why: that run returned row 1 because gen() handed G1 to decide() as numpy.bool, which the fail-closed 'is True' check
rejects. Claude (Anthropic, Opus 5.5), 2026-11-27. SELF-TESTED only.
usage: python3 tor001_reval.py RESULTS_JSON RUN_LOG
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tor001 as T  # noqa: E402

js, log = sys.argv[1], sys.argv[2]
for p in (js, log, T.__file__):
    print(os.path.basename(p), "sha256", hashlib.sha256(open(p, "rb").read()).hexdigest())
lines = open(log).read().splitlines()
g1 = "G1 HELD" in lines
inter = [ln for ln in lines if ln.startswith("interface:")]
order = len(inter) == 3 and all(ln.endswith("True") for ln in inter)
print("gates read from the run log: G1", g1, "| interface lines", len(inter), "all True", order)
raw = json.load(open(js))["errors"]
E = {f: {a: {int(h): float(v) for h, v in hs.items()} for a, hs in arms.items()} for f, arms in raw.items()}
if not T.selftest():
    sys.exit("decide() selftest failed")
row, outcome, P = T.decide(E, {"G1": g1, "order": order})
med = lambda f, a, h: T.med(E[f], a, h)  # noqa: E731
print(f"P1 inputs: F1 L4 h1000 {E['F1']['L4'][1000]:.4f}")
print(f"P2 inputs: F2 T2 h1000 median {med('F2', 'T2', 1000):.4f}; K4 median {med('F2', 'K4', 1000):.4f}; "
      f"L4 {E['F2']['L4'][1000]:.4f}")
print(f"P3 inputs: F2 L* h1000 {E['F2']['L*'][1000]:.4f}")
print(f"P4 inputs: F2 E2 h1 median {med('F2', 'E2', 1):.4f}; T2 h1 median {med('F2', 'T2', 1):.4f}")
print(f"P5 inputs: F3 T2 h100 median {med('F3', 'T2', 100):.4f}")
print(f"P6 inputs: F2 NP h1000 median {med('F2', 'NP', 1000):.4f}; paired T2<NP per seed "
      f"{[E['F2'][f'T2/{s}'][1000] < E['F2'][f'NP/{s}'][1000] for s in T.SEEDS]}")
for k, v in P.items():
    print(f"{k}: {'HELD' if v else 'REFUTED'}")
print(f"VERDICT (re-evaluated) row {row}: {outcome}")
