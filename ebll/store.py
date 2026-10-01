"""
Append-only store for DecisionRecord, OutcomeRecord, Hypothesis,
EvaluationResult, and PromotionRecord.

Invariants:
- No mutation of existing records.
- No deletion.
- Evaluation layer can only append.
- Lookup is by id; original bytes/fingerprint are retained.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from .records import (
    DecisionRecord,
    OutcomeRecord,
    LearningCase,
    Hypothesis,
    EvaluationResult,
    PromotionRecord,
)


class AppendOnlyStore:
    """In-memory append-only store. Suitable for deterministic reference runs."""

    def __init__(self) -> None:
        self._decisions: Dict[str, DecisionRecord] = {}
        self._outcomes: Dict[str, OutcomeRecord] = {}
        self._hypotheses: Dict[str, Hypothesis] = {}
        self._evaluations: Dict[str, EvaluationResult] = {}
        self._promotions: Dict[str, PromotionRecord] = {}
        self._append_log: List[str] = []

    def append_decision(self, rec: DecisionRecord) -> None:
        if rec.decision_id in self._decisions:
            raise ValueError(
                f"Decision {rec.decision_id} already exists; store is append-only"
            )
        self._decisions[rec.decision_id] = rec
        self._append_log.append(f"decision:{rec.decision_id}")

    def append_outcome(self, rec: OutcomeRecord) -> None:
        if rec.outcome_id in self._outcomes:
            raise ValueError(
                f"Outcome {rec.outcome_id} already exists; store is append-only"
            )
        if rec.decision_id not in self._decisions:
            raise ValueError(
                f"Outcome references unknown decision_id={rec.decision_id}"
            )
        self._outcomes[rec.outcome_id] = rec
        self._append_log.append(f"outcome:{rec.outcome_id}")

    def append_hypothesis(self, hyp: Hypothesis) -> None:
        if hyp.hypothesis_id in self._hypotheses:
            raise ValueError(
                f"Hypothesis {hyp.hypothesis_id} already exists; store is append-only"
            )
        self._hypotheses[hyp.hypothesis_id] = hyp
        self._append_log.append(f"hypothesis:{hyp.hypothesis_id}")

    def append_evaluation(self, ev: EvaluationResult) -> None:
        if ev.evaluation_id in self._evaluations:
            raise ValueError(
                f"Evaluation {ev.evaluation_id} already exists; store is append-only"
            )
        if ev.hypothesis_id not in self._hypotheses:
            raise ValueError(
                f"Evaluation references unregistered hypothesis_id={ev.hypothesis_id}"
            )
        self._evaluations[ev.evaluation_id] = ev
        self._append_log.append(f"evaluation:{ev.evaluation_id}")

    def append_promotion(self, promo: PromotionRecord) -> None:
        if promo.promotion_id in self._promotions:
            raise ValueError(
                f"Promotion {promo.promotion_id} already exists; store is append-only"
            )
        if promo.evaluation_id not in self._evaluations:
            raise ValueError(
                f"Promotion references unknown evaluation_id={promo.evaluation_id}"
            )
        self._promotions[promo.promotion_id] = promo
        self._append_log.append(f"promotion:{promo.promotion_id}")

    def get_decision(self, decision_id: str) -> Optional[DecisionRecord]:
        return self._decisions.get(decision_id)

    def get_outcome(self, outcome_id: str) -> Optional[OutcomeRecord]:
        return self._outcomes.get(outcome_id)

    def get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        return self._hypotheses.get(hypothesis_id)

    def get_evaluation(self, evaluation_id: str) -> Optional[EvaluationResult]:
        return self._evaluations.get(evaluation_id)

    def get_promotion(self, promotion_id: str) -> Optional[PromotionRecord]:
        return self._promotions.get(promotion_id)

    def list_decisions(self) -> List[DecisionRecord]:
        return list(self._decisions.values())

    def list_outcomes(self) -> List[OutcomeRecord]:
        return list(self._outcomes.values())

    def list_hypotheses(self) -> List[Hypothesis]:
        return list(self._hypotheses.values())

    def list_evaluations(self) -> List[EvaluationResult]:
        return list(self._evaluations.values())

    def list_promotions(self) -> List[PromotionRecord]:
        return list(self._promotions.values())

    def make_learning_cases(self) -> List[LearningCase]:
        cases: List[LearningCase] = []
        outcomes_by_decision: Dict[str, List[OutcomeRecord]] = {}
        for o in self._outcomes.values():
            outcomes_by_decision.setdefault(o.decision_id, []).append(o)
        for d in self._decisions.values():
            for o in outcomes_by_decision.get(d.decision_id, []):
                cases.append(
                    LearningCase(
                        case_id=f"{d.decision_id}::{o.outcome_id}",
                        decision=d,
                        outcome=o,
                        provenance="joined_from_append_only_store",
                    )
                )
        return cases

    def append_log(self) -> List[str]:
        return list(self._append_log)

    def fingerprints(self) -> Dict[str, str]:
        out: Dict[str, str] = {}
        for d in self._decisions.values():
            out[f"decision:{d.decision_id}"] = d.fingerprint()
        for o in self._outcomes.values():
            out[f"outcome:{o.outcome_id}"] = o.fingerprint()
        for h in self._hypotheses.values():
            out[f"hypothesis:{h.hypothesis_id}"] = h.fingerprint()
        for e in self._evaluations.values():
            out[f"evaluation:{e.evaluation_id}"] = e.fingerprint()
        return out
