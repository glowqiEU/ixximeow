import unittest

from core.models import Decision
from core.plan_builder import build_plan


class TestPlanBuilder(unittest.TestCase):
    def test_builds_one_step_plan_from_decision(self):
        decision = Decision(
            objective="goal-1",
            action="create X content",
            reason="selected action",
            goal_id="goal-1",
        )

        plan = build_plan(decision)

        self.assertEqual(plan.decision_id, decision.id)
        self.assertEqual(plan.goal_id, decision.goal_id)
        self.assertEqual(plan.steps, [decision.action])
        self.assertEqual(plan.status, "proposed")

    def test_rejects_empty_action(self):
        decision = Decision(
            objective="goal-1",
            action="   ",
            reason="invalid",
            goal_id="goal-1",
        )

        with self.assertRaises(ValueError):
            build_plan(decision)


if __name__ == "__main__":
    unittest.main()
