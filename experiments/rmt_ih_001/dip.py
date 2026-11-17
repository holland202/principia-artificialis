"""RMT-IH-001 part B analysis (REGISTRATION_B.md): the top_norm dip. Usage: python3 dip.py RUNS.json
Written by Claude (Anthropic, Opus 5.5), 2026-11-16. SELF-TESTED only."""
import json
import sys

import numpy as np

import analyze as A

AFTER = 400


def dip(rows):
    """Largest fall of top_norm below its running maximum at or after step AFTER: (size, step)."""
    st = [r["step"] for r in rows]
    t = np.array([r["top_norm"] for r in rows])
    i0 = st.index(AFTER)
    fall = (np.maximum.accumulate(t) - t)[i0:]
    j = int(np.argmax(fall)) + i0
    return float(fall.max()), st[j]


def verdicts(runs):
    rep = {k.split("/")[1]: v for k, v in runs.items() if k.startswith("repeat/")}
    nor = {k.split("/")[1]: v for k, v in runs.items() if k.startswith("norepeat/")}
    table, v = [], {}
    for s, rows in rep.items():
        steps, icl = [r["step"] for r in rows], [r["icl"] for r in rows]
        size, at = dip(rows)
        table.append((s, size, at, A.t_change(steps, icl, 0.5, 1.0), A.t_change(steps, icl, 0.1, 1.0)))
    nd = {s: dip(rows)[0] for s, rows in nor.items()}
    n = len(table)
    a1 = sum(size >= 0.5 for _, size, _, _, _ in table)
    a2 = sum(x < 0.2 for x in nd.values())
    v["P6a"] = (a1 >= 5 and a2 >= 5, f"repeat dips >= 0.5 in {a1}/{n}; norepeat dips < 0.2 in {a2}/{len(nd)}")
    b = sum(A.before(at, t50) for _, _, at, t50, _ in table)
    v["P6b"] = (b >= 5, f"dip before the 50% ICL point in {b}/{n}")
    c = sum(A.before(at, t10) for _, _, at, _, t10 in table)
    v["P6c"] = (c >= 5, f"dip before the 10% ICL point in {c}/{n}")
    return table, nd, v


if __name__ == "__main__":
    runs = json.load(open(sys.argv[1]))["runs"]
    table, nd, v = verdicts(runs)
    print("seed  dip_size  dip_step  t_icl50  t_icl10   (repeat)")
    for s, size, at, t50, t10 in table:
        print(f"{s:>4}  {size:.3f}  {at}  {t50}  {t10}")
    print("norepeat dip sizes:", ", ".join(f"{s}:{x:.3f}" for s, x in nd.items()))
    for k, (ok, why) in v.items():
        print(f"{k}: {'HELD' if ok else 'FAILED'}  ({why})")
