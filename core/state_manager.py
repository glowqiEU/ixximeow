from datetime import datetime, timezone

from .models import Decision, Result, Task
from .state import SystemState


def _touch(state: SystemState) -> SystemState:
    state.updated_at = datetime.now(timezone.utc).isoformat()
    return state


def apply_decision(
    state: SystemState,
    decision: Decision,
    task: Task,
) -> SystemState:
    state.active_task = task.id
    state.last_decision_id = decision.id
    state.last_result_id = None
    return _touch(state)


def apply_result(
    state: SystemState,
    task: Task,
    result: Result,
) -> SystemState:
    if result.task_id != task.id:
        raise ValueError("result does not belong to task")

    state.active_task = None
    state.last_result_id = result.id
    return _touch(state)


def apply_uncertain_execution(
    state: SystemState,
    task: Task,
) -> SystemState:
    """Clear active work when execution needs reconciliation before a result exists."""
    if state.active_task != task.id:
        raise ValueError("uncertain execution does not belong to active task")

    state.active_task = None
    state.last_result_id = None
    return _touch(state)


def apply_cancellation(
    state: SystemState,
    task: Task,
) -> SystemState:
    state.active_task = None
    return _touch(state)
