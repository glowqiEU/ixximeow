import json
from pathlib import Path
from uuid import uuid4

from .models import Task


TASKS_FILE = Path("tasks.json")


def save_tasks(tasks: list[Task]) -> None:
    TASKS_FILE.write_text(
        json.dumps([task.__dict__ for task in tasks], indent=2),
        encoding="utf-8",
    )


def load_tasks() -> list[Task]:
    if not TASKS_FILE.exists():
        return []

    data = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    return [Task(**item) for item in data]


def ensure_task_id(task: Task) -> Task:
    if task.id is None:
        task.id = str(uuid4())

    return task
