from .models import Result, Task


def verify_execution_result(task: Task, result: Result) -> None:
    """Validate the structural integrity of an execution result."""
    if result.task_id != task.id:
        raise ValueError("result does not belong to task")

    if not isinstance(result.success, bool):
        raise ValueError("result success must be a boolean")

    if not result.summary.strip():
        raise ValueError("result summary must not be empty")
