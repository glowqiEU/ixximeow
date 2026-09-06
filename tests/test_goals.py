import unittest

from core.goals import Goal


class TestGoal(unittest.TestCase):
    def test_goal_has_stable_id(self):
        goal = Goal(
            title="test goal",
            description="test description",
        )

        self.assertIsNotNone(goal.id)
        self.assertTrue(goal.id)

    def test_goal_defaults_are_safe(self):
        goal = Goal(
            title="test goal",
            description="test description",
        )

        self.assertEqual(goal.priority, 0)
        self.assertEqual(goal.status, "active")
        self.assertEqual(goal.metrics, [])
        self.assertEqual(goal.constraints, [])


if __name__ == "__main__":
    unittest.main()
