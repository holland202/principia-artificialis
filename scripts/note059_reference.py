#!/usr/bin/env python3
"""
note059_reference.py -- reference code for note059.

Builds every fixture here, so the numbers do not depend on the state of any
repository. Dependency-light: stdlib only. Prints every number that appears in
the note.

The mutation operator implemented below is a MINIMAL reimplementation of one
operator from mutation_probe.py (comparison-boundary swap). It exists so this
note is self-contained and runnable by someone who does not have the vacuity
lint repo. The corpus numbers quoted in the note came from the real tool; the
note names the exact commands to reproduce them.

Run:  python3 note059_reference.py
Exit: 0 if the gate passes and predictions resolve as recorded, 1 if the gate
      fails (in which case NO prediction is reported in either direction).
"""
import ast
import os
import subprocess
import sys
import tempfile

# --------------------------------------------------------------- fixtures
# LOUD: computes the correct verdict, announces it, exits 0 regardless.
LOUD = '''\
import sys
value = 10
limit = 10
ok = value >= limit
if not ok:
    print("[FAIL] value below limit")
else:
    print("[PASS] value at or above limit")
print("done")
sys.exit(0)
'''

# GATED: identical logic, verdict reaches the exit code.
GATED = '''\
import sys
value = 10
limit = 10
ok = value >= limit
if not ok:
    print("[FAIL] value below limit")
    sys.exit(1)
print("[PASS] value at or above limit")
sys.exit(0)
'''

# SPARSE_LOAD: correctly gated, exactly ONE eligible comparison, load-bearing.
SPARSE_LOAD = '''\
import sys
value = 10
if value >= 10:
    sys.exit(0)
sys.exit(1)
'''

# SPARSE_DEAD: correctly gated, exactly ONE eligible comparison, decorative.
# The exit code is fixed by construction; the comparison only picks a label.
SPARSE_DEAD = '''\
import sys
value = 10
label = "high" if value >= 10 else "low"
print("label:", label)
sys.exit(1)
'''


# --------------------------------------------------------------- operator
SWAP = {ast.GtE: ast.Gt, ast.Gt: ast.GtE, ast.LtE: ast.Lt, ast.Lt: ast.LtE,
        ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}


# --------------------------------------------- Amendment 3 fixtures
# FULL_COV: every eligible site is on a line that executes.
FULL_COV = '''\
import sys
x = 5
flag = True
if x >= 5 and flag:
    sys.exit(0)
sys.exit(1)
'''

# PARTIAL_COV: identical head, plus a branch guarded by a test that is
# false at run time. The three eligible sites inside it can never fire.
PARTIAL_COV = '''\
import sys
x = 5
flag = True
if x >= 5 and flag:
    sys.exit(0)
if x < 0:
    dead = True
    if dead or flag:
        sys.exit(2)
sys.exit(1)
'''

# DELIBERATELY a second operator definition, separate from SWAP above.
# SWAP is this script's own minimal comparison-boundary operator. The
# reachability finding in Amendment 3 is about the denominator of scores
# produced by the EXTERNAL mutation_probe.py, whose site set is different:
# boundary comparisons, boolean constants, and boolean operators, counted
# per node rather than per operator. A control measuring SWAP's sites would
# be internally tidy and externally irrelevant -- the corpus numbers
# (91 / 25 / 66) came from mutation_probe's site set, so the fixtures must
# use the same one. Kept adjacent and named so the divergence is visible
# rather than accidental.
MP_BOUNDARY = {ast.Lt: ast.LtE, ast.LtE: ast.Lt,
               ast.Gt: ast.GtE, ast.GtE: ast.Gt}
MP_BOOLOP = {ast.And: ast.Or, ast.Or: ast.And}


def eligible_site_lines(src):
    """Line number of every site mutation_probe.eligible_nodes would yield,
    in ast.walk order."""
    out = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Compare) and len(node.ops) == 1 \
                and type(node.ops[0]) in MP_BOUNDARY:
            out.append(node.lineno)
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            out.append(node.lineno)
        elif isinstance(node, ast.BoolOp) and type(node.op) in MP_BOOLOP:
            out.append(node.lineno)
    return out


