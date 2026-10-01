"""
Focused tests for Evidence-Bound Learning Loop invariants.
"""

from __future__ import annotations

import pytest
from ebll.records import (
    DecisionRecord,
    OutcomeRecord,
    Hypothesis,
    OutcomeStatus,
    PromotionStatus,
    LearningCase,
)
from ebll.store import AppendOnlyStore
from ebll.evaluator import Evaluator
from ebll.experiment import (
    run_reference_experiment,
    build_synthetic_history,
    baseline_v1,
    candidate_v2,
)


def _dec(did: str = "d1") -> DecisionRecord:
    return DecisionRecord(
        decision_id=did,
        agent_version="v1",
        proposal="p",
        available_evidence=("stable",),
        gate_decision="ALLOW",
        constraints=(),
        action="a",
        decision_timestamp="2026-01-01T00:00:00Z",
        provenance="test",
    )


def _out(did: str = "d1", oid: str = "o1", success: bool = True) -> OutcomeRecord:
    return OutcomeRecord(
        outcome_id=oid,
        decision_id=did,
        observed_outcome="ok" if success else "fail",
        outcome_timestamp="2026-01-01T01:00:00Z",
        success=success,
        metrics=(("success", 1.0 if success else 0.0),),
        provenance="test",
    )


def test_records_immutable():
    d = _dec()
    with pytest.raises(Exception):
        d.decision_id = "mutated"  # type: ignore


def test_store_append_only_rejects_duplicate():
    store = AppendOnlyStore()
    store.append_decision(_dec())
    with pytest.raises(ValueError, match="append-only"):
        store.append_decision(_dec())


def test_outcome_requires_existing_decision():
    store = AppendOnlyStore()
    with pytest.raises(ValueError, match="unknown decision"):
        store.append_outcome(_out())


def test_hypothesis_before_evaluation():
    store = AppendOnlyStore()
    store.append_decision(_dec())
    store.append_outcome(_out())
    cases = store.make_learning_cases()
    ev = Evaluator(store, agent_fn_baseline=baseline_v1, agent_fn_candidate=candidate_v2)
    with pytest.raises(ValueError, match="not registered"):
        ev.evaluate(
            "H-missing",
            cases,
            dataset_id="t",
            dataset_version="1",
            evaluation_protocol="p",
        )


def test_evaluation_references_cases():
    store = AppendOnlyStore()
    build_synthetic_history(store)
    cases = [c for c in store.make_learning_cases() if c.decision.decision_id.startswith("d")]
    hyp = Hypothesis(
        hypothesis_id="H-ref",
        statement="test",
        candidate_version="v2",
        baseline_version="v1",
        prediction="delta>0",
        registered_at="2026-01-01T00:00:00Z",
        dataset_id="t",
        dataset_version="1",
        evaluation_protocol="p",
        anti_vacuity="a",
    )
    ev = Evaluator(store, agent_fn_baseline=baseline_v1, agent_fn_candidate=candidate_v2)
    ev.register_hypothesis(hyp)
    r = ev.evaluate("H-ref", cases, "t", "1", "p")
    assert len(r.learning_case_ids) == len(cases)
    assert all(cid in {c.case_id for c in cases} for cid in r.learning_case_ids)


def test_supported_requires_evaluation():
    store = AppendOnlyStore()
    build_synthetic_history(store)
    cases = [c for c in store.make_learning_cases() if c.decision.decision_id.startswith("h")]
    hyp = Hypothesis(
        hypothesis_id="H-sup",
        statement="v2 better",
        candidate_version="v2",
        baseline_version="v1",
        prediction="delta>0",
        registered_at="2026-01-01T00:00:00Z",
        dataset_id="t",
        dataset_version="1",
        evaluation_protocol="p",
        anti_vacuity="a",
    )
    ev = Evaluator(store, agent_fn_baseline=baseline_v1, agent_fn_candidate=candidate_v2)
    ev.register_hypothesis(hyp)
    r = ev.evaluate("H-sup", cases, "t", "1", "p")
    assert r.result == OutcomeStatus.SUPPORTED
    promo = ev.propose_promotion(r.evaluation_id, "ok")
    assert promo.status == PromotionStatus.PROPOSED


