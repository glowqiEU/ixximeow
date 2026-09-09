import unittest

from core.action import Action
from core.evidence import Evidence
from core.execution import Execution
from core.models import Decision, Result, Task
from core.outcome import Outcome
from core.verification import verify_outcome


class TestOutcomeContract(unittest.TestCase):
    def setUp(self):
        self.decision = Decision(
            objective="publish the approved post",
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
            summary="platform accepted publication",
            id="result-1",
        )
        self.evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="external_observation",
            content="post is visible on the platform",
            source="platform check",
            verified=True,
            id="evidence-1",
        )

    def test_outcome_can_be_achieved(self):
        outcome = Outcome(
            decision_id="decision-1",
            task_id="task-1",
            status="achieved",
            summary="post is live and visible",
            result_ids=["result-1"],
            evidence_ids=["evidence-1"],
        )

        verify_outcome(
            self.decision,
            self.task,
            [self.result],
            [self.evidence],
            outcome,
        )

    def test_technical_success_does_not_force_achieved_outcome(self):
        outcome = Outcome(
            decision_id="decision-1",
            task_id="task-1",
            status="uncertain",
            summary="platform accepted request but visibility could not be verified",
            result_ids=["result-1"],
        )

        verify_outcome(
            self.decision,
            self.task,
            [self.result],
            [],
            outcome,
        )

    def test_achieved_outcome_requires_evidence(self):
        outcome = Outcome(
            decision_id="decision-1",
            task_id="task-1",
            status="achieved",
            summary="done",
            result_ids=["result-1"],
        )

        with self.assertRaises(ValueError):
            verify_outcome(
                self.decision,
                self.task,
                [self.result],
                [],
                outcome,
            )

    def test_achieved_outcome_requires_verified_evidence(self):
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="external_observation",
            content="post appears to be visible",
            verified=False,
            id="evidence-2",
        )
        outcome = Outcome(
            decision_id="decision-1",
            task_id="task-1",
            status="achieved",
            summary="done",
            result_ids=["result-1"],
            evidence_ids=["evidence-2"],
        )

        with self.assertRaises(ValueError):
            verify_outcome(
                self.decision,
                self.task,
                [self.result],
                [evidence],
                outcome,
            )

    def test_unknown_result_is_rejected(self):
        outcome = Outcome(
            decision_id="decision-1",
            task_id="task-1",
            status="achieved",
            summary="done",
            result_ids=["missing-result"],
            evidence_ids=["evidence-1"],
        )

        with self.assertRaises(ValueError):
            verify_outcome(
                self.decision,
                self.task,
                [self.result],
                [self.evidence],
                outcome,
            )

    def test_cross_task_evidence_is_rejected(self):
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
            kind="execution_output",
            content="other output",
            id="evidence-2",
        )
        outcome = Outcome(
            decision_id="decision-1",
            task_id="task-1",
            status="achieved",
            summary="done",
            result_ids=["result-2"],
            evidence_ids=["evidence-2"],
        )

        with self.assertRaises(ValueError):
            verify_outcome(
                self.decision,
                self.task,
                [self.result, other_result],
                [self.evidence, other_evidence],
                outcome,
            )


if __name__ == "__main__":
    unittest.main()
