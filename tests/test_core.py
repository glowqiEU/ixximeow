import unittest

from core.models import Decision
from core.decision_engine import choose_decision
from core.orchestrator import Orchestrator
from core.executor import execute_task
from core.models import Task


class TestDecisionEngine(unittest.TestCase):
    def test_chooses_highest_priority(self):
        options = [
            Decision('test', 'low', 'low priority', priority=1),
            Decision('test', 'high', 'high priority', priority=10),
            Decision('test', 'medium', 'medium priority', priority=5),
        ]

        decision = choose_decision(options)

        self.assertEqual(decision.action, 'high')
        self.assertEqual(decision.priority, 10)
        self.assertIsNotNone(decision.id)



class TestExecutor(unittest.TestCase):
    def test_execute_task_returns_result(self):
        task = Task(title="test task", id="task-1")

        result = execute_task(task)

        self.assertEqual(result.task_id, "task-1")
        self.assertFalse(result.success)
        self.assertEqual(result.summary, "execution not implemented yet")


class TestOrchestrator(unittest.TestCase):
    def test_run_produces_decision(self):
        decision, task, result = Orchestrator().run()

        self.assertIsNotNone(decision)
        self.assertIsNotNone(decision.id)
        self.assertEqual(decision.status, 'proposed')


if __name__ == '__main__':
    unittest.main()
