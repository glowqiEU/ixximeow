import unittest
from unittest.mock import patch

from core.action import Action
from core.approval_gate import check_approval
from core.permissions import AutonomyLevel


class TestApprovalGate(unittest.TestCase):
    def test_approval_is_bound_to_action(self):
        action = Action(
            task_id="task-1",
            name="publish_post",
            permission_level="publish",
        )

        with patch("core.approval_gate.CURRENT_AUTONOMY_LEVEL", AutonomyLevel.EXECUTE):
            approval = check_approval(action)

        self.assertIsNotNone(approval)
        self.assertEqual(approval.action_id, action.id)
        self.assertEqual(approval.task_id, action.task_id)

    def test_no_approval_when_action_permission_is_sufficient(self):
        action = Action(
            task_id="task-1",
            name="prepare_post",
            permission_level="execute",
        )

        with patch("core.approval_gate.CURRENT_AUTONOMY_LEVEL", AutonomyLevel.EXECUTE):
            approval = check_approval(action)

        self.assertIsNone(approval)


if __name__ == "__main__":
    unittest.main()
