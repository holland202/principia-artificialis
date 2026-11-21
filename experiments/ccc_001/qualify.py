"""CCC-001 stage Q harness. Registration: QUALIFICATION_PREREG.md (commit ec1c422).

Usage: python3 experiments/ccc_001/qualify.py [--sabotage] [--json results/ccc_001/qualify.json]
Exit 0 only if Q1-Q4 hold as registered (and, once pinned, match RECORDED).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import EXPLICIT, digest, load, measure, n_tokens, summary, weather_filler  # noqa: E402
from probes import OPTIONS  # noqa: E402

RECORDED = ((True, False, True, True), "fa3e9cef237fb058c31205d86e346a7dee72ad1fddb0975d281b9f123ad9d38b")  # pinned after the run at its commit

ap = argparse.ArgumentParser()
ap.add_argument("--sabotage", action="store_true")
ap.add_argument("--json")
a = ap.parse_args()

tok, model = load()
arms = {"D": [], "E": EXPLICIT, "F16": weather_filler(16), "F64": weather_filler(64),
        "EF64": EXPLICIT + weather_filler(64)}
res = {}
for name, ctx in arms.items():
    res[name] = measure(tok, model, ctx, sabotage=a.sabotage)
    s = summary(res[name])
    print(f"arm {name:5s} ctx_tokens {n_tokens(tok, ctx):5d}  S {s['S']:.4f}  G {s['G']:.4f}  modal {s['modal']}")
repeats = [res["D"]] + [measure(tok, model, [], sabotage=a.sabotage) for _ in range(2)]

held = []
q1 = all(r == repeats[0] for r in repeats[1:])
held.append(q1)
print("Q1", "HELD" if q1 else "REFUTED", "D measured 3 times, identical to 6 dp:", q1)

gD = [r["G"] for r in res["D"]]
gE = [r["G"] for r in res["E"]]
diff = round(sum(gE) / 24 - sum(gD) / 24, 4)
wins = sum(1 for x, y in zip(gE, gD) if x > y)
q2 = diff >= 0.10 and wins >= 14
held.append(q2)
print("Q2", "HELD" if q2 else "REFUTED", f"mean G(E)-G(D) = {diff:.4f} (>= 0.10), E>D on {wins} of 24 (>= 14)")

flat = all(r["S"] == 0.333333 and r["G"] == 0.333333 for arm in res.values() for r in arm)
q3 = (not a.sabotage) or (flat and not q2)
held.append(q3)
print("Q3", "HELD" if q3 else "REFUTED",
      "sabotage run: all S=G=0.333333 and Q2 refuted" if a.sabotage else "(fires only under --sabotage)")

match = sum(1 for r in res["E"] if OPTIONS[r["p"].index(max(r["p"]))] == r["key"])
q4 = match >= 12
held.append(q4)
print("Q4", "HELD" if q4 else "REFUTED", f"E modal letter = key on {match} of 24 (>= 12)")

canon = {k: [[round(x, 4) for x in r["p"]] for r in v] for k, v in res.items()}
d = digest(canon)
n = sum(held)
print(f"VERDICT {n} of 4 as registered")
print("DIGEST", d)
if a.json:
    json.dump({"arms": res, "held": held, "digest": d, "sabotage": a.sabotage}, open(a.json, "w"), indent=1)
if a.sabotage:
    ok = False
elif RECORDED is not None:
    ok = (tuple(held), d) == RECORDED  # exit 0 only on the recorded outcome (W4)
else:
    ok = all(held)
sys.exit(0 if ok else 1)
