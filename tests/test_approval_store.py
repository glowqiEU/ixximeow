import unittest

from core.approval import Approval
from core.approval_store import load_approvals, save_approvals


class TestApprovalStore(unittest.TestCase):
    def test_approval_persists(self):
        approval = Approval(
            action_id="action-123",
            task_id="task-123",
            required_level="publish",
            reason="publishing requires permission",
        )

        save_approvals([approval])
        loaded = load_approvals()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].id, approval.id)
        self.assertEqual(loaded[0].action_id, "action-123")
        self.assertEqual(loaded[0].task_id, "task-123")
        self.assertEqual(loaded[0].status, "pending")


if __name__ == "__main__":
    unittest.main()
