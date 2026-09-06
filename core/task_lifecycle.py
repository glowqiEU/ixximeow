from .models import Task


ALLOWED_TRANSITIONS = {
    "pending": {"running"},
    "running": {"completed", "failed"},
    "completed": set(),
    "failed": set(),
}


def transition_task(task: Task, new_status: str) -> Task:
    allowed = ALLOWED_TRANSITIONS.get(task.status, set())

    if new_status not in allowed:
        raise ValueError(
            f"invalid task transition: {task.status} -> {new_status}"
        )

    task.status = new_status
    return task
