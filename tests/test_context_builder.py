import unittest

from core.context_builder import AgentContext, build_context
from core.state import SystemState
from core.memory import Memory
from core.history import HistoryEvent
from core.models import Task


class TestContextBuilder(unittest.TestCase):

    def test_build_context_collects_system_context(self):
        state = SystemState(active_goal_id="goal-1")
        memories = [
            Memory(
                content="flash photos perform better",
                source="observed_result",
                confidence=0.8,
            )
        ]
        history = [
            HistoryEvent(
                event_type="task_executed",
                summary="posted photo",
            )
        ]
        tasks = [
            Task(
                title="post photo",
            )
        ]

        context = build_context(
            state=state,
            memories=memories,
            history=history,
            tasks=tasks,
        )

        self.assertIsInstance(context, AgentContext)
        self.assertEqual(context.state.active_goal_id, "goal-1")
        self.assertEqual(len(context.memories), 1)
        self.assertEqual(len(context.history), 1)
        self.assertEqual(len(context.tasks), 1)


if __name__ == "__main__":
    unittest.main()
