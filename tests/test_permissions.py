import unittest

from core.permissions import AutonomyLevel, can_execute, requires_approval


class TestPermissions(unittest.TestCase):
    def test_higher_level_can_execute_lower_requirement(self):
        self.assertTrue(
            can_execute(AutonomyLevel.EXECUTE, AutonomyLevel.PREPARE)
        )

    def test_lower_level_cannot_execute_higher_requirement(self):
        self.assertFalse(
            can_execute(AutonomyLevel.PREPARE, AutonomyLevel.PUBLISH)
        )

    def test_publish_requires_approval_when_not_authorized(self):
        self.assertTrue(
            requires_approval(AutonomyLevel.EXECUTE, AutonomyLevel.PUBLISH)
        )

    def test_publish_does_not_require_approval_when_authorized(self):
        self.assertFalse(
            requires_approval(AutonomyLevel.PUBLISH, AutonomyLevel.PUBLISH)
        )


if __name__ == "__main__":
    unittest.main()
