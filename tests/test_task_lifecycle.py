import unittest

from core.models import Task
from core.task_lifecycle import transition_task


class TestTaskLifecycle(unittest.TestCase):
    def test_pending_to_running(self):
        task = Task(title="test")

        transition_task(task, "running")

        self.assertEqual(task.status, "running")

    def test_running_to_completed(self):
        task = Task(title="test", status="running")

        transition_task(task, "completed")

        self.assertEqual(task.status, "completed")

    def test_running_to_failed(self):
        task = Task(title="test", status="running")

        transition_task(task, "failed")

        self.assertEqual(task.status, "failed")

    def test_invalid_transition_raises(self):
        task = Task(title="test", status="pending")

        with self.assertRaises(ValueError):
            transition_task(task, "completed")


if __name__ == "__main__":
    unittest.main()
