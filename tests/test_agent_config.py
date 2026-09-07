import unittest

from core.agent_config import CURRENT_AUTONOMY_LEVEL
from core.permissions import AutonomyLevel


class TestAgentConfig(unittest.TestCase):
    def test_current_autonomy_level_is_prepare(self):
        self.assertEqual(CURRENT_AUTONOMY_LEVEL, AutonomyLevel.PREPARE)


if __name__ == "__main__":
    unittest.main()
