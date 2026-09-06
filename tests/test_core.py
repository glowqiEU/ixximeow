import unittest

from core.models import Decision
from core.decision_engine import choose_decision
from core.orchestrator import Orchestrator


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


class TestOrchestrator(unittest.TestCase):
    def test_run_produces_decision(self):
        decision, task = Orchestrator().run()

        self.assertIsNotNone(decision)
        self.assertIsNotNone(decision.id)
        self.assertEqual(decision.status, 'proposed')


if __name__ == '__main__':
    unittest.main()
