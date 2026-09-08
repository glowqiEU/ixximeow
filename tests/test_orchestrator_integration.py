import unittest
from unittest.mock import patch

from core.orchestrator import Orchestrator
from core.context import AgentContext
from core.decision_evaluation import DecisionEvaluation
from core.state_store import load_state
from core.history_store import load_events
from core.task_store import load_tasks
from core.permissions import AutonomyLevel
from core.memory import Memory
from core.state import SystemState


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
        self.assertEqual(task.goal_id, decision.goal_id)
        self.assertEqual(result.task_id, task.id)
        self.assertEqual(task.status, "completed")
        self.assertTrue(result.success)

        state = load_state()

        self.assertEqual(state.last_decision_id, decision.id)
        self.assertEqual(state.last_result_id, result.id)
        self.assertIsNone(state.active_task)

        tasks = load_tasks()

        persisted_task = next(
            item for item in tasks if item.id == task.id
        )

        self.assertEqual(persisted_task.status, "completed")
        self.assertEqual(persisted_task.decision_id, decision.id)
        self.assertEqual(persisted_task.goal_id, decision.goal_id)

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

    def test_orchestrator_evaluates_candidates_before_selection(self):
        context = AgentContext(
            goal_id="goal-1",
            task="create X content",
        )

        low = DecisionEvaluation(
            decision_id="low",
            relevance=0.4,
            confidence=0.4,
            risk=0.6,
            effort=0.6,
            reason="lower utility",
        )
        high = DecisionEvaluation(
            decision_id="high",
            relevance=0.9,
            confidence=0.9,
            risk=0.1,
            effort=0.1,
            reason="higher utility",
        )

        with patch("core.orchestrator.build_context", return_value=context):
            with patch("core.orchestrator.generate_candidates") as mock_candidates:
                first = type(
                    "DecisionLike",
                    (),
                    {"id": "low", "action": "low action", "goal_id": "goal-1"},
                )()
                second = type(
                    "DecisionLike",
                    (),
                    {"id": "high", "action": "high action", "goal_id": "goal-1"},
                )()
                mock_candidates.return_value = [first, second]

                with patch(
                    "core.orchestrator.evaluate_decision",
                    side_effect=[low, high],
                ) as mock_evaluate:
                    with patch(
                        "core.orchestrator.select_decision",
                        return_value=second,
                    ) as mock_select:
                        with patch("core.orchestrator.load_tasks", return_value=[]), \
                             patch("core.orchestrator.save_tasks"), \
                             patch(
                                 "core.orchestrator.load_state",
                                 return_value=SystemState(active_goal_id="goal-1"),
                             ), \
                             patch("core.orchestrator.save_state"), \
                             patch("core.orchestrator.check_approval", return_value=None), \
                             patch("core.orchestrator.execute_task") as mock_execute:
                            mock_execute.return_value = (
                                type("TaskLike", (), {"id": "task-1", "status": "completed"})(),
                                type("ResultLike", (), {"id": "result-1", "summary": "done"})(),
                            )
                            with patch("core.orchestrator.append_event"), \
                                 patch("core.orchestrator.apply_decision", return_value=SystemState()), \
                                 patch("core.orchestrator.apply_result", return_value=SystemState()):
                                Orchestrator().run()

        self.assertEqual(mock_evaluate.call_count, 2)
        self.assertEqual(
            [call.args[0].id for call in mock_evaluate.call_args_list],
            ["low", "high"],
        )
        mock_select.assert_called_once_with([first, second], [low, high])


if __name__ == "__main__":
    unittest.main()
