import unittest

from core.approval import Approval
from core.approval_lifecycle import transition_approval


class TestApprovalLifecycle(unittest.TestCase):
    def test_pending_can_be_approved(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )

        transition_approval(approval, "approved")

        self.assertEqual(approval.status, "approved")

    def test_pending_can_be_rejected(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )

        transition_approval(approval, "rejected")

        self.assertEqual(approval.status, "rejected")

    def test_approved_cannot_change(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
            status="approved",
        )

        with self.assertRaises(ValueError):
            transition_approval(approval, "rejected")

    def test_rejected_cannot_change(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
            status="rejected",
        )

        with self.assertRaises(ValueError):
            transition_approval(approval, "approved")


if __name__ == "__main__":
    unittest.main()
