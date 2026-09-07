import unittest

from core.approval_gate import check_approval
from core.models import Task


class TestApprovalGate(unittest.TestCase):
    def test_publish_task_requires_approval(self):
        task = Task(
            title="publish post",
            required_level="publish",
        )

        approval = check_approval(task)

        self.assertIsNotNone(approval)
        self.assertEqual(approval.task_id, task.id)
        self.assertEqual(approval.required_level, "publish")
        self.assertEqual(approval.status, "pending")

    def test_prepare_task_does_not_require_approval(self):
        task = Task(
            title="prepare content",
            required_level="prepare",
        )

        approval = check_approval(task)

        self.assertIsNone(approval)


if __name__ == "__main__":
    unittest.main()
