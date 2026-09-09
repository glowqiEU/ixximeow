import unittest

from core.action import Action
from core.approval import Approval
from core.approval_service import create_approval_if_needed
from core.permissions import AutonomyLevel


class TestApprovalContractV1(unittest.TestCase):
    def test_no_approval_when_current_level_is_sufficient(self):
        action = Action(
            task_id="task-1",
            name="prepare_post",
            permission_level="execute",
        )

        approval = create_approval_if_needed(
            action=action,
            current_level=AutonomyLevel.EXECUTE,
            reason="same level",
        )

        self.assertIsNone(approval)

    def test_approval_is_bound_to_concrete_action_and_task(self):
        action = Action(
            task_id="task-1",
            name="publish_post",
            permission_level="publish",
        )

        approval = create_approval_if_needed(
            action=action,
            current_level=AutonomyLevel.EXECUTE,
            reason="publishing requires approval",
        )

        self.assertIsNotNone(approval)
        self.assertEqual(approval.action_id, action.id)
        self.assertEqual(approval.task_id, action.task_id)
        self.assertEqual(approval.required_level, "publish")
        self.assertEqual(approval.reason, "publishing requires approval")
        self.assertEqual(approval.status, "pending")

    def test_approval_requires_nonempty_action_id(self):
        with self.assertRaises(ValueError):
            Approval(
                action_id="",
                task_id="task-1",
                required_level="publish",
                reason="reason",
            )

    def test_approval_requires_nonempty_task_id(self):
        with self.assertRaises(ValueError):
            Approval(
                action_id="action-1",
                task_id="",
                required_level="publish",
                reason="reason",
            )

    def test_approval_requires_nonempty_reason(self):
        with self.assertRaises(ValueError):
            Approval(
                action_id="action-1",
                task_id="task-1",
                required_level="publish",
                reason="",
            )

    def test_approval_rejects_invalid_required_level(self):
        with self.assertRaises(ValueError):
            Approval(
                action_id="action-1",
                task_id="task-1",
                required_level="unknown",
                reason="reason",
            )

    def test_approval_rejects_invalid_status(self):
        with self.assertRaises(ValueError):
            Approval(
                action_id="action-1",
                task_id="task-1",
                required_level="publish",
                reason="reason",
                status="unknown",
            )


if __name__ == "__main__":
    unittest.main()
