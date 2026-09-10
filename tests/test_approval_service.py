import unittest

from core.action import Action
from core.approval_service import create_approval_if_needed
from core.permissions import AutonomyLevel


class TestApprovalService(unittest.TestCase):
    def test_creates_approval_when_level_is_insufficient(self):
        action = Action(
            task_id="task-123",
            name="publish_post",
            permission_level="publish",
        )

        approval = create_approval_if_needed(
            action=action,
            current_level=AutonomyLevel.PREPARE,
            reason="publishing requires permission",
        )

        self.assertIsNotNone(approval)
        self.assertEqual(approval.action_id, action.id)
        self.assertEqual(approval.task_id, action.task_id)
        self.assertEqual(approval.required_level, "publish")
        self.assertEqual(approval.status, "pending")

    def test_no_approval_when_level_is_sufficient(self):
        action = Action(
            task_id="task-123",
            name="publish_post",
            permission_level="publish",
        )

        approval = create_approval_if_needed(
            action=action,
            current_level=AutonomyLevel.PUBLISH,
            reason="publishing requires permission",
        )

        self.assertIsNone(approval)


if __name__ == "__main__":
    unittest.main()
