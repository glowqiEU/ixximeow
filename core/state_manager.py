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
    state.active_task = task.id or task.title
    state.last_decision_id = decision.id
    state.last_result_id = None
    return _touch(state)


def apply_result(
    state: SystemState,
    task: Task,
    result: Result,
) -> SystemState:
    state.active_task = None
    state.last_result_id = result.id
    return _touch(state)


def apply_cancellation(
    state: SystemState,
    task: Task,
) -> SystemState:
    state.active_task = None
    return _touch(state)
