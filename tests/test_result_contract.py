import unittest

from core.models import Result


class TestResultContract(unittest.TestCase):
    def test_result_requires_execution_lineage(self):
        result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="accepted",
        )

        self.assertEqual(result.task_id, "task-1")
        self.assertEqual(result.action_id, "action-1")
        self.assertEqual(result.execution_id, "execution-1")

    def test_result_rejects_missing_action_id(self):
        with self.assertRaises(ValueError):
            Result(
                task_id="task-1",
                action_id="",
                execution_id="execution-1",
                success=True,
                summary="accepted",
            )

    def test_result_rejects_missing_execution_id(self):
        with self.assertRaises(ValueError):
            Result(
                task_id="task-1",
                action_id="action-1",
                execution_id="",
                success=True,
                summary="accepted",
            )

    def test_success_means_technical_success_only(self):
        result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="platform accepted request",
        )

        self.assertTrue(result.success)
        self.assertNotIn("objective achieved", result.summary)


if __name__ == "__main__":
    unittest.main()
