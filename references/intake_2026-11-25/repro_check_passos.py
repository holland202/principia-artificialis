#!/usr/bin/env python3
"""Recompute the headline numbers of arXiv:2611.19359 from its committed rows, with Claude's own code.

  python repro_check_passos.py /path/to/gemma4-memory-study/results/run_rows.jsonl [--sabotage]

Reads the rows only; imports nothing from the study repo. Pairing follows the rule read from the study's
results/analyze_rows.py at 2eea9c6: arm recap run 1 vs arm none run 1, same backend and task, rows with
exploratory_partial excluded; primary = backends modal + kaggle, extension = aws-l40s; identical-condition
flips = none run 2 vs none run 1 within a backend. --sabotage flips ONE recap run-1 row (the first in sort order
that has a matching none run-1 row) in the data before any block is computed, so every block sees the same change.
(Before 2026-11-25 Amendment 1, it flipped the first pair separately inside each block.)
"""
import json
import math
import sys


def mcnemar_two_sided(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def main():
    path = sys.argv[1]
    rows = [json.loads(l) for l in open(path)]
    rows = [r for r in rows if not r.get("exploratory_partial") and r.get("phase") != "R"]
    I = {(r["backend"], r["arm"], r["run"], r["task_id"]): r["success"] for r in rows}

    def paired(backends, x, y):
        return [(b, t, I[(b, *x, t)], I[(b, *y, t)]) for (b, a, r, t) in sorted(I)
                if b in backends and (a, r) == x and (b, *y, t) in I]

    sab = "--sabotage" in sys.argv
    if sab:
        k = next(k for k in sorted(I) if k[1:3] == ("recap", 1) and (k[0], "none", 1, k[3]) in I)
        I[k] = 1 - I[k]
        print(f"sabotage: flipped {k[0]}/{k[1]}/run{k[2]}/{k[3]} to {I[k]}")
    out = {}
    for name, bks in (("primary_48", ("modal", "kaggle")), ("extension_50", ("aws-l40s",)),
                      ("combined_98", ("modal", "kaggle", "aws-l40s"))):
        P = paired(bks, ("recap", 1), ("none", 1))
        xs, ys = sum(p[2] for p in P), sum(p[3] for p in P)
        b = sum(1 for p in P if p[2] and not p[3]); c = sum(1 for p in P if p[3] and not p[2])
        out[name] = f"pairs {len(P)}  recap {xs}  none {ys}  diff {100 * (xs - ys) / len(P):+.1f} pts  " \
                    f"discordant recap-only {b} none-only {c}  exact McNemar p {mcnemar_two_sided(b, c):.4f}"
    for bk in ("modal", "kaggle", "aws-l40s"):
        P = paired((bk,), ("none", 2), ("none", 1))
        if P:
            f = sum(1 for p in P if p[2] != p[3])
            out[f"flip_none_run2_vs_run1_{bk}"] = f"pairs {len(P)}  flipped {f}  ({100 * f / len(P):.1f}%)"
    P = [p for bk in ("modal", "kaggle", "aws-l40s") for p in paired((bk,), ("none", 2), ("none", 1))]
    f = sum(1 for p in P if p[2] != p[3])
    out["flip_none_run2_vs_run1_all"] = f"pairs {len(P)}  flipped {f}  ({100 * f / len(P):.1f}%)"
    for k, v in out.items():
        print(f"{k:34s} {v}")


if __name__ == "__main__":
    main()
