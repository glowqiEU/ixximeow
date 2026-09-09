import unittest

from core.models import Decision, Task
from core.objective import Objective, ObjectiveCriterion


class TestObjectiveContract(unittest.TestCase):
    def test_objective_requires_at_least_one_criterion(self):
        with self.assertRaises(ValueError):
            Objective(
                decision_id="decision-1",
                task_id="task-1",
                description="publish post",
            )

    def test_objective_criterion_is_explicit(self):
        criterion = ObjectiveCriterion(
            name="post is visible",
            kind="boolean",
            expected=True,
        )
        objective = Objective(
            decision_id="decision-1",
            task_id="task-1",
            description="publish post",
            criteria=[criterion],
        )

        self.assertEqual(objective.criteria[0].name, "post is visible")
        self.assertEqual(objective.criteria[0].kind, "boolean")
        self.assertTrue(objective.criteria[0].expected)

    def test_invalid_criterion_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            ObjectiveCriterion(name="post exists", kind="vibes")

    def test_objective_lineage_is_explicit(self):
        decision = Decision(
            objective="publish post",
            action="publish_post",
            reason="scheduled",
            id="decision-1",
        )
        task = Task(
            title="publish post",
            decision_id=decision.id,
            id="task-1",
        )
        objective = Objective(
            decision_id=decision.id,
            task_id=task.id,
            description="publish post",
            criteria=[
                ObjectiveCriterion(
                    name="post is visible",
                    kind="boolean",
                    expected=True,
                )
            ],
        )

        self.assertEqual(objective.decision_id, decision.id)
        self.assertEqual(objective.task_id, task.id)


if __name__ == "__main__":
    unittest.main()
