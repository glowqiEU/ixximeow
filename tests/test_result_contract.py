import unittest

from core.models import Result


class TestResultContract(unittest.TestCase):
    def test_result_requires_full_lineage(self):
        result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="handler completed",
        )

        self.assertEqual(result.task_id, "task-1")
        self.assertEqual(result.action_id, "action-1")
        self.assertEqual(result.execution_id, "execution-1")

    def test_result_rejects_empty_task_id(self):
        with self.assertRaises(ValueError):
            Result(
                task_id="   ",
                action_id="action-1",
                execution_id="execution-1",
                success=True,
                summary="done",
            )

    def test_result_rejects_empty_action_id(self):
        with self.assertRaises(ValueError):
            Result(
                task_id="task-1",
                action_id="   ",
                execution_id="execution-1",
                success=True,
                summary="done",
            )

    def test_result_rejects_empty_execution_id(self):
        with self.assertRaises(ValueError):
            Result(
                task_id="task-1",
                action_id="action-1",
                execution_id="   ",
                success=True,
                summary="done",
            )

    def test_result_success_is_technical_execution_success(self):
        result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="external adapter accepted the request",
        )

        self.assertTrue(result.success)
        self.assertIn("accepted", result.summary)


if __name__ == "__main__":
    unittest.main()
