import unittest

from core.objective import Objective, ObjectiveCriterion


class TestObjectiveContract(unittest.TestCase):
    def test_objective_requires_at_least_one_criterion(self):
        with self.assertRaises(ValueError):
            Objective(
                decision_id="decision-1",
                task_id="task-1",
                description="publish post",
                criteria=[],
            )

    def test_criterion_has_explicit_claim_and_expected_value(self):
        criterion = ObjectiveCriterion(
            claim="post_visible",
            kind="boolean",
            expected=True,
        )

        self.assertEqual(criterion.claim, "post_visible")
        self.assertEqual(criterion.kind, "boolean")
        self.assertIs(criterion.expected, True)
        self.assertEqual(criterion.name, "post_visible")

    def test_invalid_criterion_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            ObjectiveCriterion(
                claim="post_visible",
                kind="guess",
                expected=True,
            )

    def test_boolean_criterion_requires_boolean_expected_value(self):
        with self.assertRaises(ValueError):
            ObjectiveCriterion(
                claim="post_visible",
                kind="boolean",
                expected="true",
            )

    def test_objective_lineage_is_explicit(self):
        objective = Objective(
            decision_id="decision-1",
            task_id="task-1",
            description="publish post",
            criteria=[ObjectiveCriterion("post_visible", "boolean", True)],
        )

        self.assertEqual(objective.decision_id, "decision-1")
        self.assertEqual(objective.task_id, "task-1")


if __name__ == "__main__":
    unittest.main()
