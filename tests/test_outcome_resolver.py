import unittest

from core.evidence import Evidence
from core.models import Decision, Result, Task
from core.objective import Objective, ObjectiveCriterion
from core.outcome_resolver import resolve_outcome


class TestOutcomeResolver(unittest.TestCase):
    def setUp(self):
        self.decision = Decision(
            objective="publish post",
            action="publish_post",
            reason="scheduled",
            id="decision-1",
        )
        self.task = Task(
            title="publish post",
            decision_id="decision-1",
            id="task-1",
        )
        self.objective = Objective(
            decision_id="decision-1",
            task_id="task-1",
            description="publish post",
            criteria=[
                ObjectiveCriterion(
                    name="post is visible",
                    kind="boolean",
                    expected=True,
                )
            ],
        )

    def test_no_evidence_is_uncertain(self):
        outcome = resolve_outcome(
            self.decision,
            self.task,
            self.objective,
            [],
            [],
        )

        self.assertEqual(outcome.status, "uncertain")
        self.assertEqual(outcome.result_ids, [])
        self.assertEqual(outcome.evidence_ids, [])

    def test_evidence_does_not_silently_prove_objective(self):
        result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="platform accepted publication",
            id="result-1",
        )
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="external_observation",
            content="post appears visible",
            verified=True,
            id="evidence-1",
        )

        outcome = resolve_outcome(
            self.decision,
            self.task,
            self.objective,
            [result],
            [evidence],
        )

        self.assertEqual(outcome.status, "uncertain")
        self.assertIn("post is visible", outcome.summary)
        self.assertEqual(outcome.result_ids, ["result-1"])
        self.assertEqual(outcome.evidence_ids, ["evidence-1"])

    def test_result_from_another_task_is_rejected(self):
        result = Result(
            task_id="task-2",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="platform accepted publication",
        )

        with self.assertRaises(ValueError):
            resolve_outcome(
                self.decision,
                self.task,
                self.objective,
                [result],
                [],
            )

    def test_evidence_with_unknown_result_is_rejected(self):
        evidence = Evidence(
            result_id="missing-result",
            execution_id="execution-1",
            kind="external_observation",
            content="post appears visible",
        )

        with self.assertRaises(ValueError):
            resolve_outcome(
                self.decision,
                self.task,
                self.objective,
                [],
                [evidence],
            )

    def test_evidence_execution_must_match_result(self):
        result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="platform accepted publication",
            id="result-1",
        )
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-2",
            kind="external_observation",
            content="post appears visible",
        )

        with self.assertRaises(ValueError):
            resolve_outcome(
                self.decision,
                self.task,
                self.objective,
                [result],
                [evidence],
            )

    def test_wrong_objective_lineage_is_rejected(self):
        objective = Objective(
            decision_id="decision-2",
            task_id="task-1",
            description="publish post",
            criteria=[
                ObjectiveCriterion(
                    name="post is visible",
                    kind="boolean",
                    expected=True,
                )
            ],
        )

        with self.assertRaises(ValueError):
            resolve_outcome(
                self.decision,
                self.task,
                objective,
                [],
                [],
            )


if __name__ == "__main__":
    unittest.main()
