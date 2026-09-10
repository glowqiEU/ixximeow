from typing import Optional
from uuid import uuid4

from .action import Action
from .approval import Approval
from .models import Task, Result
from .task_lifecycle import transition_task
from .action_store import load_actions, save_actions
from .result_store import load_results, save_results
from .verification import verify_execution_result


def execute_task(
    task: Task,
    approval: Optional[Approval] = None,
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

    task = transition_task(task, "running")
    action = Action(task_id=task.id, name=task.title)
    execution_id = str(uuid4())

    actions = load_actions()
    actions.append(action)
    save_actions(actions)

    try:
        result = Result(
            task_id=task.id,
            action_id=action.id,
            execution_id=execution_id,
            success=True,
            summary="task execution completed",
        )
        verify_execution_result(task, result)
        task = transition_task(task, "completed")

    except Exception as exc:
        result = Result(
            task_id=task.id,
            action_id=action.id,
            execution_id=execution_id,
            success=False,
            summary=f"task execution failed: {exc}",
        )
        verify_execution_result(task, result)
        task = transition_task(task, "failed")

    results = load_results()
    results.append(result)
    save_results(results)

    return task, result
