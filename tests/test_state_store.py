import unittest

from core import state_store
from core.state import SystemState


class TestStateStore(unittest.TestCase):
    def test_save_and_load_state(self):
        original_file = state_store.STATE_FILE

        try:
            state_store.STATE_FILE = original_file.parent / "test_state.json"
            state_store.STATE_FILE.unlink(missing_ok=True)

            state = SystemState(
                active_goal_id="goal-123",
                active_task="build agent",
                last_decision_id="decision-123",
                last_result_id="result-123",
            )

            state_store.save_state(state)
            loaded = state_store.load_state()

            self.assertEqual(loaded.active_goal_id, "goal-123")
            self.assertEqual(loaded.active_task, "build agent")
            self.assertEqual(loaded.last_decision_id, "decision-123")
            self.assertEqual(loaded.last_result_id, "result-123")

        finally:
            state_store.STATE_FILE.unlink(missing_ok=True)
            state_store.STATE_FILE = original_file


if __name__ == "__main__":
    unittest.main()
