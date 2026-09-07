import unittest
from unittest.mock import patch

from core.context_builder import build_context
from core.state import SystemState
from core.history import HistoryEvent


class TestContextBuilder(unittest.TestCase):
    @patch("core.context_builder.load_events")
    @patch("core.context_builder.load_state")
    def test_build_context_restores_state_and_history(
        self,
        mock_load_state,
        mock_load_events,
    ):
        mock_load_state.return_value = SystemState(
            active_goal_id="goal-123",
            active_task="build agent",
            last_decision_id="decision-123",
            last_result_id="result-123",
        )

        history = [
            HistoryEvent(
                event_type="task_executed",
                summary="task execution completed",
                decision_id="decision-123",
                task_id="task-123",
                result_id="result-123",
            )
        ]
        mock_load_events.return_value = history

        context, recent_history = build_context(history_limit=10)

        self.assertEqual(context.goal_id, "goal-123")
        self.assertEqual(context.task, "build agent")
        self.assertEqual(context.last_decision_id, "decision-123")
        self.assertEqual(context.last_result_id, "result-123")
        self.assertEqual(recent_history, history)
        mock_load_events.assert_called_once_with(limit=10)


if __name__ == "__main__":
    unittest.main()
