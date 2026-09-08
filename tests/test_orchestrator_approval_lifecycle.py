import unittest
from unittest.mock import patch

from core.approval import Approval
from core.models import Decision, Result, Task
from core.orchestrator import Orchestrator
from core.state import SystemState


class TestOrchestratorApprovalLifecycle(unittest.TestCase):
    def test_approval_resume_executes_approved_task(self):
        decision = Decision("goal-1", "publish", "requires approval", goal_id="goal-1")
        task = Task(
            "publish",
            decision_id=decision.id,
            goal_id=decision.goal_id,
            id="task-1",
        )
        approval = Approval(
            task_id=task.id,
            required_level="publish",
            reason="approval required",
            id="approval-1",
        )

        with patch("core.orchestrator.build_context"), \
             patch("core.orchestrator.generate_candidates", return_value=[decision]), \
             patch("core.orchestrator.evaluate_decision"), \
             patch("core.orchestrator.select_decision", return_value=decision), \
             patch("core.orchestrator.save_decision_evaluations"), \
             patch("core.orchestrator.load_decisions", return_value=[]), \
             patch("core.orchestrator.save_decisions"), \
             patch("core.orchestrator.load_tasks", return_value=[]), \
             patch("core.orchestrator.save_tasks"), \
             patch("core.orchestrator.ensure_task_id", return_value=task), \
             patch("core.orchestrator.load_state", return_value=SystemState()), \
             patch("core.orchestrator.save_state"), \
             patch("core.orchestrator.check_approval", return_value=approval), \
             patch("core.orchestrator.load_approvals", return_value=[]), \
             patch("core.orchestrator.save_approvals"), \
             patch("core.orchestrator.append_event"), \
             patch("core.orchestrator.execute_task") as execute_task:
            first = Orchestrator().run()
            execute_task.assert_not_called()

        self.assertEqual(first[1].status, "waiting_approval")
        self.assertIsNone(first[2])
        self.assertEqual(first[1].approval_id, approval.id)

        approval.status = "approved"
        approved_result = Result(task.id, True, "executed")

        with patch("core.orchestrator.load_approvals", return_value=[approval]), \
             patch("core.orchestrator.load_tasks", return_value=[first[1]]), \
             patch("core.orchestrator.save_tasks"), \
             patch("core.orchestrator.save_approvals"), \
             patch("core.orchestrator.execute_task", return_value=(
                 Task(
                     "publish",
                     status="completed",
                     decision_id=decision.id,
                     goal_id=decision.goal_id,
                     approval_id=approval.id,
                     id=task.id,
                 ),
                 approved_result,
             )) as resume_execute, \
             patch("core.orchestrator.load_state", return_value=SystemState(
                 active_task=task.id,
                 active_goal_id=decision.goal_id,
             )), \
             patch("core.orchestrator.save_state"), \
             patch("core.orchestrator.append_event"):
            resumed_task, result = Orchestrator().resume_approval(approval.id)

        self.assertEqual(resumed_task.status, "completed")
        self.assertEqual(result.task_id, resumed_task.id)
        self.assertTrue(result.success)
        resume_execute.assert_called_once_with(first[1], approval=approval)

    def test_rejected_approval_cancels_task_without_execution(self):
        approval = Approval(
            task_id="task-1",
            required_level="publish",
            reason="approval required",
            status="rejected",
            id="approval-1",
        )
        task = Task(
            "publish",
            status="waiting_approval",
            approval_id=approval.id,
            id=approval.task_id,
        )
        cancelled_task = Task(
            "publish",
            status="cancelled",
            approval_id=approval.id,
            id=approval.task_id,
        )

        with patch("core.orchestrator.load_approvals", return_value=[approval]), \
             patch("core.orchestrator.load_tasks", return_value=[task]), \
             patch("core.orchestrator.save_tasks"), \
             patch("core.orchestrator.save_approvals"), \
             patch("core.orchestrator.execute_task", return_value=(cancelled_task, None)) as execute_task, \
             patch("core.orchestrator.load_state", return_value=SystemState(active_task=task.id)), \
             patch("core.orchestrator.save_state"), \
             patch("core.orchestrator.append_event"):
            resumed_task, result = Orchestrator().resume_approval(approval.id)

        self.assertEqual(resumed_task.status, "cancelled")
        self.assertIsNone(result)
        execute_task.assert_called_once_with(task, approval=approval)


if __name__ == "__main__":
    unittest.main()
