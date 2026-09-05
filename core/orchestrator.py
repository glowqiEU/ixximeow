from .decision_engine import choose_decision
from .models import Decision, Result, Task


class Orchestrator:
    def run(self, options: list[Decision]) -> tuple[Decision, Task, Result]:
        decision = choose_decision(options)

        task = Task(
            title=decision.action,
            decision_id=decision.id,
        )

        result = Result(
            task_id=task.id or task.title,
            success=False,
            summary="task created; execution not yet performed",
        )

        return decision, task, result
