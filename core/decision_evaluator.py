from .context import AgentContext
from .decision_evaluation import DecisionEvaluation
from .models import Decision


def evaluate_decision(
    decision: Decision,
    context: AgentContext,
) -> DecisionEvaluation:
    return DecisionEvaluation(
        decision_id=decision.id,
        relevance=1.0 if context.goal_id == decision.objective else 0.5,
        confidence=0.5,
        risk=0.5,
        effort=0.5,
        score=float(decision.priority),
        reason="initial deterministic evaluation",
    )
