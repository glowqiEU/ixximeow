import unittest

from core.context import AgentContext
from core.planner import generate_candidates


class TestPlanner(unittest.TestCase):
    def test_active_task_has_highest_priority(self):
        context = AgentContext(goal_id="goal-1", task="build agent")

        candidates = generate_candidates(context)

        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0].action, "continue: build agent")
        self.assertEqual(candidates[0].priority, 10)

    def test_goal_without_task_creates_review_candidate(self):
        context = AgentContext(goal_id="goal-1", task=None)

        candidates = generate_candidates(context)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].action, "review next useful action")
        self.assertEqual(candidates[0].priority, 5)

    def test_empty_context_creates_inspection_candidate(self):
        context = AgentContext()

        candidates = generate_candidates(context)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].action, "inspect current state")
        self.assertEqual(candidates[0].priority, 1)


if __name__ == "__main__":
    unittest.main()
