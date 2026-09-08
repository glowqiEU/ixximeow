import unittest

from core.context import AgentContext
from core.memory import Memory
from core.models import Task
from core.planner import generate_candidates


class TestPlannerContract(unittest.TestCase):
    def test_active_task_uses_task_title_not_id(self):
        task = Task(title="build agent", id="task-123")
        context = AgentContext(goal_id="goal-1", task=task)

        candidates = generate_candidates(context)

        self.assertEqual(candidates[0].action, "continue: build agent")
        self.assertNotIn(task.id, candidates[0].action)

    def test_active_task_can_use_relevant_memory(self):
        task = Task(title="create X content", id="task-1")
        context = AgentContext(
            goal_id="goal-1",
            task=task,
            memories=[
                Memory(
                    content="flash photos perform better",
                    source="observed_result",
                    confidence=0.8,
                )
            ],
        )

        candidates = generate_candidates(context)

        self.assertIn("flash photos perform better", candidates[0].reason)


if __name__ == "__main__":
    unittest.main()
