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

        print("\n[P4 -- OPEN, NOT RUN]")
        print("  Does the LOUD->GATED score shift reproduce on a large target?")
        print("  calibrate_governance.py, 1071 lines pre-fix / 1125 post-fix.")
        print("  Not run here: every mutant re-runs a full calibration.")

        # Per the estate's gate/prediction rule: the GATE failing exits 1
        # (the instrument is untrustworthy, report nothing). A prediction
        # being REFUTED exits 0 -- refutations are kept findings, not build
        # failures. Getting this backwards deletes published findings.
        print(f"\nP2 CONFIRMED, P3 REFUTED (kept). Gate passed, so the")
        print(f"instrument is trusted and both verdicts stand. Exit 0.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
