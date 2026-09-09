import unittest

from core.execution import Execution


class TestExecutionContract(unittest.TestCase):
    def test_execution_has_stable_identity_and_action_lineage(self):
        execution = Execution(action_id="action-1", task_id="task-1")

        self.assertIsNotNone(execution.id)
        self.assertEqual(execution.action_id, "action-1")
        self.assertEqual(execution.task_id, "task-1")
        self.assertEqual(execution.status, "pending")
        self.assertEqual(execution.attempt, 0)
        self.assertEqual(execution.idempotency_key, "action-1")

    def test_starting_execution_creates_first_attempt(self):
        execution = Execution(action_id="action-1", task_id="task-1")

        execution.transition("running")

        self.assertEqual(execution.status, "running")
        self.assertEqual(execution.attempt, 1)
        self.assertIsNotNone(execution.started_at)
        self.assertIsNone(execution.finished_at)

    def test_execution_can_finish_successfully(self):
        execution = Execution(action_id="action-1", task_id="task-1")
        execution.transition("running")
        execution.transition("succeeded")

        self.assertEqual(execution.status, "succeeded")
        self.assertIsNotNone(execution.finished_at)

    def test_crash_ambiguity_is_explicit(self):
        execution = Execution(action_id="action-1", task_id="task-1")
        execution.transition("running")
        execution.transition("uncertain")

        self.assertEqual(execution.status, "uncertain")
        self.assertIsNone(execution.finished_at)

    def test_uncertain_execution_can_be_retried_without_changing_identity(self):
        execution = Execution(action_id="action-1", task_id="task-1")
        execution.transition("running")
        execution.transition("uncertain")
        execution_id = execution.id
        idempotency_key = execution.idempotency_key

        execution.transition("running")

        self.assertEqual(execution.id, execution_id)
        self.assertEqual(execution.idempotency_key, idempotency_key)
        self.assertEqual(execution.attempt, 2)
        self.assertEqual(execution.status, "running")

    def test_execution_rejects_missing_lineage(self):
        with self.assertRaises(ValueError):
            Execution(action_id="", task_id="task-1")

        with self.assertRaises(ValueError):
            Execution(action_id="action-1", task_id="")

    def test_execution_rejects_invalid_transition(self):
        execution = Execution(action_id="action-1", task_id="task-1")

        with self.assertRaises(ValueError):
            execution.transition("succeeded")


if __name__ == "__main__":
    unittest.main()
