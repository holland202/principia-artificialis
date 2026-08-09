#!/usr/bin/env python3
"""
prereg.py -- a harness that can return null, and refuses to report when it can't.

Dependency-free. Python 3.8+. No NumPy, no install. Runs on a phone.

WHY THIS EXISTS
    Across an archive of AI-generated "verification" systems, one defect recurs:
    a check that cannot fail. A gate returning True unless the output contains
    the literal word "hallucination". A governor printing "Thermal OK" from a
    loop that reads no sensor. A rejection branch behind a function ending in
    `return True`. An SO(3) invariance test whose point cloud is spaced wider
    than its own neighbourhood radius, so it compares zero to zero and prints
    VERIFIED.

    None of those are lies. Each is a real metric computed on nothing, or a
    branch that no input reaches. The common structure is that the instrument
    was never shown to be capable of returning null.

    This is the runtime companion to vacuity_lint, which finds the same defect
    statically. Here the rule is enforced by construction:

        NO PREDICTION IS REPORTED UNLESS EVERY GATE PASSES.

    A gate is a claim about the INSTRUMENT, not the hypothesis: a ceiling that
    proves the channel carries signal, a floor that proves the comparison is
    unconfounded, an identity that proves the arithmetic is what you think.

WHAT IT BUYS, MEASURED
    Both experiments this was extracted from hit a dead instrument on run one.
    kx_probe: the budget happened to equal all-nodes-at-2, so every arm produced
    identical allocations -- the anti-vacuity gate caught it before a number
    existed to be wrong about. kx_synth: a constant marginal made the allocator
    walk node 0 to the ceiling before node 1 got anything, so the "uniform"
    floor was not uniform; the shuffled arm scoring +0.8686 exposed it. A second
    independent implementation hit the identical defect the same week.

USAGE
    from prereg import Study

    s = Study("my experiment")
    s.gate("oracle beats uniform", lambda: oracle_gain > 0.10, expect=">0.10")
    s.gate("shuffled does not win", lambda: shuffled_gain <= 0.02, expect="<=0.02")
    s.predict("P1", "curvature correlates with r", lambda: abs(rho) > 0.05,
              value=f"rho={rho:+.4f}")
    s.predict("P2", "beats uniform at matched budget", lambda: gain > 0.10,
              value=f"{gain:+.4f}")
    s.open_question("P3", "repeat with Ollivier-Ricci")
    raise SystemExit(s.report())

    Exit code 0 whether predictions pass or fail -- a refutation is a result.
    Exit code 1 only when a GATE fails, because then there is no result.

SELFTEST
    python3 prereg.py --selftest
    Feeds the harness a rigged gate and confirms the report is suppressed. If
    this file could not suppress, it would be the thing it was written against.

Author: Chad Edward Holland. Extracted with Claude (Anthropic) from
kx_probe.py and kx_synth.py. Vincit Omnia Veritas.
"""

import sys

BAR = "=" * 68


