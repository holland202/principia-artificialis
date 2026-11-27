"""TOR-001 T6: compare two runs' saved error tables entry by entry (descriptive; not a verdict).
Usage: python -I t6_compare_runs.py RUN_A.json RUN_B.json. Claude (Anthropic, Opus 5.5), 2026-11-27. SELF-TESTED.
Both runs are Claude's, on the same code and environment, so agreement shows reproducibility, not independence (M10).
"""
import json
import sys

a = json.load(open(sys.argv[1]))["errors"]
b = json.load(open(sys.argv[2]))["errors"]
rows = [(f, m, h, a[f][m][h], b[f][m][h]) for f in a for m in a[f] for h in a[f][m]]
diff = [r for r in rows if r[3] != r[4]]
print(f"entries {len(rows)}; bitwise identical {len(rows) - len(diff)}; differing {len(diff)}")
for f, m, h, x, y in diff:
    print(f"  {f} {m} h{h}: A {x!r} B {y!r} |diff| {abs(x - y):.4g}")
