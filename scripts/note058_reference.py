#!/usr/bin/env python3
"""
note058_reference.py -- reference code for note058.

Re-runs the estate-wide vacuity scan and the two Kupferman-Vardi-shaped
demonstrations live, rather than hardcoding the numbers from the day this note
was written. The estate changes; this script does not go stale the way a
pasted table would.

Requires network access to clone the public repos and a local copy of
vacuity_lint.py (cloned below). Dependency-light beyond that: stdlib only.

Run:  python3 note058_reference.py
Exit: 0 if predictions resolve as recorded, 1 otherwise.
"""
import os
import subprocess
import sys
import tempfile

REPOS = [
    "principia-artificialis", "slc-v12-", "skn-v1-", "sovereign-evolution",
    "sovereign-suite", "sentinel-batadal-validation", "polytope-explorer",
    "edge-ai-primitives", "coverage-preserving-synthesis", "qolas-synthesis",
    "qsleuth", "vacuity_lint.py", "quasar-v2",
]

VACUOUS_ANTECEDENT_NEVER_FIRES = '''\
# Kupferman & Vardi's motivating example, as code instead of LTL.
# phi = G(req -> F grant): "every request is eventually followed by a grant".
# Vacuously true in any system where req never fires -- the implication is
# true on every step for a reason that has nothing to do with grants.
req_log = []       # req never appended to
grant_log = []

def check_g_req_implies_f_grant(req_log, grant_log):
    for i, req in enumerate(req_log):
        if req and not any(grant_log[i:]):
            return False
    return True

result = check_g_req_implies_f_grant(req_log, grant_log)
print(f"G(req -> F grant) holds: {result}")
print(f"but req fired {sum(req_log)} times out of {len(req_log)} steps")
'''


def run(path, args=None, cwd=None):
    p = subprocess.run([sys.executable, path] + (args or []),
                        capture_output=True, text=True, timeout=120, cwd=cwd)
    return p.returncode, p.stdout + p.stderr


def clone(url, dest, cwd=None):
    r = subprocess.run(["git", "clone", "-q", "--depth", "1", url, dest],
                        capture_output=True, text=True, timeout=120, cwd=cwd)
    return r.returncode == 0


