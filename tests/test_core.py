import unittest

from core.models import Decision
from core.decision_engine import choose_decision
from core.orchestrator import Orchestrator


class TestDecisionEngine(unittest.TestCase):

    def test_chooses_highest_priority(self):
        options = [
            Decision("test", "low", "low priority", priority=1),
            Decision("test", "high", "high priority", priority=10),
            Decision("test", "medium", "medium priority", priority=5),
        ]

        decision = choose_decision(options)

        self.assertEqual(decision.action, "high")
        self.assertEqual(decision.priority, 10)


class TestOrchestrator(unittest.TestCase):

    def test_decision_creates_task_and_result(self):
        options = [
            Decision("test", "first", "first option", priority=1),
            Decision("test", "best", "best option", priority=10),
        ]

        decision, task, result = Orchestrator().run(options)

        self.assertEqual(decision.action, "best")
        self.assertEqual(task.title, "best")
        self.assertTrue(result.success)
        self.assertEqual(result.summary, "task created: best")


if __name__ == "__main__":
    unittest.main()
