from .models import Task, Result


def execute_task(task: Task) -> Result:
    return Result(
        task_id=task.id,
        success=False,
        summary="execution not implemented yet",
    )
