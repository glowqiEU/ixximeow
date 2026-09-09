import unittest

from core.action import Action
from core.execution import Execution
from core.models import Result, Task
from core.verification import verify_execution_result


class TestExecutionVerification(unittest.TestCase):
    def _lineage(self):
        task = Task(title="test", id="task-1")
        action = Action(task_id=task.id, name="test", id="action-1")
        execution = Execution(
            action_id=action.id,
            task_id=task.id,
            id="execution-1",
        )
        execution.transition("running")
        execution.transition("succeeded")
        result = Result(
            task_id=task.id,
            action_id=action.id,
            execution_id=execution.id,
            success=True,
            summary="done",
        )
        return task, action, execution, result

    def test_valid_result_passes(self):
        task, action, execution, result = self._lineage()
        verify_execution_result(task, action, execution, result)

    def test_wrong_task_is_rejected(self):
        task, action, execution, result = self._lineage()
        result.task_id = "task-2"

        with self.assertRaises(ValueError):
            verify_execution_result(task, action, execution, result)

    def test_wrong_action_is_rejected(self):
        task, action, execution, result = self._lineage()
        result.action_id = "action-2"

        with self.assertRaises(ValueError):
            verify_execution_result(task, action, execution, result)

    def test_wrong_execution_is_rejected(self):
        task, action, execution, result = self._lineage()
        result.execution_id = "execution-2"

        with self.assertRaises(ValueError):
            verify_execution_result(task, action, execution, result)

    def test_successful_result_requires_succeeded_execution(self):
        task = Task(title="test", id="task-1")
        action = Action(task_id=task.id, name="test", id="action-1")
        execution = Execution(
            action_id=action.id,
            task_id=task.id,
            id="execution-1",
        )
        execution.transition("running")
        result = Result(
            task_id=task.id,
            action_id=action.id,
            execution_id=execution.id,
            success=True,
            summary="done",
        )

        with self.assertRaises(ValueError):
            verify_execution_result(task, action, execution, result)

    def test_non_boolean_success_is_rejected(self):
        task, action, execution, result = self._lineage()
        result.success = "yes"

        with self.assertRaises(ValueError):
            verify_execution_result(task, action, execution, result)

    def test_empty_summary_is_rejected(self):
        task, action, execution, result = self._lineage()
        result.summary = "   "

        with self.assertRaises(ValueError):
            verify_execution_result(task, action, execution, result)


if __name__ == "__main__":
    unittest.main()
