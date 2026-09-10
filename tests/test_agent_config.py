import unittest
from unittest.mock import patch

from core.agent_config import CURRENT_AUTONOMY_LEVEL
from core.approval_gate import check_approval
from core.executor import _ensure_execution_permission
from core.models import Task
from core.permissions import AutonomyLevel


class TestAgentConfig(unittest.TestCase):
    def test_current_autonomy_level_is_prepare(self):
        self.assertEqual(CURRENT_AUTONOMY_LEVEL, AutonomyLevel.PREPARE)

    def test_approval_gate_and_executor_read_same_autonomy_source(self):
        task = Task(title="execute task", required_level="execute")

        with patch("core.agent_config.CURRENT_AUTONOMY_LEVEL", AutonomyLevel.EXECUTE):
            self.assertIsNone(check_approval(task))
            _ensure_execution_permission(task, approval=None)

        with patch("core.agent_config.CURRENT_AUTONOMY_LEVEL", AutonomyLevel.PREPARE):
            self.assertIsNotNone(check_approval(task))
            with self.assertRaises(PermissionError):
                _ensure_execution_permission(task, approval=None)


if __name__ == "__main__":
    unittest.main()
