import unittest

from core.approval import Approval
from core.approval_service import create_approval_if_needed
from core.permissions import AutonomyLevel


class TestApprovalContractV1(unittest.TestCase):
    def test_no_approval_when_current_level_is_sufficient(self):
        approval = create_approval_if_needed(
            task_id="task-1",
            current_level=AutonomyLevel.EXECUTE,
            required_level=AutonomyLevel.EXECUTE,
            reason="same level",
        )
        self.assertIsNone(approval)

    def test_approval_contains_required_level_and_reason(self):
        approval = create_approval_if_needed(
            task_id="task-1",
            current_level=AutonomyLevel.EXECUTE,
            required_level=AutonomyLevel.PUBLISH,
            reason="publishing requires approval",
        )
        self.assertIsNotNone(approval)
        self.assertEqual(approval.task_id, "task-1")
        self.assertEqual(approval.required_level, "publish")
        self.assertEqual(approval.reason, "publishing requires approval")
        self.assertEqual(approval.status, "pending")

    def test_approval_requires_nonempty_task_id(self):
        with self.assertRaises(ValueError):
            Approval(
                task_id="",
                required_level="publish",
                reason="reason",
            )

    def test_approval_requires_nonempty_reason(self):
        with self.assertRaises(ValueError):
            Approval(
                task_id="task-1",
                required_level="publish",
                reason="",
            )

    def test_approval_rejects_invalid_required_level(self):
        with self.assertRaises(ValueError):
            Approval(
                task_id="task-1",
                required_level="unknown",
                reason="reason",
            )


if __name__ == "__main__":
    unittest.main()
