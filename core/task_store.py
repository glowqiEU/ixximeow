from pathlib import Path
from uuid import uuid4

from .models import Task
from .persistence import load_json, save_json


TASKS_FILE = Path("tasks.json")


def save_tasks(tasks: list[Task]) -> None:
    save_json(TASKS_FILE, [task.__dict__ for task in tasks])


def load_tasks() -> list[Task]:
    data = load_json(TASKS_FILE, [])
    return [Task(**item) for item in data]


def ensure_task_id(task: Task) -> Task:
    if task.id is None:
        task.id = str(uuid4())

    return task
