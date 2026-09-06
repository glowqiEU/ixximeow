import unittest

from core.models import Decision, Result, Task
from core.state import SystemState
from core.state_manager import apply_decision, apply_result


class TestStateManager(unittest.TestCase):
    def test_apply_decision_updates_state(self):
        state = SystemState()
        decision = Decision("grow", "post", "best option")
        task = Task("post", decision_id=decision.id)

        state = apply_decision(state, decision, task)

        self.assertEqual(state.active_task, task.id)
        self.assertEqual(state.last_decision_id, decision.id)
        self.assertIsNone(state.last_result_id)

    def test_apply_result_clears_active_task(self):
        state = SystemState(active_task="task-1", last_decision_id="decision-1")
        task = Task("post", id="task-1")
        result = Result("task-1", True, "done")

        state = apply_result(state, task, result)

        self.assertIsNone(state.active_task)
        self.assertEqual(state.last_result_id, result.id)


if __name__ == "__main__":
    unittest.main()
