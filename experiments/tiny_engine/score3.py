"""Apply REGISTRATION_003.md. Usage: python3 score3.py RESULTS_DIR (containing A/ and B/). Fail-closed via guard.py:
exactly seeds 11-16 in each arm, matching configs, distinct results; otherwise exit 2 and no verdict.
Claude (Anthropic, Opus 5.5), 2026-11-20. SELF-TESTED only."""
import sys
from pathlib import Path
import engine as E
import guard
SEEDS = (11, 12, 13, 14, 15, 16)
BAR002 = [(f"{t}_L{L}", .95) for L in (128, 256, 512) for t in ("periodic_heldout", "recall", "copy")] + \
         [("periodic_heldout_L1024", .90), ("recall_L1024", .90)]
KEYS = [k for k, _ in BAR002] + ["tf_alpha8_k63", "tf_alpha8_k127", "free_distinct_k127"]
d = Path(sys.argv[1])
try:
    A = guard.load(d / "A", E.CFG2, KEYS, SEEDS)
    B = guard.load(d / "B", E.CFG3, KEYS, SEEDS)
except guard.InvalidResults as e:
    print(f"INVALID RESULT SET, no verdict: {e}"); sys.exit(2)
a = {r["seed"]: r["scores"] for r in A}; b = {r["seed"]: r["scores"] for r in B}
for k in ("tf_alpha8_k63", "tf_alpha8_k127", "free_distinct_k127"):
    print(k, " ".join(f"{s}:A{a[s][k]:.3f}/B{b[s][k]:.3f}" for s in SEEDS))
P = {"P1 B>A tf_alpha8_k63": sum(b[s]["tf_alpha8_k63"] > a[s]["tf_alpha8_k63"] for s in SEEDS),
     "P2 B>A free_distinct_k127": sum(b[s]["free_distinct_k127"] > a[s]["free_distinct_k127"] for s in SEEDS),
     "P3 B meets the 002 bar": sum(all(b[s][k] >= t for k, t in BAR002) for s in SEEDS),
     "P4 B tf_alpha8_k127 < 0.90": sum(b[s]["tf_alpha8_k127"] < .90 for s in SEEDS)}
for name, n in P.items():
    print(f"{name}: {'HELD' if n >= 5 else 'FAILED'} ({n}/6 seeds; need 5)")
