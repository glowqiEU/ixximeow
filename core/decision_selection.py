from typing import Iterable

from .decision_evaluation import DecisionEvaluation
from .models import Decision


def calculate_selection_score(evaluation: DecisionEvaluation) -> float:
    """Calculate the initial normalized utility for a decision evaluation.

    Higher relevance and confidence improve the score.
    Higher risk and effort reduce the score.
    The four signals are weighted equally for the initial deterministic policy.
    """
    return (
        evaluation.relevance
        + evaluation.confidence
        + (1.0 - evaluation.risk)
        + (1.0 - evaluation.effort)
    ) / 4.0


def select_decision(
    decisions: Iterable[Decision],
    evaluations: Iterable[DecisionEvaluation],
) -> Decision:
    """Select the highest-scoring decision from evaluated candidates."""
    candidates = list(decisions)
    if not candidates:
        raise ValueError("no decision options provided")

    evaluation_by_id = {evaluation.decision_id: evaluation for evaluation in evaluations}

    missing = [
        decision.id
        for decision in candidates
        if decision.id not in evaluation_by_id
    ]
    if missing:
        raise ValueError("missing evaluation for decision: " + missing[0])

    return max(
        candidates,
        key=lambda decision: calculate_selection_score(
            evaluation_by_id[decision.id]
        ),
    )