def _cover_hit(line):
    """True if a trace .cover line carries a hit count. trace marks
    never-executed lines with '>>>>>>'."""
    if line.startswith(">>>>>>"):
        return False
    head, sep, _ = line.partition(":")
    return bool(sep) and head.strip().isdigit()


def reachability(src, name, workdir):
    """Run src under trace, return (eligible, reachable, unreachable).
    Returns None if trace produced no .cover file."""
    path = os.path.join(workdir, name + ".py")
    with open(path, "w") as f:
        f.write(src)
    covdir = os.path.join(workdir, "cov_" + name)
    subprocess.run([sys.executable, "-m", "trace", "--count",
                    "--coverdir", covdir, path],
                   capture_output=True, text=True, cwd=workdir)
    cover = os.path.join(covdir, name + ".cover")
    if not os.path.exists(cover):
        return None
    with open(cover) as f:
        hit = set(i for i, ln in enumerate(f, 1) if _cover_hit(ln))
    sites = eligible_site_lines(src)
    live = [ln for ln in sites if ln in hit]
    return len(sites), len(live), len(sites) - len(live)


def count_eligible(src):
    n = 0
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Compare):
            n += sum(1 for op in node.ops if type(op) in SWAP)
    return n


def make_mutant(src, k):
    """Re-parse the ORIGINAL source and mutate the k-th eligible operator.

    Never deep-copies. mutation_probe.py records that deepcopy-and-match-by-id
    was the first bug it found in itself: deepcopy allocates new ids, so the
    mutation applies to nothing and every verdict comes back SURVIVED.
    """
    tree = ast.parse(src)
    i = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for j, op in enumerate(node.ops):
                if type(op) in SWAP:
                    if i == k:
                        node.ops[j] = SWAP[type(op)]()
                        return ast.unparse(ast.fix_missing_locations(tree))
                    i += 1
    return None


def run(src, workdir):
    path = os.path.join(workdir, "m.py")
    with open(path, "w") as f:
        f.write(src)
    p = subprocess.run([sys.executable, path], capture_output=True, timeout=30)
    return p.returncode


def score(name, src, workdir):
    base = run(src, workdir)
    n = count_eligible(src)
    killed = survived = 0
    for k in range(n):
        mut = make_mutant(src, k)
        if mut is None:
            continue
        if run(mut, workdir) != base:
            killed += 1
        else:
            survived += 1
    total = killed + survived
    pct = (100.0 * killed / total) if total else float("nan")
    print(f"  {name:12s} baseline_exit={base}  mutants={total:2d}  "
          f"killed={killed}  survived={survived}  score={pct:.1f}%")
    return {"name": name, "base": base, "n": total, "killed": killed,
            "survived": survived, "score": pct}



from math import comb as _a4_comb

# ---------------------------------------------------------------------------
# AMENDMENT 4 -- Clopper-Pearson intervals on mutation scores.
#
# NOT Amendment 3: P5 above already forward-references Amendment 3 as the
# REACHABILITY correction (25 of 91 eligible sites on calibrate_governance).
# Resolving that reference to different work would be the quiet drift this
# note exists to prevent, so intervals take the next free slot.
#
# Predictions P9-P12. P1-P8 are claimed above.
# Stdlib only (math.comb). Device-verified bit-identical on x86_64/py3.12
# and aarch64/Termux/py3.14.
# ---------------------------------------------------------------------------

A4_ALPHA = 0.05
A4_SABOTAGE = "--sabotage-a4" in sys.argv


def _a4_tail_ge(k, n, p):
    return sum(_a4_comb(n, i) * p**i * (1.0 - p)**(n - i)
               for i in range(k, n + 1))


def _a4_tail_le(k, n, p):
    return sum(_a4_comb(n, i) * p**i * (1.0 - p)**(n - i)
               for i in range(0, k + 1))


def _a4_bisect(fn, target, lo, hi, iters=200):
    rising = fn(hi) > fn(lo)
    for _ in range(iters):
        mid = (lo + hi) / 2.0
        if (fn(mid) < target) == rising:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def a4_cp(k, n, alpha=A4_ALPHA):
    """Exact two-sided Clopper-Pearson interval."""
    if n <= 0 or not 0 <= k <= n:
        raise ValueError("bad k/n")
    lo = 0.0 if k == 0 else _a4_bisect(lambda p: _a4_tail_ge(k, n, p),
                                       alpha / 2.0, 0.0, 1.0)
    hi = 1.0 if k == n else _a4_bisect(lambda p: _a4_tail_le(k, n, p),
                                       alpha / 2.0, 0.0, 1.0)
    if A4_SABOTAGE:
        lo = hi = k / n
    return lo, hi


