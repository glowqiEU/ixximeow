from .context import AgentContext
from .models import Decision


def _task_title(task) -> str:
    return task.title if hasattr(task, "title") else task


def generate_candidates(context: AgentContext) -> list[Decision]:
    candidates = []

    if context.task:
        reason = "an active task already exists"

        if context.goal is not None:
            reason += f"; goal: {context.goal.description}"

        if context.memories:
            memory_summary = "; ".join(
                memory.content for memory in context.memories
            )
            reason += f"; relevant memory: {memory_summary}"

        candidates.append(
            Decision(
                objective=context.goal_id or "continue current goal",
                action=f"continue: {_task_title(context.task)}",
                reason=reason,
                priority=10,
                goal_id=context.goal_id,
            )
        )

    if context.goal_id:
        reason = "an active goal exists without requiring a specific task"
        if context.goal is not None:
            reason += f"; goal: {context.goal.description}"

        candidates.append(
            Decision(
                objective=context.goal_id,
                action="review next useful action",
                reason=reason,
                priority=5,
                goal_id=context.goal_id,
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
