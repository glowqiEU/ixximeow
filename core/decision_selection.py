from .decision_evaluation import DecisionEvaluation


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