def _a4_overlaps(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


A4_CASES = [
    ("engine_diagnostic_patch.py",              0,   1),
    ("verify_quantum_claims pre-fix  a1c990d",  0,   7),
    ("verify_quantum_claims post-fix 33ad55e",  2,   7),
    ("calibrate_governance  pre-fix  a1c990d",  2,  87),
    ("calibrate_governance  post-fix 33ad55e",  3,  90),
]

A4_REACH_NUM, A4_REACH_DEN = 25, 91


def amendment4():
    """Returns True if all four gates pass. Prints P9-P12 either way."""
    print("\n" + "=" * 70)
    print("[AMENDMENT 4 -- Clopper-Pearson intervals, P9-P12]")
    print("Amendment 3 is RESERVED for the reachability run P5 promises.")
    if A4_SABOTAGE:
        print("*** --sabotage-a4 ACTIVE: intervals collapsed to points ***")

    gates = []
    ok = True
    for n in (1, 7, 10, 87):
        if (abs(a4_cp(0, n)[1] - (1.0 - (A4_ALPHA / 2.0) ** (1.0 / n))) > 1e-9
                or abs(a4_cp(n, n)[0] - (A4_ALPHA / 2.0) ** (1.0 / n)) > 1e-9):
            ok = False
    gates.append(("G1 closed-form agreement (k=0 and k=n)", ok))

    lo, hi = a4_cp(3, 20)
    gates.append(("G2 bounds satisfy the defining tail equations",
                  abs(_a4_tail_ge(3, 20, lo) - A4_ALPHA / 2.0) < 1e-9
                  and abs(_a4_tail_le(3, 20, hi) - A4_ALPHA / 2.0) < 1e-9))

    w, t = a4_cp(0, 1), a4_cp(500, 1000)
    gates.append(("G3 anti-vacuity: wide at n=1 AND tight at n=1000",
                  (w[1] - w[0]) > 0.90 and (t[1] - t[0]) < 0.10))

    gates.append(("G4 anti-vacuity: overlap returns False when separated",
                  (not _a4_overlaps(a4_cp(2, 87), a4_cp(60, 90)))
                  and _a4_overlaps(a4_cp(2, 87), a4_cp(3, 90))))

    for name, g in gates:
        print("  [%s] %s" % ("PASS" if g else "FAIL", name))
    if not all(g for _, g in gates):
        print("  GATE FAILURE -- no Amendment 4 verdicts reported.")
        return False

    print("\n  INTERVALS (n = eligible sites, as published)")
    iv = {}
    for name, k, n in A4_CASES:
        lo, hi = a4_cp(k, n)
        iv[name] = (lo, hi)
        print("    %-38s %2d/%-3d = %6.2f%%  95%% CI [%6.2f%%, %6.2f%%]"
              % (name, k, n, 100.0 * k / n, 100 * lo, 100 * hi))

    lo, hi = iv["engine_diagnostic_patch.py"]
    p9 = (hi - lo) > 0.90
    print("\n  P9  n=1 interval spans >90%% of [0,1]: width %.2f%% -> %s"
          % (100 * (hi - lo), "CONFIRMED" if p9 else "REFUTED"))
    print("      P2's claim restated as an interval, not an assertion.")

    a = iv["calibrate_governance  pre-fix  a1c990d"]
    b = iv["calibrate_governance  post-fix 33ad55e"]
    p10 = _a4_overlaps(a, b)
    print("  P10 calibrate_governance pre/post OVERLAP: "
          "[%.2f%%, %.2f%%] vs [%.2f%%, %.2f%%] -> %s"
          % (100 * a[0], 100 * a[1], 100 * b[0], 100 * b[1],
             "CONFIRMED" if p10 else "REFUTED"))
    print("      P4's refutation survives at 95%: no detectable shift.")

    a = iv["verify_quantum_claims pre-fix  a1c990d"]
    b = iv["verify_quantum_claims post-fix 33ad55e"]
    p11 = _a4_overlaps(a, b)
    print("  P11 verify_quantum_claims pre/post OVERLAP: "
          "[%.2f%%, %.2f%%] vs [%.2f%%, %.2f%%] -> %s"
          % (100 * a[0], 100 * a[1], 100 * b[0], 100 * b[1],
             "CONFIRMED" if p11 else "REFUTED"))
    print("      RETRACTION: the 0.0% -> 28.6% jump is not resolvable at")
    print("      n=7. note057's 'affirmative evidence that the loud variant")
    print("      is detectable' does not stand as a mutation-score claim.")
    print("      Ground truth untouched -- defect and fix were both made")
    print("      deliberately -- only the instrument's resolution is at issue.")

    print("\n  SENSITIVITY TO P5 (assumption, NOT a measurement)")
    print("    A killed mutant is necessarily reachable, so P5's correction")
    print("    shrinks n and leaves k fixed. Applying %d/%d to survivors:"
          % (A4_REACH_NUM, A4_REACH_DEN))
    ratio = A4_REACH_NUM / A4_REACH_DEN
    for name, k, n in A4_CASES[3:]:
        nr = max(k, k + round((n - k) * ratio))
        lo, hi = a4_cp(k, nr)
        print("      %-36s %2d/%-3d = %6.2f%%  95%% CI [%6.2f%%, %6.2f%%]"
              % (name, k, nr, 100.0 * k / nr, 100 * lo, 100 * hi))
    print("    Smaller n gives WIDER intervals, so every overlap verdict")
    print("    above can only strengthen when P5 runs.")

    print("\n  LIMITATION: Clopper-Pearson assumes independent trials.")
    print("    Mutants in one function share a code path, so kills are")
    print("    correlated and these intervals are too NARROW. Every overlap")
    print("    reported is a lower bound on the true overlap.")

    print("\n  [P12 -- OPEN, NOT RUN] Recompute with a cluster bootstrap")
    print("    resampling whole FUNCTIONS. Registered: no verdict changes,")
    print("    because correlation widens intervals and all verdicts overlap.")
    return True


def main():
    tmp = os.environ.get("TMPDIR") or os.path.join(os.path.expanduser("~"), "tmp")
    os.makedirs(tmp, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=tmp) as wd:
        print("note059 -- mutation score needs a denominator\n")
        print("[fixtures]")
        loud = score("LOUD", LOUD, wd)
        gated = score("GATED", GATED, wd)
        s_load = score("SPARSE_LOAD", SPARSE_LOAD, wd)
        s_dead = score("SPARSE_DEAD", SPARSE_DEAD, wd)

        # ---------------------------------------------------------- GATE
        # Anti-vacuity: the instrument must DISCRIMINATE. LOUD and GATED are
        # the same logic; only the exit wiring differs. If the operator cannot
        # separate them, it is measuring nothing and no prediction is reported.
        print("\n[GATE] instrument must separate LOUD from GATED")
        same_n = loud["n"] == gated["n"]
        separates = loud["score"] == 0.0 and gated["score"] > 0.0
        print(f"  equal mutant counts (confound held fixed): {same_n} "
              f"({loud['n']} vs {gated['n']})")
        print(f"  LOUD=0.0% and GATED>0.0%: {separates}")
        if not (same_n and separates):
            print("\n  GATE FAILED. The operator does not discriminate on a")
            print("  pair whose only difference is the exit wiring. No")
            print("  prediction is reported in either direction. Exit 1.")
            return 1
        print("  GATE PASS")

        # ------------------------------------------- GATE 2 (Amendment 3)
        # Anti-vacuity for the reachability filter. A filter that reports
        # unreachable sites on every input measures nothing. It must return
        # NULL on a fully-covered fixture and NON-NULL on one with known
        # dead sites. Independent of GATE 1; both must pass.
        print("\n[GATE 2] reachability filter must return both directions")
        full = reachability(FULL_COV, "full_cov", wd)
        part = reachability(PARTIAL_COV, "partial_cov", wd)
        if full is None or part is None:
            print("\n  GATE 2 FAILED. trace produced no .cover file. No")
            print("  prediction is reported in either direction. Exit 1.")
            return 1
        print(f"  full_cov.py    eligible={full[0]} reachable={full[1]} "
              f"unreachable={full[2]}")
        print(f"  partial_cov.py eligible={part[0]} reachable={part[1]} "
              f"unreachable={part[2]}")
        null_ok = full[2] == 0
        signal_ok = part[2] > 0
        print(f"  returns null on full coverage       : {null_ok} "
              f"(expected True)")
        print(f"  returns non-null on partial coverage : {signal_ok} "
              f"(expected True)")
        if not (null_ok and signal_ok):
            print("\n  GATE 2 FAILED. The filter did not return both")
            print("  directions. No prediction is reported in either")
            print("  direction. Exit 1.")
            return 1
        if (full[0], full[1], full[2]) != (3, 3, 0) or \
                (part[0], part[1], part[2]) != (6, 3, 3):
            print("\n  GATE 2 FAILED. Fixture values drifted from the")
            print("  numbers recorded in Amendment 3 (expected 3/3/0 and")
            print("  6/3/3). No prediction reported. Exit 1.")
            return 1
        print("  GATE 2 PASS")

        # --------------------------------------------------- predictions
        print("\n[predictions]")
        p2 = (s_load["n"] == 1 and s_dead["n"] == 1
              and s_load["score"] == 100.0 and s_dead["score"] == 0.0)
        print(f"  P2 at n=1 the score is uninformative: "
              f"SPARSE_LOAD={s_load['score']:.1f}% "
              f"SPARSE_DEAD={s_dead['score']:.1f}% "
              f"-> {'CONFIRMED' if p2 else 'REFUTED'}")
        print("     Both files are correctly gated. Score alone separates")
        print("     them anyway, so a low score at small n is not evidence")
        print("     of vacuity -- it is evidence of a small denominator.")

        p3 = gated["score"] < 100.0 and gated["survived"] > 0
        print(f"  P3 a correctly gated file still leaves survivors: "
              f"GATED survived={gated['survived']} "
              f"-> {'CONFIRMED' if p3 else 'REFUTED'}")
        print("     So an exit code keyed to 'any survivor' fires on correct")
        print("     code too, and cannot gate CI without a score threshold.")

        print("\n[P4 -- REFUTED (kept), Amendment 1]")
        print("  The LOUD->GATED shift does NOT reproduce on")
        print("  calibrate_governance.py. Scores 2.3% -> 3.3% across the same")
        print("  commit pair. Re-scored with the crash-detecting probe in")
        print("  Amendment 2 (P6 RESOLVED): the flat result is real, not an")
        print("  artifact of the instrument that measured it.")
        print("\n[P5 -- OPEN, NOT RUN]")
        print("  What fraction of each estate target\x27s eligible sites is")
        print("  reachable under the no-argument invocation mutation_probe")
        print("  uses? On calibrate_governance.py it is 25 of 91. If that")
        print("  holds estate-wide, every published score needs the same")
        print("  correction. See Amendment 3.")
        print("\n[P8 -- OPEN, NOT RUN]")
        print("  Is engine_diagnostic_patch.py\x27s single eligible site")
        print("  reachable at all? One command decides whether that corpus")
        print("  row is weak evidence or none.")

        # Per the estate's gate/prediction rule: the GATE failing exits 1
        # (the instrument is untrustworthy, report nothing). A prediction
        # being REFUTED exits 0 -- refutations are kept findings, not build
        # failures. Getting this backwards deletes published findings.
        a4_ok = amendment4()

        # Per the estate's gate/prediction rule: the GATE failing exits 1
        # (the instrument is untrustworthy, report nothing). A prediction
        # being REFUTED exits 0 -- refutations are kept findings, not build
        # failures. Getting this backwards deletes published findings.
        print("\nP2 %s, P3 %s. Amendment 4 gate: %s."
              % ("CONFIRMED" if p2 else "REFUTED",
                 "CONFIRMED" if p3 else "REFUTED (kept)",
                 "PASS" if a4_ok else "FAIL"))
        print("Verdicts stand where the gate passed.")
        return 0 if a4_ok else 1


if __name__ == "__main__":
    sys.exit(main())
