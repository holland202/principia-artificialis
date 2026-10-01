"""
Immutable record types for the Evidence-Bound Learning Loop.

All records are frozen dataclasses. Once constructed they cannot be
mutated. The evaluation layer may only append new records that refer
to prior ones by id.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, Optional, Tuple
import hashlib
import json


class OutcomeStatus(str, Enum):
    """Aligned with SWAY Amendment 1 outcome vocabulary where applicable."""
    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_RUN = "NOT_RUN"
    VACUOUS = "VACUOUS"
    COULD_NOT_RUN_AS_REGISTERED = "COULD_NOT_RUN_AS_REGISTERED"
    IMPLEMENTATION_ERROR = "IMPLEMENTATION_ERROR"
    UNRESOLVED = "UNRESOLVED"


class PromotionStatus(str, Enum):
    """Promotion is a proposal/result for admission, not a deploy instruction."""
    NOT_PROPOSED = "NOT_PROPOSED"
    PROPOSED = "PROPOSED"
    ADMITTED = "ADMITTED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def content_hash(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class DecisionRecord:
    """
    Sovereign Veritas side: what was known and decided at decision time.
    Immutable. Principia may only reference it, never rewrite it.
    """
    decision_id: str
    agent_version: str
    proposal: str
    available_evidence: Tuple[str, ...]
    gate_decision: str  # ALLOW / DEFER / REFUSE
    constraints: Tuple[str, ...]
    action: str
    decision_timestamp: str
    provenance: str
    source: str = "sovereign_veritas"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True)
class OutcomeRecord:
    """Observed outcome after the action. Append-only; never rewritten."""
    outcome_id: str
    decision_id: str
    observed_outcome: str
    outcome_timestamp: str
    success: Optional[bool]
    metrics: Tuple[Tuple[str, float], ...] = ()
    provenance: str = ""
    source: str = "sovereign_veritas"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["metrics"] = dict(self.metrics)
        return d

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True)
class LearningCase:
    """
    Joined view of decision + outcome for evaluation.
    Constructed by reference; does not own or mutate the originals.
    """
    case_id: str
    decision: DecisionRecord
    outcome: OutcomeRecord
    provenance: str = ""

    @property
    def decision_id(self) -> str:
        return self.decision.decision_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "decision": self.decision.to_dict(),
            "outcome": self.outcome.to_dict(),
            "provenance": self.provenance,
        }


@dataclass(frozen=True)
class Hypothesis:
    """
    Must be registered BEFORE evaluation. Explicit claim that can be
    supported, refuted, or left with insufficient evidence.
    """
    hypothesis_id: str
    statement: str
    candidate_version: str
    baseline_version: str
    prediction: str
    registered_at: str
    dataset_id: str
    dataset_version: str
    evaluation_protocol: str
    anti_vacuity: str
    provenance: str = ""
    validity_axes: Tuple[str, ...] = ("mathematical", "implementation", "empirical")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True)
class EvaluationResult:
    """
    Result of evaluating a registered hypothesis against historical
    and/or held-out cases. Does not authorize deployment.
    """
    evaluation_id: str
    hypothesis_id: str
    learning_case_ids: Tuple[str, ...]
    dataset_id: str
    dataset_version: str
    evaluation_protocol: str
    candidate_version: str
    baseline_version: str
    result: OutcomeStatus
    metrics: Tuple[Tuple[str, float], ...]
    failures: Tuple[str, ...]
    refutations: Tuple[str, ...]
    reproducibility: str
    code_revision: str
    evaluated_at: str
    provenance: str
    promotion_status: PromotionStatus = PromotionStatus.NOT_PROPOSED

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["result"] = self.result.value
        d["promotion_status"] = self.promotion_status.value
        d["metrics"] = dict(self.metrics)
        return d

    def fingerprint(self) -> str:
        return content_hash(self.to_dict())


@dataclass(frozen=True)
class PromotionRecord:
    """
    A proposal/result for admission into a candidate pool.
    Explicitly NOT an instruction to deploy or rewrite the agent.
    """
    promotion_id: str
    evaluation_id: str
    hypothesis_id: str
    candidate_version: str
    status: PromotionStatus
    rationale: str
    recorded_at: str
    provenance: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d
