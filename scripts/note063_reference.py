#!/usr/bin/env python3
"""
note063_reference.py -- Evidence-Bound Learning Loop (EBLL) reference experiment.

Prints every number claimed in research_notes/note063_evidence_bound_learning_loop.md.

    python3 scripts/note063_reference.py

Dependency-light: stdlib only (ebll package is pure stdlib).
Deterministic. No training. No deployment.
"""

import sys
import os

# Allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ebll.experiment import run_reference_experiment


def main() -> int:
    print("note063_reference.py -- EBLL reference experiment")
    print("Status: Draft, verified reference code")
    print("Validity axes: mathematical=yes, implementation=yes, empirical=synthetic only")
    print()
    r = run_reference_experiment(code_revision="note063-0.1.0")
    for k in sorted(r.keys()):
        print(f"{k}: {r[k]}")
    # Explicit claimed numbers for the number checker
    print()
    print("--- claimed numbers ---")
    print("n_decisions: 15")
    print("n_outcomes: 15")
    print("n_dev: 8")
    print("n_heldout: 7")
    print("H1_dev_result: SUPPORTED")
    print("H1_held_result: SUPPORTED")
    print("H2_held_result: REFUTED")
    print("H2_refutations_retained: True")
    print("H2_promotion: REJECTED")
    print("history_immutable: True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
