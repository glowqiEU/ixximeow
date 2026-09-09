import unittest

from core.action import Action
from core.evidence import Evidence
from core.execution import Execution
from core.models import Decision, Result, Task
from core.objective import Objective, ObjectiveCriterion
from core.outcome import Outcome
from core.verification import verify_outcome


class TestOutcomeContract(unittest.TestCase):
    def setUp(self):
        self.decision = Decision(objective="publish the approved post", action="publish_post", reason="scheduled publication", id="decision-1")
        self.task = Task(title="publish post", decision_id="decision-1", id="task-1")
        self.action = Action(task_id="task-1", name="publish_post", id="action-1")
        self.execution = Execution(action_id="action-1", task_id="task-1", id="execution-1")
        self.result = Result(task_id="task-1", action_id="action-1", execution_id="execution-1", success=True, summary="platform accepted publication", id="result-1")
        self.objective = Objective(
            decision_id="decision-1", task_id="task-1",
            description="publish and verify visibility",
            criteria=[ObjectiveCriterion("post_visible", "boolean", True)],
            id="objective-1",
        )
        self.evidence = Evidence(
            result_id="result-1", execution_id="execution-1", kind="external_observation",
            claim="post_visible", value=True, content="post is visible on the platform",
            source="platform check", verified=True, id="evidence-1",
        )

    def verify(self, outcome, results=None, evidence=None):
        verify_outcome(self.decision, self.task, self.objective, results if results is not None else [self.result], evidence if evidence is not None else [self.evidence], outcome)

    def test_outcome_can_be_achieved(self):
        outcome = Outcome(decision_id="decision-1", task_id="task-1", status="achieved", summary="post is live and visible", result_ids=["result-1"], evidence_ids=["evidence-1"])
        self.verify(outcome)

    def test_technical_success_does_not_force_achieved_outcome(self):
        outcome = Outcome(decision_id="decision-1", task_id="task-1", status="uncertain", summary="visibility could not be verified", result_ids=["result-1"])
        self.verify(outcome, evidence=[])

    def test_achieved_outcome_requires_verified_evidence(self):
        evidence = Evidence(result_id="result-1", execution_id="execution-1", kind="external_observation", claim="post_visible", value=True, content="post appears to be visible", verified=False, id="evidence-2")
        outcome = Outcome(decision_id="decision-1", task_id="task-1", status="achieved", summary="done", result_ids=["result-1"], evidence_ids=["evidence-2"])
        with self.assertRaises(ValueError):
            self.verify(outcome, evidence=[evidence])

    def test_wrong_status_is_rejected(self):
        outcome = Outcome(decision_id="decision-1", task_id="task-1", status="uncertain", summary="wrong status", result_ids=["result-1"], evidence_ids=["evidence-1"])
        with self.assertRaises(ValueError):
            self.verify(outcome)

    def test_unknown_result_is_rejected(self):
        outcome = Outcome(decision_id="decision-1", task_id="task-1", status="achieved", summary="done", result_ids=["missing-result"], evidence_ids=["evidence-1"])
        with self.assertRaises(ValueError):
            self.verify(outcome)

    def test_cross_task_evidence_is_rejected(self):
        other_result = Result(task_id="task-2", action_id="action-2", execution_id="execution-2", success=True, summary="other task", id="result-2")
        other_evidence = Evidence(result_id="result-2", execution_id="execution-2", kind="execution_output", claim="post_visible", value=True, content="other output", id="evidence-2")
        outcome = Outcome(decision_id="decision-1", task_id="task-1", status="achieved", summary="done", result_ids=["result-2"], evidence_ids=["evidence-2"])
        with self.assertRaises(ValueError):
            self.verify(outcome, results=[self.result, other_result], evidence=[self.evidence, other_evidence])

    def test_evidence_execution_must_match_result_execution(self):
        mismatched = Evidence(result_id="result-1", execution_id="execution-2", kind="verification", claim="post_visible", value=True, content="mismatched provenance", verified=True, id="evidence-3")
        outcome = Outcome(decision_id="decision-1", task_id="task-1", status="achieved", summary="done", result_ids=["result-1"], evidence_ids=["evidence-3"])
        with self.assertRaises(ValueError):
            self.verify(outcome, evidence=[mismatched])


if __name__ == "__main__":
    unittest.main()
