import unittest
from unittest.mock import patch

from core.approval import Approval
from core.executor import execute_task
from core.models import Task
from core.permissions import AutonomyLevel


class TestExecutorApproval(unittest.TestCase):
    def test_pending_approval_blocks_execution(self):
        task = Task(
            title="publish content",
            required_level="publish",
        )
        approval = Approval(
            task_id=task.id,
            required_level="publish",
            reason="publishing requires permission",
        )
        task.approval_id = approval.id

        task, result = execute_task(task, approval=approval)

        self.assertEqual(task.status, "waiting_approval")
        self.assertIsNone(result)

    def test_approved_task_can_execute(self):
        task = Task(
            title="publish content",
            required_level="publish",
        )
        approval = Approval(
            task_id=task.id,
            required_level="publish",
            reason="publishing requires permission",
            status="approved",
        )
        task.approval_id = approval.id

        with patch("core.executor.load_approvals", return_value=[approval]), \
             patch.object(
                 __import__("core.agent_config", fromlist=["CURRENT_AUTONOMY_LEVEL"]),
                 "CURRENT_AUTONOMY_LEVEL",
                 AutonomyLevel.EXECUTE,
             ):
            task, result = execute_task(task, approval=approval)

        self.assertEqual(task.status, "completed")
        self.assertIsNotNone(result)
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
