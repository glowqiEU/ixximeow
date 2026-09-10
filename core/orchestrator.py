from .action import Action
from .action_registry import ActionRegistry
from .action_store import find_action_by_id
from .approval_store import load_approvals, save_approvals
from .decision_store import load_decisions
from .execution_service import reserve_execution
from .history import HistoryEvent
from .history_store import append_event
from .orchestrator_v2 import OrchestratorV2
from .state_manager import apply_cancellation
from .state_store import load_state, save_state
from .task_lifecycle import transition_task
from .task_store import load_tasks, save_tasks


class Orchestrator(OrchestratorV2):
    """Public orchestrator entry point for the explicit lifecycle."""

    def __init__(self, registry: ActionRegistry) -> None:
        super().__init__(registry)

    def resume_approval(self, approval_id: str):
        approvals = load_approvals()
        approval = next((item for item in approvals if item.id == approval_id), None)
        if approval is None:
            raise ValueError("approval not found")
        if approval.status not in {"approved", "rejected"}:
            raise ValueError(f"approval is not ready to resume: {approval.status}")

        tasks = load_tasks()
        task = next((item for item in tasks if item.id == approval.task_id), None)
        if task is None:
            raise ValueError("task for approval not found")
        if task.approval_id != approval.id:
            raise ValueError("approval does not belong to task")
        if task.action_id != approval.action_id:
            raise ValueError("approval does not belong to action")
        if approval.required_level != task.required_level:
            raise ValueError("approval permission level does not match task")
        if task.status != "waiting_approval":
            raise ValueError(f"task is not waiting for approval: {task.status}")

        if approval.status == "rejected":
            task = transition_task(task, "cancelled")
            index = next(index for index, item in enumerate(tasks) if item.id == task.id)
            tasks[index] = task
            save_tasks(tasks)
            save_approvals(approvals)
            state = apply_cancellation(load_state(), task=task)
            save_state(state)
            append_event(
                HistoryEvent(
                    event_type="task_cancelled",
                    summary="task cancelled after approval rejection",
                    decision_id=task.decision_id,
                    task_id=task.id,
                )
            )
            return task, None

        decision = next((item for item in load_decisions() if item.id == task.decision_id), None)
        if decision is None:
            raise ValueError("decision for approved task not found")
        if task.action_id is None:
            raise ValueError("approved task has no action_id")

        action = find_action_by_id(task.action_id)
        if action is None:
            raise ValueError("approved action definition not found")
        if action.task_id != task.id:
            raise ValueError("approved action does not belong to task")
        if action.id != approval.action_id:
            raise ValueError("approved action does not match approval")
        if action.permission_level != approval.required_level:
            raise ValueError("approved action permission level does not match approval")

        execution = reserve_execution(action)
        task = transition_task(task, "running")
        index = next(index for index, item in enumerate(tasks) if item.id == task.id)
        tasks[index] = task
        save_tasks(tasks)
        save_approvals(approvals)
        return self._finalize(task, decision, action, execution, load_state(), tasks)
