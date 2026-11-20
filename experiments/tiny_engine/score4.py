"""Apply REGISTRATION_004.md. Usage: python3 score4.py RESULTS_DIR (containing A/, B/, C/). Fail-closed via guard.py:
exactly seeds 21-26 in each arm with that arm's config; otherwise exit 2 and no verdict.
Claude (Anthropic, Opus 5.5), 2026-11-20. SELF-TESTED only."""
import sys
from pathlib import Path
import engine as E
import guard
SEEDS = (21, 22, 23, 24, 25, 26)
BAR002 = [(f"{t}_L{L}", .95) for L in (128, 256, 512) for t in ("periodic_heldout", "recall", "copy")] + \
         [("periodic_heldout_L1024", .90), ("recall_L1024", .90)]
KEYS = [k for k, _ in BAR002] + ["tf_alpha8_k127", "free_alpha8_k63", "tf_alpha8_k127_uncoupled"]
d = Path(sys.argv[1])
try:
    R = {a: {r["seed"]: r["scores"] for r in guard.load(d / a, c, KEYS, SEEDS)}
         for a, c in (("A", E.CFG3), ("B", E.CFG4B), ("C", E.CFG4C))}
except guard.InvalidResults as e:
    print(f"INVALID RESULT SET, no verdict: {e}"); sys.exit(2)
A, B, C = R["A"], R["B"], R["C"]
for k in ("tf_alpha8_k127", "free_alpha8_k63", "tf_alpha8_k127_uncoupled"):
    print(k, " ".join(f"{s}:A{A[s][k]:.3f}/B{B[s][k]:.3f}/C{C[s][k]:.3f}" for s in SEEDS))
P = {"P1 C>B tf_alpha8_k127 (coupling isolated)": sum(C[s]["tf_alpha8_k127"] > B[s]["tf_alpha8_k127"] for s in SEEDS),
     "P2 C tf_alpha8_k127 >= 0.95": sum(C[s]["tf_alpha8_k127"] >= .95 for s in SEEDS),
     "P3 C free_alpha8_k63 >= 0.50": sum(C[s]["free_alpha8_k63"] >= .50 for s in SEEDS),
     "P4 C meets the 002 bar": sum(all(C[s][k] >= t for k, t in BAR002) for s in SEEDS),
     "P5 B<A tf_alpha8_k127 (label alone hurts)": sum(B[s]["tf_alpha8_k127"] < A[s]["tf_alpha8_k127"] for s in SEEDS),
     "P6 C uncoupled tf_alpha8_k127 < 0.50": sum(C[s]["tf_alpha8_k127_uncoupled"] < .50 for s in SEEDS)}
for name, n in P.items():
    print(f"{name}: {'HELD' if n >= 5 else 'FAILED'} ({n}/6 seeds; need 5)")
