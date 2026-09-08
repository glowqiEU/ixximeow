import unittest
from unittest.mock import patch

from core.orchestrator import Orchestrator
from core.context import AgentContext
from core.state_store import load_state
from core.history_store import load_events
from core.task_store import load_tasks
from core.permissions import AutonomyLevel
from core.memory import Memory


class TestOrchestratorIntegration(unittest.TestCase):
    def test_full_lifecycle_persists(self):
        with patch(
            "core.approval_gate.CURRENT_AUTONOMY_LEVEL",
            AutonomyLevel.EXECUTE,
        ):
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

        self.assertTrue(
            any(item.id == task.id for item in tasks)
        )

        history = load_events()

        self.assertTrue(
            any(
                event.task_id == task.id
                and event.result_id == result.id
                and event.decision_id == decision.id
                for event in history
            )
        )


    def test_orchestrator_builds_context_with_memory_query(self):
        context = AgentContext(
            goal_id="goal-1",
            task="create X content",
        )

        with patch("core.orchestrator.build_context", side_effect=[
            context,
            AgentContext(
                goal_id="goal-1",
                task="create X content",
                memories=[
                    Memory(
                        content="flash photos perform better",
                        source="observed_result",
                        confidence=0.8,
                    )
                ],
            ),
        ]) as mock_build_context:
            with patch(
                "core.approval_gate.CURRENT_AUTONOMY_LEVEL",
                AutonomyLevel.EXECUTE,
            ):
                Orchestrator().run()

        self.assertEqual(mock_build_context.call_count, 2)
        self.assertEqual(
            mock_build_context.call_args.kwargs["query"],
            "create X content",
        )

if __name__ == "__main__":
    unittest.main()
