import unittest

from core.models import Result, Task
from core.verification import verify_execution_result


class TestExecutionVerification(unittest.TestCase):
    def test_valid_result_passes(self):
        task = Task(title="test", id="task-1")
        result = Result(task_id="task-1", success=True, summary="done")

        verify_execution_result(task, result)

    def test_wrong_task_is_rejected(self):
        task = Task(title="test", id="task-1")
        result = Result(task_id="task-2", success=True, summary="done")

        with self.assertRaises(ValueError):
            verify_execution_result(task, result)

    def test_non_boolean_success_is_rejected(self):
        task = Task(title="test", id="task-1")
        result = Result(task_id="task-1", success="yes", summary="done")

        with self.assertRaises(ValueError):
            verify_execution_result(task, result)

    def test_empty_summary_is_rejected(self):
        task = Task(title="test", id="task-1")
        result = Result(task_id="task-1", success=True, summary="   ")

        with self.assertRaises(ValueError):
            verify_execution_result(task, result)


if __name__ == "__main__":
    unittest.main()
