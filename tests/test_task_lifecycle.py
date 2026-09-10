import unittest

from core.models import Task
from core.task_lifecycle import transition_task


class TestTaskLifecycle(unittest.TestCase):
    def test_pending_to_running(self):
        task = Task(title="test")

        transition_task(task, "running")

        self.assertEqual(task.status, "running")

    def test_pending_to_waiting_approval(self):
        task = Task(title="test")

        transition_task(task, "waiting_approval")

        self.assertEqual(task.status, "waiting_approval")

    def test_waiting_approval_to_running(self):
        task = Task(title="test", status="waiting_approval")

        transition_task(task, "running")

        self.assertEqual(task.status, "running")

    def test_waiting_approval_to_cancelled(self):
        task = Task(title="test", status="waiting_approval")

        transition_task(task, "cancelled")

        self.assertEqual(task.status, "cancelled")

    def test_running_to_completed(self):
        task = Task(title="test", status="running")

        transition_task(task, "completed")

        self.assertEqual(task.status, "completed")

    def test_running_to_failed(self):
        task = Task(title="test", status="running")

        transition_task(task, "failed")

        self.assertEqual(task.status, "failed")

    def test_running_to_blocked(self):
        task = Task(title="test", status="running")

        transition_task(task, "blocked")

        self.assertEqual(task.status, "blocked")

    def test_blocked_to_running(self):
        task = Task(title="test", status="blocked")

        transition_task(task, "running")

        self.assertEqual(task.status, "running")

    def test_blocked_to_cancelled(self):
        task = Task(title="test", status="blocked")

        transition_task(task, "cancelled")

        self.assertEqual(task.status, "cancelled")

    def test_blocked_cannot_complete(self):
        task = Task(title="test", status="blocked")

        with self.assertRaises(ValueError):
            transition_task(task, "completed")

    def test_blocked_cannot_fail(self):
        task = Task(title="test", status="blocked")

        with self.assertRaises(ValueError):
            transition_task(task, "failed")

    def test_blocked_cannot_be_uncertain(self):
        task = Task(title="test", status="blocked")

        with self.assertRaises(ValueError):
            transition_task(task, "uncertain")

    def test_failed_is_terminal_until_retry_contract_exists(self):
        task = Task(title="test", status="failed")

        with self.assertRaises(ValueError):
            transition_task(task, "pending")

    def test_pending_to_cancelled(self):
        task = Task(title="test")

        transition_task(task, "cancelled")

        self.assertEqual(task.status, "cancelled")

    def test_completed_is_terminal(self):
        task = Task(title="test", status="completed")

        with self.assertRaises(ValueError):
            transition_task(task, "running")

    def test_cancelled_is_terminal(self):
        task = Task(title="test", status="cancelled")

        with self.assertRaises(ValueError):
            transition_task(task, "running")

    def test_invalid_transition_raises(self):
        task = Task(title="test")

        with self.assertRaises(ValueError):
            transition_task(task, "completed")


if __name__ == "__main__":
    unittest.main()