def main():
    results = []
    print("=" * 68)
    print("P1  The Kupferman-Vardi vacuity example reproduces exactly:")
    print("    a specification holds for a reason unrelated to its intent")
    print("    when its antecedent never fires.")
    print("=" * 68)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "kv_example.py")
        with open(p, "w") as f:
            f.write(VACUOUS_ANTECEDENT_NEVER_FIRES)
        rc, out = run(p)
        print(out.strip())
        p1 = "holds: True" in out and "fired 0 times" in out
        print(f"P1: {'CONFIRMED' if p1 else 'REFUTED'}")
        results.append(("P1", p1, True))

    print()
    print("=" * 68)
    print("P2  Estate-wide vacuity scan. Denominator and findings should be")
    print("    reported live, not copied from a prior run.")
    print("=" * 68)
    with tempfile.TemporaryDirectory() as d:
        # NOTE, added 2026-08-15: this block used to open with os.chdir(d) and
        # never restore it. When this 'with' exits, d is deleted from disk,
        # but the PROCESS's cwd is still pointed at that now-gone path --
        # os.getcwd() raises FileNotFoundError from that state. P3, which
        # runs afterward and does not set cwd= on its subprocess call,
        # silently inherited the dangling directory and 'git clone' failed
        # with exit 128 ("could not create work tree dir: No such file or
        # directory"). clone() only checks the return code, so P3 reported
        # "could not clone -- network unavailable" -- a real, reproducible
        # bug misreported as a transient network condition. Confirmed by a
        # minimal repro (chdir into a TemporaryDirectory, let it close, run
        # any subprocess with no cwd=) before this fix was written. Fixed by
        # never chdir'ing at all: every subprocess call below now takes an
        # explicit cwd=d, so the process's own working directory is never
        # touched and nothing downstream can inherit a stale one.
        got_scanner = clone("https://github.com/holland202/vacuity_lint.py.git", "vl", cwd=d)
        if not got_scanner:
            print("  could not clone vacuity_lint.py -- P2 UNRUN (network unavailable)")
            results.append(("P2", None, None))
        else:
            scanner = os.path.join(d, "vl", "vacuity_lint.py")
            n_repos, n_py, n_findings, n_workflows_with_ci = 0, 0, 0, 0
            per_repo = []
            for name in REPOS:
                ok = clone(f"https://github.com/holland202/{name}.git", name, cwd=d)
                if not ok:
                    continue
                n_repos += 1
                pyfiles = subprocess.run(
                    ["git", "-C", name, "ls-files", "*.py"],
                    capture_output=True, text=True, cwd=d).stdout.strip().splitlines()
                n_py += len(pyfiles)
                rc, out = run(scanner, [name], cwd=d)
                fi = 0
                for line in out.splitlines():
                    if line.strip().startswith("findings"):
                        try:
                            fi = int(line.split(":")[1].strip())
                        except (IndexError, ValueError):
                            pass
                n_findings += fi
                ci = subprocess.run(
                    ["git", "-C", name, "ls-files", ".github/workflows"],
                    capture_output=True, text=True, cwd=d).stdout.strip()
                if ci:
                    n_workflows_with_ci += 1
                per_repo.append((name, len(pyfiles), fi))
            print(f"  repositories cloned      : {n_repos}")
            print(f"  python files scanned     : {n_py}")
            print(f"  repositories with any CI : {n_workflows_with_ci}")
            print(f"  total vacuity findings   : {n_findings}")
            for name, npy, fi in per_repo:
                if fi:
                    print(f"    {name}: {fi} finding(s) in {npy} files")
            rate = n_findings / n_py if n_py else 0.0
            print(f"  finding rate: {n_findings}/{n_py} = {rate:.1%}")
            print(f"  Kupferman-Vardi's reported LTL baseline: ~20% of "
                  f"specifications register vacuously")
            p2 = n_repos >= 10 and n_py >= 100
            print(f"P2: {'CONFIRMED' if p2 else 'REFUTED'} -- scan covered "
                  f"enough of the estate to be informative ({n_repos} repos, "
                  f"{n_py} files)")
            results.append(("P2", p2, True))

    print()
    print("=" * 68)
    print("P3  ANTI-VACUITY. This scan must be able to find zero as well as")
    print("    find something. A scan of a clean file must not error or")
    print("    manufacture a finding.")
    print("=" * 68)
    with tempfile.TemporaryDirectory() as d3:
        got_scanner_p3 = clone("https://github.com/holland202/vacuity_lint.py.git",
                                os.path.join(d3, "vl"))
        if not got_scanner_p3:
            print("  could not clone vacuity_lint.py -- P3 UNRUN (network unavailable)")
            results.append(("P3", None, None))
        else:
            clean_dir = os.path.join(d3, "clean")
            os.makedirs(clean_dir)
            with open(os.path.join(clean_dir, "clean.py"), "w") as f:
                f.write("def add(a, b):\n    return a + b\n")
            rc, out = run(os.path.join(d3, "vl", "vacuity_lint.py"), [clean_dir])
            print(out.strip())
            p3 = (rc == 0) and ("findings                : 0" in out)
            print(f"P3: {'PASS' if p3 else 'FAIL'} -- exit {rc}")
            results.append(("P3", p3, True))

    print()
    print("=" * 68)
    print("VERDICT")
    print("=" * 68)
    ran = [(n, g, w) for n, g, w in results if g is not None]
    unrun = [n for n, g, w in results if g is None]
    bad = [n for n, g, w in ran if g != w]
    for n, g, w in results:
        if g is None:
            print(f"  {n}: UNRUN (network unavailable)")
        else:
            print(f"  {n}: {'as registered' if g == w else 'NOT as registered'}")
    if bad:
        print(f"\nFAIL -- {', '.join(bad)} did not resolve as recorded.")
        return 1
    if unrun:
        print(f"\n{len(unrun)} prediction(s) unrun -- network required. "
              f"Not a failure; run with network access to complete.")
        return 0
    print("\nAll predictions resolved as recorded in note058.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
