import unittest

from core.approval_service import create_approval_if_needed
from core.permissions import AutonomyLevel


class TestApprovalService(unittest.TestCase):
    def test_creates_approval_when_level_is_insufficient(self):
        approval = create_approval_if_needed(
            task_id="task-123",
            current_level=AutonomyLevel.PREPARE,
            required_level=AutonomyLevel.PUBLISH,
            reason="publishing requires permission",
        )

        self.assertIsNotNone(approval)
        self.assertEqual(approval.task_id, "task-123")
        self.assertEqual(approval.required_level, "publish")
        self.assertEqual(approval.status, "pending")

    def test_no_approval_when_level_is_sufficient(self):
        approval = create_approval_if_needed(
            task_id="task-123",
            current_level=AutonomyLevel.PUBLISH,
            required_level=AutonomyLevel.PUBLISH,
            reason="publishing requires permission",
        )

        self.assertIsNone(approval)


if __name__ == "__main__":
    unittest.main()
