from pathlib import Path
from uuid import uuid4

from .file_lock import exclusive_file_lock
from .models import Task
from .persistence import load_json, save_json


TASKS_FILE = Path("tasks.json")


def save_tasks(tasks: list[Task]) -> None:
    save_json(TASKS_FILE, [task.__dict__ for task in tasks])


def load_tasks() -> list[Task]:
    data = load_json(TASKS_FILE, [])
    return [Task(**item) for item in data]


def claim_task_running(task_id: str, approval_id: str) -> Task:
    """Atomically consume an approval-waiting task for execution."""
    from .task_lifecycle import transition_task

    with exclusive_file_lock(TASKS_FILE):
        tasks = load_tasks()
        task = next((item for item in tasks if item.id == task_id), None)
        if task is None:
            raise ValueError("task not found")
        if task.approval_id != approval_id:
            raise ValueError("approval does not belong to task")
        if task.status != "waiting_approval":
            raise ValueError(f"task is not waiting for approval: {task.status}")

        task = transition_task(task, "running")
        for index, item in enumerate(tasks):
            if item.id == task.id:
                tasks[index] = task
                break
        save_tasks(tasks)
        return task


def ensure_task_id(task: Task) -> Task:
    if task.id is None:
        task.id = str(uuid4())

    return task