def test_refuted_retained():
    store = AppendOnlyStore()
    build_synthetic_history(store)
    cases = [c for c in store.make_learning_cases() if c.decision.decision_id.startswith("h")]

    def always_yes_match(case: LearningCase) -> bool:
        return True == bool(case.outcome.success)

    def baseline_match(case: LearningCase) -> bool:
        return baseline_v1(case) == bool(case.outcome.success)

    hyp = Hypothesis(
        hypothesis_id="H-refute",
        statement="always-yes better",
        candidate_version="v3",
        baseline_version="v1",
        prediction="delta>0",
        registered_at="2026-01-01T00:00:00Z",
        dataset_id="t",
        dataset_version="1",
        evaluation_protocol="p",
        anti_vacuity="a",
    )
    ev = Evaluator(store, agent_fn_baseline=baseline_match, agent_fn_candidate=always_yes_match)
    ev.register_hypothesis(hyp)
    r = ev.evaluate("H-refute", cases, "t", "1", "p")
    assert r.result == OutcomeStatus.REFUTED
    assert len(r.refutations) > 0
    assert store.get_evaluation(r.evaluation_id) is not None
    assert store.get_hypothesis("H-refute") is not None


def test_missing_evidence_not_positive():
    store = AppendOnlyStore()
    hyp = Hypothesis(
        hypothesis_id="H-empty",
        statement="s",
        candidate_version="v2",
        baseline_version="v1",
        prediction="p",
        registered_at="2026-01-01T00:00:00Z",
        dataset_id="t",
        dataset_version="1",
        evaluation_protocol="p",
        anti_vacuity="a",
    )
    ev = Evaluator(store, agent_fn_baseline=baseline_v1, agent_fn_candidate=candidate_v2)
    ev.register_hypothesis(hyp)
    r = ev.evaluate("H-empty", [], "t", "1", "p", min_cases=1)
    assert r.result == OutcomeStatus.INSUFFICIENT_EVIDENCE


def test_evaluation_not_governance_authorization():
    store = AppendOnlyStore()
    build_synthetic_history(store)
    cases = [c for c in store.make_learning_cases() if c.decision.decision_id.startswith("h")]
    hyp = Hypothesis(
        hypothesis_id="H-gov",
        statement="s",
        candidate_version="v2",
        baseline_version="v1",
        prediction="p",
        registered_at="2026-01-01T00:00:00Z",
        dataset_id="t",
        dataset_version="1",
        evaluation_protocol="p",
        anti_vacuity="a",
    )
    ev = Evaluator(store, agent_fn_baseline=baseline_v1, agent_fn_candidate=candidate_v2)
    ev.register_hypothesis(hyp)
    r = ev.evaluate("H-gov", cases, "t", "1", "p")
    promo = ev.propose_promotion(r.evaluation_id, "r")
    assert promo.status in (PromotionStatus.PROPOSED, PromotionStatus.REJECTED)
    assert promo.status != PromotionStatus.ADMITTED


def test_dataset_and_code_revision_recorded():
    store = AppendOnlyStore()
    build_synthetic_history(store)
    cases = store.make_learning_cases()[:3]
    hyp = Hypothesis(
        hypothesis_id="H-meta",
        statement="s",
        candidate_version="v2",
        baseline_version="v1",
        prediction="p",
        registered_at="2026-01-01T00:00:00Z",
        dataset_id="my-ds",
        dataset_version="9.9",
        evaluation_protocol="proto-x",
        anti_vacuity="a",
    )
    ev = Evaluator(
        store,
        code_revision="rev-abc",
        agent_fn_baseline=baseline_v1,
        agent_fn_candidate=candidate_v2,
    )
    ev.register_hypothesis(hyp)
    r = ev.evaluate("H-meta", cases, "my-ds", "9.9", "proto-x")
    assert r.dataset_id == "my-ds"
    assert r.dataset_version == "9.9"
    assert r.code_revision == "rev-abc"
    assert r.evaluation_protocol == "proto-x"


def test_deterministic_replay():
    r1 = run_reference_experiment(code_revision="replay-test")
    r2 = run_reference_experiment(code_revision="replay-test")
    for k in (
        "n_decisions",
        "n_outcomes",
        "n_dev",
        "n_heldout",
        "H1_dev_result",
        "H1_held_result",
        "H2_held_result",
        "H2_refutations_retained",
        "H2_promotion",
        "history_immutable",
    ):
        assert r1[k] == r2[k], f"nondeterministic on {k}"


def test_reference_experiment_numbers():
    r = run_reference_experiment()
    assert r["n_decisions"] == 15
    assert r["n_outcomes"] == 15
    assert r["n_dev"] == 8
    assert r["n_heldout"] == 7
    assert r["H1_dev_result"] == "SUPPORTED"
    assert r["H1_held_result"] == "SUPPORTED"
    assert r["H2_held_result"] == "REFUTED"
    assert r["H2_refutations_retained"] is True
    assert r["H2_promotion"] == "REJECTED"
    assert r["history_immutable"] is True
