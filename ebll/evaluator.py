"""
Evaluator: registers hypotheses, runs deterministic comparisons,
produces EvaluationResult and optional PromotionRecord.

Critical invariants enforced here:
- Hypothesis must be registered before evaluation.
- Original decision/outcome records are never mutated.
- SUPPORTED requires an executed evaluation with evidence.
- Failed hypotheses become REFUTED and are retained.
- Missing evidence yields INSUFFICIENT_EVIDENCE, never positive evidence.
- Evaluation result != governance authorization.
- Promotion is admission proposal only.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple
from datetime import datetime, timezone

from .records import (
    Hypothesis,
    EvaluationResult,
    PromotionRecord,
    LearningCase,
    OutcomeStatus,
    PromotionStatus,
    content_hash,
)
from .store import AppendOnlyStore


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Evaluator:
    """
    Principia side of the loop. Holds a reference to the append-only store
    but never mutates historical decision/outcome records.
    """

    def __init__(
        self,
        store: AppendOnlyStore,
        code_revision: str = "unknown",
        agent_fn_baseline: Optional[Callable[[LearningCase], bool]] = None,
        agent_fn_candidate: Optional[Callable[[LearningCase], bool]] = None,
    ) -> None:
        self.store = store
        self.code_revision = code_revision
        self._fn_baseline = agent_fn_baseline
        self._fn_candidate = agent_fn_candidate
        self._registered_before_eval: Dict[str, bool] = {}

    def register_hypothesis(self, hyp: Hypothesis) -> None:
        """Must be called before evaluate()."""
        self.store.append_hypothesis(hyp)
        self._registered_before_eval[hyp.hypothesis_id] = True

    def evaluate(
        self,
        hypothesis_id: str,
        cases: Sequence[LearningCase],
        dataset_id: str,
        dataset_version: str,
        evaluation_protocol: str,
        *,
        min_cases: int = 1,
    ) -> EvaluationResult:
        """
        Run candidate vs baseline on the supplied cases.
        Hypothesis must already be registered.
        """
        hyp = self.store.get_hypothesis(hypothesis_id)
        if hyp is None:
            raise ValueError(
                f"Hypothesis {hypothesis_id} is not registered. "
                "Register before evaluation (invariant 3)."
            )
        if not self._registered_before_eval.get(hypothesis_id, False):
            raise ValueError(
                f"Hypothesis {hypothesis_id} was not registered via "
                "register_hypothesis before evaluate (invariant 3)."
            )

        if len(cases) < min_cases:
            result = OutcomeStatus.INSUFFICIENT_EVIDENCE
            metrics: List[Tuple[str, float]] = [("n_cases", float(len(cases)))]
            failures: Tuple[str, ...] = (f"fewer than min_cases={min_cases}",)
            refutations: Tuple[str, ...] = ()
        elif self._fn_baseline is None or self._fn_candidate is None:
            result = OutcomeStatus.COULD_NOT_RUN_AS_REGISTERED
            metrics = [("n_cases", float(len(cases)))]
            failures = ("agent functions not supplied",)
            refutations = ()
        else:
            baseline_correct = 0
            candidate_correct = 0
            n = 0
            for case in cases:
                b_ok = self._fn_baseline(case)
                c_ok = self._fn_candidate(case)
                if b_ok:
                    baseline_correct += 1
                if c_ok:
                    candidate_correct += 1
                n += 1
            baseline_rate = baseline_correct / n if n else 0.0
            candidate_rate = candidate_correct / n if n else 0.0
            metrics = [
                ("n_cases", float(n)),
                ("baseline_correct", float(baseline_correct)),
                ("candidate_correct", float(candidate_correct)),
                ("baseline_rate", baseline_rate),
                ("candidate_rate", candidate_rate),
                ("delta", candidate_rate - baseline_rate),
            ]
            failures = ()
            if candidate_rate > baseline_rate:
                result = OutcomeStatus.SUPPORTED
                refutations = ()
            elif candidate_rate < baseline_rate:
                result = OutcomeStatus.REFUTED
                refutations = (
                    f"candidate_rate={candidate_rate:.4f} < "
                    f"baseline_rate={baseline_rate:.4f}",
                )
            else:
                result = OutcomeStatus.INSUFFICIENT_EVIDENCE
                refutations = (
                    f"candidate_rate == baseline_rate == {candidate_rate:.4f}",
                )

        eval_id = (
            f"eval-{hypothesis_id}-{dataset_id}-"
            f"{content_hash({'n': len(cases), 'ds': dataset_version})}"
        )
        ev = EvaluationResult(
            evaluation_id=eval_id,
            hypothesis_id=hypothesis_id,
            learning_case_ids=tuple(c.case_id for c in cases),
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            evaluation_protocol=evaluation_protocol,
            candidate_version=hyp.candidate_version,
            baseline_version=hyp.baseline_version,
            result=result,
            metrics=tuple(metrics),
            failures=failures,
            refutations=refutations,
            reproducibility=(
                f"deterministic; code_revision={self.code_revision}"
            ),
            code_revision=self.code_revision,
            evaluated_at=_utc_now(),
            provenance="ebll.evaluator",
            promotion_status=PromotionStatus.NOT_PROPOSED,
        )
        self.store.append_evaluation(ev)
        return ev

    def propose_promotion(
        self,
        evaluation_id: str,
        rationale: str,
    ) -> PromotionRecord:
        """
        Create a promotion record only if the evaluation exists.
        SUPPORTED -> PROPOSED; otherwise REJECTED.
        Still only an admission proposal, never a deploy instruction.
        """
        ev = self.store.get_evaluation(evaluation_id)
        if ev is None:
            raise ValueError(f"Unknown evaluation_id={evaluation_id}")
        if ev.result != OutcomeStatus.SUPPORTED:
            status = PromotionStatus.REJECTED
            rationale = (
                f"Rejected: evaluation result was {ev.result.value}, "
                f"not SUPPORTED. Original rationale: {rationale}"
            )
        else:
            status = PromotionStatus.PROPOSED
        promo = PromotionRecord(
            promotion_id=f"promo-{evaluation_id}",
            evaluation_id=evaluation_id,
            hypothesis_id=ev.hypothesis_id,
            candidate_version=ev.candidate_version,
            status=status,
            rationale=rationale,
            recorded_at=_utc_now(),
            provenance="ebll.evaluator.propose_promotion",
        )
        self.store.append_promotion(promo)
        return promo
