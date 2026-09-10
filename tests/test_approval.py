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
        )

        approval.transition("approved")

        self.assertEqual(approval.status, "approved")

    def test_approval_can_be_rejected(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )

        approval.transition("rejected")

        self.assertEqual(approval.status, "rejected")

    def test_pending_approval_can_be_cancelled(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )

        approval.transition("cancelled")

        self.assertEqual(approval.status, "cancelled")

    def test_approved_approval_is_terminal(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )
        approval.transition("approved")

        with self.assertRaises(ValueError):
            approval.transition("rejected")

    def test_rejected_approval_is_terminal(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )
        approval.transition("rejected")

        with self.assertRaises(ValueError):
            approval.transition("approved")

    def test_cancelled_approval_is_terminal(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )
        approval.transition("cancelled")

        with self.assertRaises(ValueError):
            approval.transition("approved")

    def test_invalid_approval_transition_is_rejected(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )

        with self.assertRaises(ValueError):
            approval.transition("pending")


if __name__ == "__main__":
    unittest.main()
