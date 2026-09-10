import unittest

from core.action import Action
from core.evidence import Evidence
from core.execution import Execution
from core.models import Decision, Result, Task
from core.objective import Objective, ObjectiveCriterion
from core.outcome_resolver import resolve_outcome


class TestOutcomeResolver(unittest.TestCase):
    def setUp(self):
        self.decision = Decision(
            objective="publish approved post",
            action="publish_post",
            reason="scheduled publication",
            id="decision-1",
        )
        self.task = Task(
            title="publish post",
            decision_id="decision-1",
            id="task-1",
        )
        self.action = Action(
            task_id="task-1",
            name="publish_post",
            id="action-1",
        )
        self.execution = Execution(
            action_id="action-1",
            task_id="task-1",
            id="execution-1",
        )
        self.result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="publication request accepted",
            id="result-1",
        )

    def evidence(self, claim, value, verified=True, id="evidence-1"):
        return Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="external_observation",
            claim=claim,
            value=value,
            content=f"{claim}: {value}",
            verified=verified,
            id=id,
        )

    def test_all_criteria_passing_produces_achieved(self):
        objective = Objective(
            decision_id="decision-1",
            task_id="task-1",
            description="publish the approved post and verify visibility",
            criteria=[
                ObjectiveCriterion("post_visible", "boolean", True),
                ObjectiveCriterion("post_id", "exists"),
            ],
        )
        evidence = [
            self.evidence("post_visible", True, id="evidence-1"),
            self.evidence("post_id", "123", id="evidence-2"),
        ]

        outcome = resolve_outcome(
            self.decision,
            self.task,
            objective,
            [self.result],
            evidence,
        )

        self.assertEqual(outcome.status, "achieved")
        self.assertEqual(outcome.result_ids, ["result-1"])
        self.assertEqual(outcome.evidence_ids, ["evidence-1", "evidence-2"])

    def test_failed_criterion_produces_not_achieved(self):
        objective = Objective(
            decision_id="decision-1",
            task_id="task-1",
            description="publish the post",
            criteria=[ObjectiveCriterion("post_visible", "boolean", True)],
        )

        outcome = resolve_outcome(
            self.decision,
            self.task,
            objective,
            [self.result],
            [self.evidence("post_visible", False)],
        )

        self.assertEqual(outcome.status, "not_achieved")

    def test_missing_or_conflicting_evidence_produces_uncertain(self):
        objective = Objective(
            decision_id="decision-1",
            task_id="task-1",
            description="publish the post",
            criteria=[ObjectiveCriterion("post_visible", "boolean", True)],
        )

        missing = resolve_outcome(
            self.decision,
            self.task,
            objective,
            [self.result],
            [],
        )
        conflicting = resolve_outcome(
            self.decision,
            self.task,
            objective,
            [self.result],
            [
                self.evidence("post_visible", True, id="evidence-1"),
                self.evidence("post_visible", False, id="evidence-2"),
            ],
        )

        self.assertEqual(missing.status, "uncertain")
        self.assertEqual(conflicting.status, "uncertain")

    def test_unrelated_task_evidence_cannot_satisfy_objective(self):
        objective = Objective(
            decision_id="decision-1",
            task_id="task-1",
            description="publish the post",
            criteria=[ObjectiveCriterion("post_visible", "boolean", True)],
        )
        other_result = Result(
            task_id="task-2",
            action_id="action-2",
            execution_id="execution-2",
            success=True,
            summary="other task",
            id="result-2",
        )
        other_evidence = Evidence(
            result_id="result-2",
            execution_id="execution-2",
            kind="external_observation",
            claim="post_visible",
            value=True,
            content="other task post is visible",
            verified=True,
            id="evidence-2",
        )

        outcome = resolve_outcome(
            self.decision,
            self.task,
            objective,
            [self.result, other_result],
            [other_evidence],
        )

        self.assertEqual(outcome.status, "uncertain")
        self.assertEqual(outcome.result_ids, ["result-1"])
        self.assertEqual(outcome.evidence_ids, [])

    def test_wrong_objective_lineage_is_rejected(self):
        objective = Objective(
            decision_id="decision-2",
            task_id="task-1",
            description="wrong decision",
            criteria=[ObjectiveCriterion("post_visible", "boolean", True)],
        )

        with self.assertRaises(ValueError):
            resolve_outcome(
                self.decision,
                self.task,
                objective,
                [self.result],
                [],
            )


if __name__ == "__main__":
    unittest.main()
