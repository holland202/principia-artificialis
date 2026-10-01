"""
Reference experiment for Evidence-Bound Learning Loop (EBLL).

Demonstrates:
  historical evidence
  -> hypothesis registration
  -> candidate evaluation (dev + held-out)
  -> SUPPORTED / REFUTED / INSUFFICIENT_EVIDENCE
  -> retained refutation
  -> promotion as admission proposal only

Baseline v1: simple rule that succeeds when evidence contains "stable".
Candidate v2: improved rule that also succeeds on "partial".
Candidate v3: deliberately worse rule (always yes) -> REFUTED on held-out.

No training. No deployment. Synthetic deterministic history only.
"""

from __future__ import annotations

from typing import List, Tuple
from datetime import datetime, timezone

from .records import (
    DecisionRecord,
    OutcomeRecord,
    Hypothesis,
    OutcomeStatus,
    PromotionStatus,
    LearningCase,
)
from .store import AppendOnlyStore
from .evaluator import Evaluator


def _ts(i: int) -> str:
    return f"2026-09-2{i % 10}T12:00:00Z"


def build_synthetic_history(store: AppendOnlyStore) -> None:
    """Populate a tiny deterministic decision/outcome set."""
    specs = [
        ("d01", ("stable", "sensor_ok"), "ALLOW", "proceed", True, "dev"),
        ("d02", ("partial",), "ALLOW", "proceed", True, "dev"),
        ("d03", ("noisy",), "DEFER", "wait", False, "dev"),
        ("d04", ("stable", "partial"), "ALLOW", "proceed", True, "dev"),
        ("d05", ("unstable",), "REFUSE", "abort", False, "dev"),
        ("d06", ("stable",), "ALLOW", "proceed", True, "dev"),
        ("d07", ("partial", "noisy"), "ALLOW", "proceed", True, "dev"),
        ("d08", ("unknown",), "DEFER", "wait", False, "dev"),
        ("h01", ("stable",), "ALLOW", "proceed", True, "heldout"),
        ("h02", ("partial",), "ALLOW", "proceed", True, "heldout"),
        ("h03", ("noisy",), "DEFER", "wait", False, "heldout"),
        ("h04", ("stable", "extra"), "ALLOW", "proceed", True, "heldout"),
        ("h05", ("unstable", "partial"), "REFUSE", "abort", False, "heldout"),
        ("h06", ("partial",), "ALLOW", "proceed", True, "heldout"),
        ("h07", ("noisy", "unknown"), "DEFER", "wait", False, "heldout"),
    ]
    for i, (did, evidence, gate, action, success, _split) in enumerate(specs):
        store.append_decision(
            DecisionRecord(
                decision_id=did,
                agent_version="v1",
                proposal=f"handle case {did}",
                available_evidence=evidence,
                gate_decision=gate,
                constraints=("safety_first",),
                action=action,
                decision_timestamp=_ts(i),
                provenance="synthetic_reference",
            )
        )
        store.append_outcome(
            OutcomeRecord(
                outcome_id=f"o-{did}",
                decision_id=did,
                observed_outcome="ok" if success else "fail",
                outcome_timestamp=_ts(i + 1),
                success=success,
                metrics=(("success", 1.0 if success else 0.0),),
                provenance="synthetic_reference",
            )
        )


def baseline_v1(case: LearningCase) -> bool:
    """Succeeds iff evidence contains 'stable'."""
    return "stable" in case.decision.available_evidence


def candidate_v2(case: LearningCase) -> bool:
    """Improved: succeeds on 'stable' or 'partial'."""
    ev = case.decision.available_evidence
    return "stable" in ev or "partial" in ev


def candidate_v3_always_yes(case: LearningCase) -> bool:
    """Deliberately failing candidate: always predicts success."""
    return True


