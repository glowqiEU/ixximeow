import unittest

from core.approval import Approval


class TestApproval(unittest.TestCase):
    def test_approval_defaults_to_pending(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )

        self.assertEqual(approval.status, "pending")

    def test_approval_can_be_approved(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
            status="approved",
        )

        self.assertEqual(approval.status, "approved")

    def test_approval_can_be_rejected(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
            status="rejected",
        )

        self.assertEqual(approval.status, "rejected")


if __name__ == "__main__":
    unittest.main()
