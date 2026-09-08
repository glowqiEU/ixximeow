import unittest

from unittest.mock import patch

from core.context_builder import build_context
from core.goals import Goal
from core.models import Task
from core.state import SystemState


class TestContextLineageContract(unittest.TestCase):
    def test_context_resolves_active_goal_and_task_objects(self):
        goal = Goal(
            title="grow audience",
            description="build a consistent audience",
            metrics=["weekly followers"],
            constraints=["preserve identity"],
            id="goal-1",
        )
        task = Task(
            title="create X content",
            goal_id=goal.id,
            id="task-1",
        )
        state = SystemState(
            active_goal_id=goal.id,
            active_task=task.id,
        )

        with patch("core.context_builder.get_goal", return_value=goal):
            context = build_context(
                state=state,
                memories=[],
                history=[],
                tasks=[task],
            )

        self.assertEqual(context.goal_id, goal.id)
        self.assertEqual(context.goal.id, goal.id)
        self.assertEqual(context.goal.description, goal.description)
        self.assertEqual(context.goal.metrics, goal.metrics)
        self.assertEqual(context.goal.constraints, goal.constraints)
        self.assertEqual(context.task.id, task.id)
        self.assertEqual(context.task.title, task.title)
        self.assertEqual(context.task.goal_id, goal.id)

    def test_context_rejects_stale_active_goal(self):
        state = SystemState(active_goal_id="missing-goal")

        with patch("core.context_builder.get_goal", return_value=None):
            with self.assertRaises(ValueError):
                build_context(
                    state=state,
                    memories=[],
                    history=[],
                    tasks=[],
                )

    def test_context_rejects_stale_active_task(self):
        state = SystemState(active_task="missing-task")

        with self.assertRaises(ValueError):
            build_context(
                state=state,
                memories=[],
                history=[],
                tasks=[],
            )

    def test_context_rejects_task_from_different_goal(self):
        goal = Goal(
            title="grow audience",
            description="build a consistent audience",
            id="goal-1",
        )
        task = Task(
            title="create X content",
            goal_id="goal-2",
            id="task-1",
        )
        state = SystemState(
            active_goal_id=goal.id,
            active_task=task.id,
        )

        with patch("core.context_builder.get_goal", return_value=goal):
            with self.assertRaises(ValueError):
                build_context(
                    state=state,
                    memories=[],
                    history=[],
                    tasks=[task],
                )


if __name__ == "__main__":
    unittest.main()
