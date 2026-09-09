from pathlib import Path

from .execution import Execution
from .persistence import load_json, save_json


EXECUTIONS_FILE = Path("executions.json")


def save_executions(executions: list[Execution]) -> None:
    save_json(EXECUTIONS_FILE, [execution.__dict__ for execution in executions])


def load_executions() -> list[Execution]:
    data = load_json(EXECUTIONS_FILE, [])
    return [Execution(**item) for item in data]


def find_execution_by_id(execution_id: str) -> Execution | None:
    return next(
        (execution for execution in load_executions() if execution.id == execution_id),
        None,
    )


def find_execution_by_idempotency_key(key: str) -> Execution | None:
    return next(
        (
            execution
            for execution in load_executions()
            if execution.idempotency_key == key
        ),
        None,
    )


def upsert_execution(execution: Execution) -> None:
    executions = load_executions()

    for index, existing in enumerate(executions):
        if existing.id == execution.id:
            executions[index] = execution
            save_executions(executions)
            return

    executions.append(execution)
    save_executions(executions)
