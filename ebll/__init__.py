"""
Evidence-Bound Learning Loop (EBLL)

Architectural bridge: Sovereign Veritas records what happened;
Principia Artificialis evaluates whether a proposed change has earned
evidence of improvement. The evaluation layer never rewrites history.

This package demonstrates the data/evaluation loop only.
It does not train, deploy, or autonomously modify an agent.

Status: Draft, verified reference code (the reference experiment prints
the claimed numbers). The overall learning loop is NOT validated.
"""

from .records import (
    DecisionRecord,
    OutcomeRecord,
    LearningCase,
    Hypothesis,
    EvaluationResult,
    PromotionRecord,
    OutcomeStatus,
    PromotionStatus,
)
from .store import AppendOnlyStore
from .evaluator import Evaluator
from .experiment import run_reference_experiment

__all__ = [
    "DecisionRecord",
    "OutcomeRecord",
    "LearningCase",
    "Hypothesis",
    "EvaluationResult",
    "PromotionRecord",
    "OutcomeStatus",
    "PromotionStatus",
    "AppendOnlyStore",
    "Evaluator",
    "run_reference_experiment",
]

__version__ = "0.1.0"
