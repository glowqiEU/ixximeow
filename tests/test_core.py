import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.models import Decision, Task
from core.decision_engine import choose_decision
from core.executor import execute_task
from core.goal_store import get_goal, load_goals, save_goals
from core.goals import Goal
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
        self.assertIsNotNone(decision.id)


class TestExecutor(unittest.TestCase):
    def test_execute_task_returns_result(self):
        task = Task(title="test task", id="task-1")

        with patch("core.agent_config.CURRENT_AUTONOMY_LEVEL", 3):
            task, result = execute_task(task)

        self.assertEqual(result.task_id, "task-1")
        self.assertTrue(result.success)
        self.assertEqual(result.summary, "task execution completed")


class TestOrchestrator(unittest.TestCase):
    def test_run_produces_decision(self):
        with patch("core.agent_config.CURRENT_AUTONOMY_LEVEL", 3):
            decision, task, result = Orchestrator().run()

        self.assertIsNotNone(decision)
        self.assertIsNotNone(decision.id)
        self.assertEqual(decision.status, "proposed")


class TestGoalStore(unittest.TestCase):
    def test_loads_existing_goal(self):
        goal = Goal(
            title="grow ixximeow",
            description="test goal",
        )

        with tempfile.TemporaryDirectory() as directory:
            goals_file = Path(directory) / "goals.json"
            with patch("core.goal_store.GOALS_FILE", goals_file):
                save_goals([goal])
                goals = load_goals()

        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0].title, "grow ixximeow")
        self.assertEqual(goals[0].id, goal.id)

    def test_get_goal_returns_matching_goal(self):
        goal = Goal(
            title="grow ixximeow",
            description="test goal",
        )

        with tempfile.TemporaryDirectory() as directory:
            goals_file = Path(directory) / "goals.json"
            with patch("core.goal_store.GOALS_FILE", goals_file):
                save_goals([goal])
                loaded_goal = get_goal(goal.id)

        self.assertIsNotNone(loaded_goal)
        self.assertEqual(loaded_goal.title, "grow ixximeow")


if __name__ == "__main__":
    unittest.main()