class Study:
    def __init__(self, title, quiet=False):
        self.title = title
        self.quiet = quiet
        self._gates = []
        self._preds = []
        self._open = []
        self._notes = []

    # ---- gates: claims about the instrument
    def gate(self, name, fn, expect=""):
        """A gate must establish that the instrument CAN return null, or that
        the comparison is unconfounded. Not that the hypothesis is true."""
        try:
            ok = bool(fn())
            err = None
        except Exception as e:                      # a gate that crashes fails
            ok, err = False, repr(e)
        self._gates.append((name, ok, expect, err))
        return ok

    # ---- predictions: claims about the world, registered before running
    def predict(self, tag, name, fn, value="", refuted_note=""):
        try:
            ok = bool(fn())
            err = None
        except Exception as e:
            ok, err = False, repr(e)
        self._preds.append((tag, name, ok, value, err, refuted_note))
        return ok

    def open_question(self, tag, name):
        """Every study ends with a door. Reported, never evaluated."""
        self._open.append((tag, name))

    def note(self, text):
        """An observation that is NOT a registered claim. Printed as such."""
        self._notes.append(text)

    # ---- report
    def report(self):
        out = []
        w = out.append
        w(BAR); w(self.title); w(BAR)

        w("\n--- gates (can this instrument return null?) ---")
        for name, ok, expect, err in self._gates:
            line = f"    {'PASS' if ok else 'FAIL'}  {name}"
            if expect:
                line += f"   [{expect}]"
            if err:
                line += f"   raised {err}"
            w(line)

        failed = [g for g in self._gates if not g[1]]
        if not self._gates:
            w("\n    NO GATES DECLARED.")
            w("    A study with no gates cannot show its instrument is live.")
            w("    No predictions reported.")
            if not self.quiet:
                print("\n".join(out))
            return 1
        if failed:
            w(f"\n{len(failed)} gate(s) failed. The instrument is not")
            w("demonstrably able to return null, so NO PREDICTION IS REPORTED")
            w("-- in either direction. Fix the harness, then re-run.")
            if not self.quiet:
                print("\n".join(out))
            return 1

        w("\n--- registered predictions ---")
        for tag, name, ok, value, err, rn in self._preds:
            w(f"    {tag}  {'PASS' if ok else 'REFUTED'}  {name}"
              + (f"   {value}" if value else "")
              + (f"   raised {err}" if err else ""))
            if not ok and rn:
                w(f"          kept: {rn}")

        if self._notes:
            w("\n--- observations (NOT registered claims) ---")
            for t in self._notes:
                w(f"    {t}")

        if self._open:
            w("\n--- left unrun ---")
            for tag, name in self._open:
                w(f"    {tag}  {name}")
        else:
            w("\n    WARNING: no open prediction. Every study ends with a door.")

        n_ref = sum(1 for p in self._preds if not p[2])
        w(f"\n{len(self._preds)} registered, {n_ref} refuted and kept.")
        if not self.quiet:
            print("\n".join(out))
        return 0


# ------------------------------------------------------------------ selftest

def _selftest():
    print("prereg.py selftest -- the harness must be able to suppress itself\n")
    fails = []

    # 1. a failing gate must suppress a PASSING prediction
    s = Study("rigged: gate fails, prediction would pass", quiet=True)
    s.gate("oracle beats floor", lambda: False, expect="must be live")
    s.predict("P1", "hypothesis holds", lambda: True, value="looks great")
    s.open_question("P2", "unrun")
    rc = s.report()
    ok = (rc == 1)
    print(f"  [{'ok' if ok else 'FAIL'}] failing gate suppresses report (rc={rc}, want 1)")
    if not ok: fails.append("gate-suppression")

    # 2. a study with NO gates must be refused
    s = Study("rigged: no gates at all", quiet=True)
    s.predict("P1", "hypothesis holds", lambda: True)
    rc = s.report()
    ok = (rc == 1)
    print(f"  [{'ok' if ok else 'FAIL'}] no gates is refused (rc={rc}, want 1)")
    if not ok: fails.append("no-gates")

    # 3. a gate that raises must count as failed, not crash the run
    s = Study("rigged: gate raises", quiet=True)
    s.gate("boom", lambda: 1 / 0)
    s.predict("P1", "hypothesis holds", lambda: True)
    rc = s.report()
    ok = (rc == 1)
    print(f"  [{'ok' if ok else 'FAIL'}] raising gate counts as failed (rc={rc}, want 1)")
    if not ok: fails.append("gate-raises")

    # 4. gates passing + prediction REFUTED is still a reported result
    s = Study("honest: gates pass, prediction refuted", quiet=True)
    s.gate("oracle beats floor", lambda: True)
    s.predict("P1", "hypothesis holds", lambda: False, value="-0.2932",
              refuted_note="lost to uniform at matched budget")
    s.open_question("P2", "unrun")
    rc = s.report()
    ok = (rc == 0)
    print(f"  [{'ok' if ok else 'FAIL'}] refutation is a RESULT, not an error (rc={rc}, want 0)")
    if not ok: fails.append("refutation-is-result")

    # 5. the suppression must be visible in the text, not silent
    s = Study("rigged", quiet=True)
    s.gate("dead", lambda: False)
    s.predict("P1", "x", lambda: True)
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        s.quiet = False
        s.report()
    txt = buf.getvalue()
    ok = "NO PREDICTION IS REPORTED" in txt and "P1" not in txt
    print(f"  [{'ok' if ok else 'FAIL'}] suppressed report does not leak the prediction")
    if not ok: fails.append("leak")

    print()
    if fails:
        print(f"SELFTEST FAILED: {', '.join(fails)}")
        return 1
    print("SELFTEST PASSED: 5/5. The harness can refuse to report.")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    print(__doc__)
    print("Run with --selftest to verify the harness can suppress itself.")
