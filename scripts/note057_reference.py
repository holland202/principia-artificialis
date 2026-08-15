#!/usr/bin/env python3
"""
note057_reference.py -- reference code for note057.

Reproduces the phenomenon the note describes, from fixtures built here, so the
numbers do not depend on the state of any repository. Dependency-light: stdlib
only. Prints every number that appears in the note.

Run:  python3 note057_reference.py
Exit: 0 if every registered prediction resolves as recorded, 1 otherwise.
"""
import os
import subprocess
import sys
import tempfile

SILENT = '''\
import sys
ok = check()
def check():
    return False
print("done")
'''

# A Type A check that says nothing about the failure it found.
QUIET = '''\
import sys
ok = False
print("checking")
sys.exit(0)
'''

# A Type A check that detects the failure, announces it in alarming language,
# independently re-verifies that the failure is real, and then exits 0.
# This is the shape of igar/test2_honest_failure.py before 2026-08-14.
LOUD = '''\
import sys
result = {'Z1'}          # wrong: does not block both confounding paths
expected = None
print("=== TEST: honest failure under throttling ===")
print(f"Result: {'CORRECT' if result is expected else 'DANGER: returned ' + str(result)}")
if result is not expected:
    is_actually_valid = False        # independent re-check
    print(f"Double-checking validity directly: {is_actually_valid}")
'''

# The same check with its verdict propagated.
GATED = LOUD + '''\
if result is not expected:
    print("VERDICT: FAIL")
    sys.exit(1)
print("VERDICT: PASS")
sys.exit(0)
'''


def run(path):
    p = subprocess.run([sys.executable, path], capture_output=True, text=True)
    return p.returncode, p.stdout


def alarm_words(out):
    return sum(w in out for w in ("DANGER", "FAIL", "invalid", "False"))


def main():
    results = []
    with tempfile.TemporaryDirectory() as d:
        paths = {}
        for name, src in (("quiet", QUIET), ("loud", LOUD), ("gated", GATED)):
            paths[name] = os.path.join(d, f"{name}.py")
            with open(paths[name], "w") as f:
                f.write(src)

        print("=" * 68)
        print("P1  A check can detect a real failure, announce it, independently")
        print("    re-verify it, and still exit 0.")
        print("=" * 68)
        rc_q, out_q = run(paths["quiet"])
        rc_l, out_l = run(paths["loud"])
        rc_g, out_g = run(paths["gated"])
        print(f"  quiet  Type A   exit {rc_q}   alarm words in output: {alarm_words(out_q)}")
        print(f"  loud   Type A   exit {rc_l}   alarm words in output: {alarm_words(out_l)}")
        print(f"  gated           exit {rc_g}   alarm words in output: {alarm_words(out_g)}")
        p1 = (rc_l == 0 and alarm_words(out_l) >= 2)
        print(f"  P1: {'CONFIRMED' if p1 else 'REFUTED'} -- loud exits {rc_l} "
              f"while printing {alarm_words(out_l)} alarm words")
        results.append(("P1", p1, True))

        print()
        print("=" * 68)
        print("P2  Severity varies WITHIN Type A: quiet and loud are the same")
        print("    class to a detector, but not to a reader.")
        print("=" * 68)
        print(f"  quiet alarm words: {alarm_words(out_q)}    loud alarm words: {alarm_words(out_l)}")
        p2 = alarm_words(out_l) > alarm_words(out_q) and rc_l == rc_q
        print(f"  same exit code ({rc_q} vs {rc_l}), different reader signal: "
              f"{'CONFIRMED' if p2 else 'REFUTED'}")
        results.append(("P2", p2, True))

        print()
        print("=" * 68)
        print("P3  ANTI-VACUITY. The instrument must be able to return null.")
        print("    A gated check must NOT be reported as defective.")
        print("=" * 68)
        p3 = (rc_g == 1)
        print(f"  gated exit code: {rc_g} (expected 1 -- verdict propagated)")
        print(f"  P3: {'PASS' if p3 else 'FAIL'} -- the probe distinguishes gated "
              f"from ungated; it is not reporting every file as defective")
        results.append(("P3", p3, True))

        print()
        print("=" * 68)
        print("P4  A shell pipeline reports the exit status of its LAST command,")
        print("    so `cmd | tail` masks a nonzero exit from cmd.")
        print("=" * 68)
        direct = subprocess.run(f'{sys.executable} {paths["gated"]} >/dev/null 2>&1; echo $?',
                                shell=True, capture_output=True, text=True).stdout.strip()
        piped = subprocess.run(f'{sys.executable} {paths["gated"]} 2>&1 | tail -1 >/dev/null; echo $?',
                               shell=True, capture_output=True, text=True).stdout.strip()
        print(f"  direct         -> exit {direct}")
        print(f"  piped to tail  -> exit {piped}")
        p4 = (direct == "1" and piped == "0")
        print(f"  P4: {'CONFIRMED' if p4 else 'REFUTED'} -- a verification harness "
              f"that pipes its subject cannot see the subject fail")
        results.append(("P4", p4, True))

    print()
    print("=" * 68)
    print("VERDICT")
    print("=" * 68)
    bad = [n for n, got, want in results if got != want]
    for n, got, want in results:
        print(f"  {n}: {'as registered' if got == want else 'NOT as registered'}")
    if bad:
        print(f"\nFAIL -- {', '.join(bad)} did not resolve as recorded in the note.")
        return 1
    print("\nAll four resolved as recorded in note057.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
