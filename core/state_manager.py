from datetime import datetime, timezone

from .models import Decision, Result, Task
from .state import SystemState


def _touch(state: SystemState) -> SystemState:
    state.updated_at = datetime.now(timezone.utc).isoformat()
    return state


def apply_decision(state, decision, task):
    state.active_task = task.id or task.title
    state.last_decision_id = decision.id
    state.last_result_id = None
    return _touch(state)


def apply_result(state, task, result):
    state.active_task = None
    state.last_result_id = result.id
    return _touch(state)


def apply_cancellation(state, task):
    state.active_task = None
    return _touch(state)
