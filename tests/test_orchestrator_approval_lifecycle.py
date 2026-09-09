import unittest
from unittest.mock import patch

from core.action_registry import ActionRegistry
from core.approval import Approval
from core.models import Decision, Result, Task
from core.orchestrator import Orchestrator
from core.state import SystemState


class TestOrchestratorApprovalLifecycle(unittest.TestCase):
    def _registry(self):
        return ActionRegistry()

    def test_approved_task_resumes_through_finalize(self):
        decision = Decision("goal-1", "publish", "requires approval", goal_id="goal-1")
        task = Task(
            "publish",
            status="waiting_approval",
            required_level="publish",
            decision_id=decision.id,
            goal_id=decision.goal_id,
            action_id="action-1",
            approval_id="approval-1",
            id="task-1",
        )
        approval = Approval(
            action_id=task.action_id,
            task_id=task.id,
            required_level="publish",
            reason="approval required",
            status="approved",
            id="approval-1",
        )
        completed_task = Task(
            "publish",
            status="completed",
            decision_id=decision.id,
            goal_id=decision.goal_id,
            action_id=task.action_id,
            approval_id=approval.id,
            id=task.id,
        )
        result = Result(
            task_id=task.id,
            action_id=task.action_id,
            execution_id="execution-1",
            success=True,
            summary="executed",
        )

        with patch("core.orchestrator.load_approvals", return_value=[approval]), \
             patch("core.orchestrator.load_tasks", return_value=[task]), \
             patch("core.orchestrator.load_decisions", return_value=[decision]), \
             patch("core.orchestrator.save_tasks"), \
             patch("core.orchestrator.save_approvals"), \
             patch("core.orchestrator.load_state", return_value=SystemState()), \
             patch.object(
                 Orchestrator,
                 "_finalize",
                 return_value=(completed_task, result),
             ) as finalize:
            resumed_task, resumed_result = Orchestrator(self._registry()).resume_approval(
                approval.id
            )

        self.assertEqual(resumed_task.status, "completed")
        self.assertEqual(resumed_result.task_id, task.id)
        finalize.assert_called_once()
        action = finalize.call_args.args[2]
        self.assertEqual(action.id, task.action_id)
        self.assertEqual(action.task_id, task.id)

    def test_rejected_approval_cancels_without_execution(self):
        approval = Approval(
            action_id="action-1",
            task_id="task-1",
            required_level="publish",
            reason="approval required",
            status="rejected",
            id="approval-1",
        )
        task = Task(
            "publish",
            status="waiting_approval",
            required_level="publish",
            action_id=approval.action_id,
            approval_id=approval.id,
            id=approval.task_id,
        )

        with patch("core.orchestrator.load_approvals", return_value=[approval]), \
             patch("core.orchestrator.load_tasks", return_value=[task]), \
             patch("core.orchestrator.save_tasks"), \
             patch("core.orchestrator.save_approvals"), \
             patch("core.orchestrator.load_state", return_value=SystemState(active_task=task.id)), \
             patch("core.orchestrator.save_state"), \
             patch("core.orchestrator.append_event"), \
             patch.object(Orchestrator, "_finalize") as finalize:
            resumed_task, result = Orchestrator(self._registry()).resume_approval(
                approval.id
            )

        self.assertEqual(resumed_task.status, "cancelled")
        self.assertIsNone(result)
        finalize.assert_not_called()

    def test_resume_rejects_approval_bound_to_different_action(self):
        approval = Approval(
            action_id="action-2",
            task_id="task-1",
            required_level="publish",
            reason="approval required",
            status="approved",
            id="approval-1",
        )
        task = Task(
            "publish",
            status="waiting_approval",
            action_id="action-1",
            approval_id=approval.id,
            id=approval.task_id,
        )

        with patch("core.orchestrator.load_approvals", return_value=[approval]), \
             patch("core.orchestrator.load_tasks", return_value=[task]):
            with self.assertRaisesRegex(ValueError, "approval does not belong to action"):
                Orchestrator(self._registry()).resume_approval(approval.id)

    def test_resume_rejects_approval_with_mismatched_permission_level(self):
        approval = Approval(
            action_id="action-1",
            task_id="task-1",
            required_level="publish",
            reason="approval required",
            status="approved",
            id="approval-1",
        )
        task = Task(
            "publish",
            status="waiting_approval",
            required_level="execute",
            action_id=approval.action_id,
            approval_id=approval.id,
            id=approval.task_id,
        )

        with patch("core.orchestrator.load_approvals", return_value=[approval]), \
             patch("core.orchestrator.load_tasks", return_value=[task]), \
             patch.object(Orchestrator, "_finalize") as finalize:
            with self.assertRaisesRegex(
                ValueError, "approval permission level does not match task"
            ):
                Orchestrator(self._registry()).resume_approval(approval.id)

        finalize.assert_not_called()


if __name__ == "__main__":
    unittest.main()
