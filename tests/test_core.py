import unittest

from core.models import Decision
from core.decision_engine import choose_decision
from core.orchestrator import Orchestrator
from core.executor import execute_task
from core.models import Task


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



class TestExecutor(unittest.TestCase):
    def test_execute_task_returns_result(self):
        task = Task(title="test task", id="task-1")

        task, result = execute_task(task)

        self.assertEqual(result.task_id, "task-1")
        self.assertTrue(result.success)
        self.assertEqual(result.summary, "task execution completed")


class TestOrchestrator(unittest.TestCase):
    def test_run_produces_decision(self):
        decision, task, result = Orchestrator().run()

        self.assertIsNotNone(decision)
        self.assertIsNotNone(decision.id)
        self.assertEqual(decision.status, 'proposed')


if __name__ == '__main__':
    unittest.main()

from core.goal_store import get_goal, load_goals


class TestGoalStore(unittest.TestCase):
    def test_loads_existing_goal(self):
        goals = load_goals()

        self.assertTrue(goals)
        self.assertEqual(goals[0].title, "grow ixximeow")

    def test_get_goal_returns_matching_goal(self):
        goals = load_goals()
        goal = get_goal(goals[0].id)

        self.assertIsNotNone(goal)
        self.assertEqual(goal.title, "grow ixximeow")
