from .action import Action
from .execution import Execution
from .models import Result, Task


def verify_execution_result(
    task: Task,
    action: Action,
    execution: Execution,
    result: Result,
) -> None:
    """Validate that a result belongs to the exact action execution lineage."""
    if result.task_id != task.id:
        raise ValueError("result does not belong to task")

    if result.action_id != action.id or action.task_id != task.id:
        raise ValueError("result does not belong to action")

    if result.execution_id != execution.id:
        raise ValueError("result does not belong to execution")

    if execution.action_id != action.id or execution.task_id != task.id:
        raise ValueError("execution does not belong to action")

    if not isinstance(result.success, bool):
        raise ValueError("result success must be a boolean")

    if not result.summary.strip():
        raise ValueError("result summary must not be empty")

    if result.success and execution.status != "succeeded":
        raise ValueError("successful result requires succeeded execution")
