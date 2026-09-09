from .models import Result, Task
from .action import Action
from .execution import Execution
from .evidence import Evidence


def verify_execution_result(
    task: Task,
    action: Action,
    execution: Execution,
    result: Result,
) -> None:
    """Validate that a technical result belongs to one execution lineage."""
    if action.task_id != task.id:
        raise ValueError("action does not belong to task")

    if execution.task_id != task.id:
        raise ValueError("execution does not belong to task")

    if execution.action_id != action.id:
        raise ValueError("execution does not belong to action")

    if result.task_id != task.id:
        raise ValueError("result does not belong to task")

    if result.action_id != action.id:
        raise ValueError("result does not belong to action")

    if result.execution_id != execution.id:
        raise ValueError("result does not belong to execution")

    if not isinstance(result.success, bool):
        raise ValueError("result success must be a boolean")

    if not result.summary.strip():
        raise ValueError("result summary must not be empty")


def verify_evidence(
    result: Result,
    execution: Execution,
    evidence: Evidence,
) -> None:
    """Validate that evidence is attached to the result that produced it."""
    if evidence.result_id != result.id:
        raise ValueError("evidence does not belong to result")

    if evidence.execution_id != execution.id:
        raise ValueError("evidence does not belong to execution")