def run_reference_experiment(code_revision: str = "ebll-0.1.0") -> dict:
    """
    Execute the full reference loop and return a summary dict of printed numbers.
    """
    store = AppendOnlyStore()
    build_synthetic_history(store)
    all_cases = store.make_learning_cases()
    dev_cases = [c for c in all_cases if c.decision.decision_id.startswith("d")]
    held_cases = [c for c in all_cases if c.decision.decision_id.startswith("h")]

    results = {
        "n_decisions": len(store.list_decisions()),
        "n_outcomes": len(store.list_outcomes()),
        "n_dev": len(dev_cases),
        "n_heldout": len(held_cases),
    }

    hyp1 = Hypothesis(
        hypothesis_id="H1-v2-improves",
        statement=(
            "Candidate v2 (stable|partial) will achieve a higher success rate "
            "than baseline v1 (stable only) on both development and held-out data."
        ),
        candidate_version="v2",
        baseline_version="v1",
        prediction="candidate_rate > baseline_rate on dev and on held-out",
        registered_at="2026-09-30T10:00:00Z",
        dataset_id="synthetic_ebll_v1",
        dataset_version="1.0",
        evaluation_protocol=(
            "strict rate comparison; candidate must strictly exceed baseline; "
            "held-out is never used for hypothesis formation"
        ),
        anti_vacuity="baseline and candidate can both return False on noisy/unknown",
        provenance="note063_reference",
    )
    ev1 = Evaluator(
        store,
        code_revision=code_revision,
        agent_fn_baseline=baseline_v1,
        agent_fn_candidate=candidate_v2,
    )
    ev1.register_hypothesis(hyp1)
    fps_before = store.fingerprints()

    r_dev = ev1.evaluate(
        "H1-v2-improves",
        dev_cases,
        dataset_id="synthetic_ebll_v1",
        dataset_version="1.0-dev",
        evaluation_protocol=hyp1.evaluation_protocol,
    )
    r_held = ev1.evaluate(
        "H1-v2-improves",
        held_cases,
        dataset_id="synthetic_ebll_v1",
        dataset_version="1.0-heldout",
        evaluation_protocol=hyp1.evaluation_protocol,
    )
    fps_after = store.fingerprints()
    for k, v in fps_before.items():
        assert fps_after.get(k) == v, f"history mutated: {k}"

    results["H1_dev_result"] = r_dev.result.value
    results["H1_held_result"] = r_held.result.value
    results["H1_dev_delta"] = dict(r_dev.metrics).get("delta", 0.0)
    results["H1_held_delta"] = dict(r_held.metrics).get("delta", 0.0)

    if r_held.result == OutcomeStatus.SUPPORTED:
        promo = ev1.propose_promotion(
            r_held.evaluation_id,
            rationale="v2 strictly better on held-out; admission proposal only",
        )
        results["H1_promotion"] = promo.status.value
    else:
        results["H1_promotion"] = "NOT_PROPOSED"

    hyp2 = Hypothesis(
        hypothesis_id="H2-v3-always-yes",
        statement=(
            "Candidate v3 (always predict success) will achieve a higher "
            "success rate than baseline v1 on held-out data."
        ),
        candidate_version="v3",
        baseline_version="v1",
        prediction="candidate_rate > baseline_rate on held-out",
        registered_at="2026-09-30T10:05:00Z",
        dataset_id="synthetic_ebll_v1",
        dataset_version="1.0",
        evaluation_protocol=hyp1.evaluation_protocol,
        anti_vacuity="always-yes cannot return False; vacuity risk acknowledged",
        provenance="note063_reference",
    )

    def baseline_match(case: LearningCase) -> bool:
        pred = baseline_v1(case)
        return pred == bool(case.outcome.success)

    def v3_match(case: LearningCase) -> bool:
        pred = candidate_v3_always_yes(case)
        return pred == bool(case.outcome.success)

    ev2 = Evaluator(
        store,
        code_revision=code_revision,
        agent_fn_baseline=baseline_match,
        agent_fn_candidate=v3_match,
    )
    ev2.register_hypothesis(hyp2)
    r_v3 = ev2.evaluate(
        "H2-v3-always-yes",
        held_cases,
        dataset_id="synthetic_ebll_v1",
        dataset_version="1.0-heldout",
        evaluation_protocol=hyp2.evaluation_protocol,
    )
    results["H2_held_result"] = r_v3.result.value
    results["H2_refutations_retained"] = len(r_v3.refutations) > 0
    results["H2_n_refutations"] = len(r_v3.refutations)

    promo2 = ev2.propose_promotion(
        r_v3.evaluation_id,
        rationale="should be rejected because not SUPPORTED",
    )
    results["H2_promotion"] = promo2.status.value

    results["n_evaluations"] = len(store.list_evaluations())
    results["n_promotions"] = len(store.list_promotions())
    results["n_hypotheses"] = len(store.list_hypotheses())
    results["history_immutable"] = True
    return results


def main() -> None:
    print("EBLL reference experiment (note063)")
    print("===================================")
    r = run_reference_experiment()
    for k, v in sorted(r.items()):
        print(f"  {k}: {v}")
    print()
    print("Claimed numbers (must appear above):")
    print("  n_decisions: 15")
    print("  n_outcomes: 15")
    print("  n_dev: 8")
    print("  n_heldout: 7")
    print("  H1_dev_result: SUPPORTED")
    print("  H1_held_result: SUPPORTED")
    print("  H2_held_result: REFUTED")
    print("  H2_refutations_retained: True")
    print("  H2_promotion: REJECTED")
    print("  history_immutable: True")


if __name__ == "__main__":
    main()
