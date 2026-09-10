from typing import Optional
from uuid import uuid4

from .action import Action
from .action_registry import (
    ActionContractError,
    ActionDispatchError,
    ActionRegistry,
)
from .action_response import ActionResponse
from .approval import Approval
from .agent_config import CURRENT_AUTONOMY_LEVEL
from .models import Task, Result
from .permissions import AutonomyLevel, can_execute
from .task_lifecycle import transition_task
from .action_store import load_actions, save_actions
from .result_store import load_results, save_results
from .verification import verify_execution_result


TASK_ACTION_NAME = "execute_task"


def _default_task_handler(action: Action) -> ActionResponse:
    """Temporary deterministic handler for the MVP task execution boundary."""
    return ActionResponse(
        success=True,
        summary="task execution completed",
        output={"task_id": action.task_id, "title": action.input["title"]},
    )


def _default_registry() -> ActionRegistry:
    registry = ActionRegistry()
    registry.register(TASK_ACTION_NAME, _default_task_handler)
    return registry


def _ensure_execution_permission(task: Task, approval: Optional[Approval]) -> None:
    required_level = AutonomyLevel[task.required_level.upper()]

    if can_execute(CURRENT_AUTONOMY_LEVEL, required_level):
        return

    if approval is None:
        raise PermissionError(
            f"task requires {task.required_level} autonomy level"
        )

    if approval.status != "approved":
        raise PermissionError(
            f"task requires approved {task.required_level} autonomy level"
        )


def execute_task(
    task: Task,
    approval: Optional[Approval] = None,
    registry: Optional[ActionRegistry] = None,
) -> tuple[Task, Optional[Result]]:
    if approval is not None:
        if task.approval_id != approval.id:
            raise ValueError("approval does not belong to task")

        if approval.status == "pending":
            task = transition_task(task, "waiting_approval")
            return task, None

        if approval.status == "rejected":
            task = transition_task(task, "cancelled")
            return task, None

        if approval.status != "approved":
            raise ValueError(f"invalid approval status: {approval.status}")

    _ensure_execution_permission(task, approval)

    task = transition_task(task, "running")
    action = Action(
        task_id=task.id,
        name=TASK_ACTION_NAME,
        input={"title": task.title},
        permission_level=task.required_level,
    )
    execution_id = str(uuid4())

    actions = load_actions()
    actions.append(action)
    save_actions(actions)

    active_registry = registry or _default_registry()
    try:
        response = active_registry.execute(action)
    except ActionDispatchError as exc:
        result = Result(
            task_id=task.id,
            action_id=action.id,
            execution_id=execution_id,
            success=False,
            summary=f"task dispatch failed: {exc}",
            failure_kind="dispatch_error",
        )
    except ActionContractError as exc:
        result = Result(
            task_id=task.id,
            action_id=action.id,
            execution_id=execution_id,
            success=False,
            summary=f"action contract failed: {exc}",
            failure_kind="contract_error",
        )
    except Exception as exc:
        result = Result(
            task_id=task.id,
            action_id=action.id,
            execution_id=execution_id,
            success=False,
            summary=f"task execution failed: {exc}",
            failure_kind="execution_error",
        )
    else:
        result = Result(
            task_id=task.id,
            action_id=action.id,
            execution_id=execution_id,
            success=response.success,
            summary=response.summary,
            failure_kind="action_failed" if not response.success else None,
        )

    verify_execution_result(task, result)
    task = transition_task(
        task,
        "completed" if result.success else "failed",
    )

    results = load_results()
    results.append(result)
    save_results(results)

    return task, result
