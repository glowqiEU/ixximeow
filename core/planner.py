from .context import AgentContext
from .models import Decision


def generate_candidates(context: AgentContext) -> list[Decision]:
    candidates = []

    if context.task:
        candidates.append(
            Decision(
                objective=context.goal_id or "continue current goal",
                action=f"continue: {context.task}",
                reason="an active task already exists",
                priority=10,
            )
        )

    if context.goal_id:
        candidates.append(
            Decision(
                objective=context.goal_id,
                action="review next useful action",
                reason="an active goal exists without requiring a specific task",
                priority=5,
            )
        )

    if not candidates:
        candidates.append(
            Decision(
                objective="understand current situation",
                action="inspect current state",
                reason="no active goal or task is available",
                priority=1,
            )
        )

    return candidates
