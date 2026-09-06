import unittest

from core.orchestrator import Orchestrator
from core.state_store import load_state
from core.history_store import load_events
from core.task_store import load_tasks


class TestOrchestratorIntegration(unittest.TestCase):
    def test_full_lifecycle_persists(self):
        decision, task, result = Orchestrator().run()

        self.assertIsNotNone(decision.id)
        self.assertIsNotNone(task.id)
        self.assertIsNotNone(result.id)

        self.assertEqual(task.decision_id, decision.id)
        self.assertEqual(result.task_id, task.id)
        self.assertEqual(task.status, "completed")
        self.assertTrue(result.success)

        state = load_state()

        self.assertEqual(state.last_decision_id, decision.id)
        self.assertEqual(state.last_result_id, result.id)
        self.assertIsNone(state.active_task)

        tasks = load_tasks()
        self.assertTrue(any(item.id == task.id for item in tasks))

        history = load_events()
        self.assertTrue(
            any(
                event.task_id == task.id
                and event.result_id == result.id
                and event.decision_id == decision.id
                for event in history
            )
        )


if __name__ == "__main__":
    unittest.main()
