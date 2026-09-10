from pathlib import Path
from typing import Optional

from .execution import EXECUTION_STATUSES, Execution
from .file_lock import exclusive_file_lock
from .persistence import load_json, save_json


EXECUTIONS_FILE = Path("executions.json")


def save_executions(executions: list[Execution]) -> None:
    save_json(EXECUTIONS_FILE, [execution.__dict__ for execution in executions])


def load_executions() -> list[Execution]:
    data = load_json(EXECUTIONS_FILE, [])
    return [Execution(**item) for item in data]


def find_execution_by_id(execution_id: str) -> Optional[Execution]:
    return next(
        (execution for execution in load_executions() if execution.id == execution_id),
        None,
    )


def find_execution_by_idempotency_key(key: str) -> Optional[Execution]:
    return next(
        (
            execution
            for execution in load_executions()
            if execution.idempotency_key == key
        ),
        None,
    )


def find_executions_by_status(status: str) -> list[Execution]:
    if status not in EXECUTION_STATUSES:
        raise ValueError(f"invalid execution status: {status}")

    return [
        execution
        for execution in load_executions()
        if execution.status == status
    ]


def reserve_execution_slot(execution: Execution) -> Execution:
    """Atomically reserve an execution idempotency key."""
    with exclusive_file_lock(EXECUTIONS_FILE):
        executions = load_executions()
        conflicting_execution = next(
            (
                existing
                for existing in executions
                if existing.idempotency_key == execution.idempotency_key
            ),
            None,
        )
        if conflicting_execution is not None:
            if conflicting_execution.id != execution.id:
                raise ValueError(
                    "execution idempotency_key already belongs to another execution"
                )
            return conflicting_execution

        executions.append(execution)
        save_executions(executions)
        return execution


def claim_execution_running(execution_id: str) -> Execution:
    """Atomically claim a pending execution before invoking its handler."""
    with exclusive_file_lock(EXECUTIONS_FILE):
        executions = load_executions()
        execution = next(
            (item for item in executions if item.id == execution_id),
            None,
        )
        if execution is None:
            raise ValueError("execution not found")
        if execution.status != "pending":
            raise ValueError(f"execution is not pending: {execution.status}")

        execution.transition("running")
        for index, item in enumerate(executions):
            if item.id == execution.id:
                executions[index] = execution
                break
        save_executions(executions)
        return execution


def upsert_execution(execution: Execution) -> None:
    # The idempotency check and insert/update must be one critical section.
    # Otherwise two workers can both observe the key as unused and both reserve it.
    with exclusive_file_lock(EXECUTIONS_FILE):
        executions = load_executions()
        conflicting_execution = next(
            (
                existing
                for existing in executions
                if existing.idempotency_key == execution.idempotency_key
            ),
            None,
        )

        if (
            conflicting_execution is not None
            and conflicting_execution.id != execution.id
        ):
            raise ValueError(
                "execution idempotency_key already belongs to another execution"
            )

        for index, existing in enumerate(executions):
            if existing.id == execution.id:
                executions[index] = execution
                save_executions(executions)
                return

        executions.append(execution)
        save_executions(executions)
