"""Score a CST-001 outputs file per arm (pairs correct, each version, malformed, by hop) and the A-vs-others
discordant pairs. Usage: python3 experiments/cst_001/analyze.py dev results/cst_001/dev_outputs.jsonl"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cases  # noqa: E402
import scorer  # noqa: E402

split, path = sys.argv[1], sys.argv[2]
pairs = cases.build(split, {"dev": 2, "test": 4}[split])
by_arm = {}
lens = Counter()
for line in open(path):
    r = json.loads(line)
    by_arm.setdefault(r["arm"], {})[(r["pair"], r["version"])] = r["output"]
    lens[(r["arm"], r["new_tokens"] > 20)] += 1
rows = {}
print(f"split {split}: {len(pairs)} pairs")
print(f"{'arm':3} {'pairs ok':>9} {'SHARED ok':>10} {'INDEP ok':>9} {'malformed':>9} {'hop1 pairs':>10} {'hop2 pairs':>10}"
      f" {'long answers':>12}")
for arm in sorted(by_arm):
    rs, t = scorer.score(pairs, by_arm[arm])
    rows[arm] = {r["pair"]: r["pair_correct"] for r in rs}
    h1 = sum(r["pair_correct"] for r in rs if r["hop"] == 1)
    h2 = sum(r["pair_correct"] for r in rs if r["hop"] == 2)
    n = len(rs)
    print(f"{arm:3} {t['pair_correct']:>4}/{n:<4} {t['shared_correct']:>5}/{n:<4} {t['independent_correct']:>4}/{n:<4}"
          f" {t['malformed']:>9} {h1:>6}/{n // 2:<3} {h2:>6}/{n // 2:<3} {lens[(arm, True)]:>12}")
print("\ndiscordant pairs against A (A right & other wrong / A wrong & other right):")
for other in sorted(rows):
    if other == "A":
        continue
    b = sum(rows["A"][k] and not rows[other][k] for k in rows["A"])
    c = sum(not rows["A"][k] and rows[other][k] for k in rows["A"])
    print(f"  A vs {other}: {b} / {c}")
