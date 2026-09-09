import unittest

from core.action import Action
from core.evidence import Evidence
from core.execution import Execution
from core.models import Result, Task
from core.verification import verify_evidence, verify_execution_result


class TestExecutionVerification(unittest.TestCase):
    def setUp(self):
        self.task = Task(title="test", id="task-1")
        self.action = Action(task_id="task-1", name="test_action", id="action-1")
        self.execution = Execution(
            action_id="action-1",
            task_id="task-1",
            status="succeeded",
            id="execution-1",
        )
        self.result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="done",
            id="result-1",
        )

    def test_valid_result_passes(self):
        verify_execution_result(
            self.task, self.action, self.execution, self.result
        )

    def test_wrong_action_is_rejected(self):
        action = Action(task_id="task-1", name="other", id="action-2")

        with self.assertRaises(ValueError):
            verify_execution_result(
                self.task, action, self.execution, self.result
            )

    def test_wrong_execution_is_rejected(self):
        execution = Execution(
            action_id="action-1",
            task_id="task-1",
            id="execution-2",
        )

        with self.assertRaises(ValueError):
            verify_execution_result(
                self.task, self.action, execution, self.result
            )

    def test_wrong_result_lineage_is_rejected(self):
        result = Result(
            task_id="task-1",
            action_id="action-2",
            execution_id="execution-1",
            success=True,
            summary="done",
        )

        with self.assertRaises(ValueError):
            verify_execution_result(
                self.task, self.action, self.execution, result
            )

    def test_empty_summary_is_rejected(self):
        with self.assertRaises(ValueError):
            Result(
                task_id="task-1",
                action_id="action-1",
                execution_id="execution-1",
                success=True,
                summary="   ",
            )

    def test_evidence_must_match_result_and_execution(self):
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="execution_output",
            claim="post_id",
            value="123",
            content="post id 123",
        )

        verify_evidence(self.result, self.execution, evidence)

    def test_evidence_with_wrong_result_is_rejected(self):
        evidence = Evidence(
            result_id="result-2",
            execution_id="execution-1",
            kind="execution_output",
            claim="post_id",
            value="123",
            content="post id 123",
        )

        with self.assertRaises(ValueError):
            verify_evidence(self.result, self.execution, evidence)


if __name__ == "__main__":
    unittest.main()
