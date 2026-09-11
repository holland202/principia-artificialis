#!/usr/bin/env python3
"""
note060_reference.py -- the reachability denominator.

REBUILD. The original instrument was written 2026-08-27, never committed, and
deleted 2026-09-11. This is a RECONSTRUCTION from the methodology described in
research_notes/note060_reachability_denominator.md, not a recovery of the
original file. It is committed BEFORE being run against the target, which is
what note060's P13 registers.

P13's registered prediction, fixed before execution:

    calibrate_governance.py at sovereign-suite commit 33ad55e reports
    91 eligible sites and 25 reachable under the no-argument invocation.

If this instrument reports different numbers, note060's numbers are WITHDRAWN
rather than adjusted. The rebuild is not permitted to redefine the
measurement until it agrees.

What it measures
----------------
mutation_probe.py scores killed / (killed + survived) over every eligible
site. A mutation on a line the target never executes cannot change the exit
code, so it is recorded SURVIVED by construction. The score therefore mixes a
claim about test strength with a claim about coverage.

This filter separates them: same eligible-site definition mutation_probe
uses, target run under coverage, count how many of those sites executed.

Reachability is a property of AN INVOCATION, not of a file. The original
measurement found 25 of 91 reachable with no arguments and 30 of 91 under
--sweep, on the same file. Every figure printed here is reported against the
command that produced it; a bare "reachable" number with no invocation beside
it is not a result.

    python3 note060_reference.py --selftest
    python3 note060_reference.py TARGET.py [ARGS...]

Exit 0 when the gate passes, whatever the reachability turns out to be. Low
reachability is a result, not a build failure. Exit 1 when the gate fails.
"""

import argparse
import ast
import contextlib
import io as _io
import os
import sys
import tempfile
import textwrap
import trace

# Mirrors mutation_probe.py exactly. If these drift apart the denominators
# stop being comparable, which is the whole point of the note.
BOUNDARY = {
    ast.Lt: ast.LtE, ast.LtE: ast.Lt,
    ast.Gt: ast.GtE, ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
}
BOOLOP = {ast.And: ast.Or, ast.Or: ast.And}


def eligible_sites(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        tree = ast.parse(f.read(), filename=path)
    out = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Compare) and len(node.ops) == 1
                and type(node.ops[0]) in BOUNDARY):
            out.append((node.lineno, "compare"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
            out.append((node.lineno, "boolconst"))
        elif isinstance(node, ast.BoolOp) and type(node.op) in BOOLOP:
            out.append((node.lineno, "boolop"))
    return out


def executed_lines(path, argv):
    """Lines of `path` executed when run with argv, via stdlib trace.

    The target's own exit is swallowed: a target that exits nonzero has still
    executed lines, and that coverage IS the measurement. A target that
    crashes early yields few lines, which is reported rather than hidden.
    """
    tr = trace.Trace(count=1, trace=0,
                     ignoredirs=[sys.prefix, sys.exec_prefix])
    src = open(path, encoding="utf-8", errors="replace").read()
    code = compile(src, path, "exec")
    old_argv = sys.argv
    old_cwd = os.getcwd()
    g = {"__name__": "__main__", "__file__": path}
    sys.argv = [path] + list(argv)
    try:
        d = os.path.dirname(os.path.abspath(path))
        if d:
            os.chdir(d)
        try:
            tr.runctx(code, g, g)
        except SystemExit:
            pass
        except BaseException as e:
            print(f"  (target raised {type(e).__name__}; coverage up to that "
                  "point is still counted)")
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)
    hit = set()
    for (fname, lineno), n in tr.results().counts.items():
        if os.path.abspath(fname) == os.path.abspath(path) and n > 0:
            hit.add(lineno)
    return hit


def measure(path, argv):
    sites = eligible_sites(path)
    hit = executed_lines(path, argv)
    reachable = [s for s in sites if s[0] in hit]
    return len(sites), len(reachable), len(sites) - len(reachable)


FULL = '''
import sys
def check(a, b):
    if a >= b:
        return True
    return False
print(check(2, 1))
print(check(1, 2))
sys.exit(0)
'''

PARTIAL = '''
import sys
def reached(a, b):
    if a >= b:
        return True
    return False

def never_called(x, y):
    if x <= y:
        return True
    if x == y:
        return False
    return True
print(reached(2, 1))
sys.exit(0)
'''


def selftest():
    """ANTI-VACUITY: the filter must return BOTH directions. One that always
    reported zero unreachable would score every corpus as fully exercised and
    could never have found what note060 found."""
    print("=" * 68)
    print("ANTI-VACUITY SELFTEST -- reachability filter")
    print("=" * 68)
    print("  NOTE: these fixtures are REBUILT, not the originals, which were")
    print("  lost with the instrument. full_cov reproduces the original's")
    print("  3/3/0. partial_cov does NOT reproduce the original's 6/3/3 --")
    print("  it is a different fixture testing the same property. The gate")
    print("  asserts the two DIRECTIONS, not the original numbers.")
    print()
    got = {}
    with tempfile.TemporaryDirectory(dir=os.environ.get("HOME")) as d:
        for name, src in (("full_cov.py", FULL), ("partial_cov.py", PARTIAL)):
            p = os.path.join(d, name)
            with open(p, "w") as f:
                f.write(textwrap.dedent(src))
            # Fixture stdout is noise, not evidence; keep the gate readable.
            with contextlib.redirect_stdout(_io.StringIO()):
                e, r, u = measure(p, [])
            got[name] = (e, r, u)
            print(f"  {name:<15} eligible={e} reachable={r} unreachable={u}")
    null_ok = got["full_cov.py"][2] == 0
    nonnull_ok = got["partial_cov.py"][2] > 0
    print()
    print(f"  returns null on full coverage        : "
          f"{'PASS' if null_ok else 'FAIL'} (expected unreachable=0)")
    print(f"  returns non-null on partial coverage : "
          f"{'PASS' if nonnull_ok else 'FAIL'} (expected unreachable>0)")
    print()
    if null_ok and nonnull_ok:
        print("GATE PASS -- reports zero unreachable on a fully exercised")
        print("file AND nonzero on a partly exercised one. Not stuck on one")
        print("verdict.")
        print("=" * 68)
        return 0
    print("GATE FAIL -- the filter did not separate the two fixtures.")
    print("=" * 68)
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?")
    ap.add_argument("args", nargs="*", default=[])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.target:
        ap.error("a target is required unless --selftest is given")

    inv = " ".join(["python3", os.path.basename(a.target)] + list(a.args))
    e, r, u = measure(a.target, a.args)
    print("=" * 68)
    print("REACHABILITY DENOMINATOR")
    print("=" * 68)
    print(f"  target      : {a.target}")
    print(f"  invocation  : {inv}")
    print(f"  eligible    : {e}")
    print(f"  reachable   : {r}")
    print(f"  unreachable : {u}")
    if e:
        print(f"  reachable   : {100.0 * r / e:.2f}% of eligible")
    print()
    print("  Reachability is a property of the invocation above, not of the")
    print("  file. Quote them together or not at all.")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
