import unittest

from core.approval import Approval
from core.executor import execute_task
from core.models import Task


class TestExecutorApproval(unittest.TestCase):
    def test_pending_approval_blocks_execution(self):
        approval = Approval(
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )

        task = Task(
            title="publish content",
            approval_id=approval.id,
        )

        task, result = execute_task(task, approval=approval)

        self.assertEqual(task.status, "waiting_approval")
        self.assertIsNone(result)

    def test_approved_task_can_execute(self):
        approval = Approval(
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
            status="approved",
        )

        task = Task(
            title="publish content",
            approval_id=approval.id,
        )

        task, result = execute_task(task, approval=approval)

        self.assertEqual(task.status, "completed")
        self.assertIsNotNone(result)
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
