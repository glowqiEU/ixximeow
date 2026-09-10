import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from core.action_registry import ActionRegistry
from core.context import AgentContext
from core.decision_evaluation import DecisionEvaluation
from core.execution_store import load_executions
from core.models import Decision
from core.orchestrator import Orchestrator
from core.state import SystemState
from core.task_store import load_tasks, save_tasks as persist_tasks


class TestOrchestratorCrashBoundary(unittest.TestCase):
    def test_crash_after_reservation_before_task_running_persists_safe_pending_state(self):
        context = AgentContext(goal_id="goal-1", task=None)
        decision = Decision(
            objective="publish the post",
            action="publish_post",
            reason="selected action",
            goal_id="goal-1",
            criteria=[
                {"claim": "post_published", "kind": "boolean", "expected": True}
            ],
        )
        state = SystemState(active_goal_id="goal-1")
        registry = ActionRegistry()
        handler_calls = []

        def handler(action):
            handler_calls.append(action.id)
            return {"summary": "published"}

        registry.register("publish_post", handler)

        with TemporaryDirectory() as directory:
            root = Path(directory)
            save_calls = 0

            def save_tasks_then_crash(tasks):
                nonlocal save_calls
                save_calls += 1
                if save_calls == 3:
                    raise RuntimeError("simulated crash")
                persist_tasks(tasks)

            with patch("core.execution_store.EXECUTIONS_FILE", root / "executions.json"), \
                 patch("core.task_store.TASKS_FILE", root / "tasks.json"), \
                 patch("core.orchestrator_v2.build_context", return_value=context), \
                 patch("core.orchestrator_v2.generate_candidates", return_value=[decision]), \
                 patch("core.orchestrator_v2.evaluate_decision", return_value=DecisionEvaluation(
                     decision_id=decision.id,
                     relevance=1.0,
                     confidence=1.0,
                     risk=0.0,
                     effort=0.0,
                     reason="strong candidate",
                 )), \
                 patch("core.orchestrator_v2.select_decision", return_value=decision), \
                 patch("core.orchestrator_v2.load_decisions", return_value=[]), \
                 patch("core.orchestrator_v2.save_decisions"), \
                 patch("core.orchestrator_v2.load_plans", return_value=[]), \
                 patch("core.orchestrator_v2.save_plans"), \
                 patch("core.orchestrator_v2.load_tasks", return_value=[]), \
                 patch("core.orchestrator_v2.check_approval", return_value=None), \
                 patch("core.orchestrator_v2.upsert_evidence"), \
                 patch("core.orchestrator_v2.upsert_outcome"), \
                 patch("core.orchestrator_v2.append_event"), \
                 patch("core.orchestrator_v2.apply_decision", return_value=state), \
                 patch("core.orchestrator_v2.apply_result", return_value=state), \
                 patch("core.orchestrator_v2.save_state"), \
                 patch("core.orchestrator_v2.save_tasks", side_effect=save_tasks_then_crash), \
                 patch("core.orchestrator_v2.execute_reserved_action") as execute:
                with self.assertRaises(RuntimeError):
                    Orchestrator(registry).run()

                persisted_tasks = load_tasks()
                persisted_executions = load_executions()

            self.assertEqual(save_calls, 3)
            self.assertEqual(len(persisted_tasks), 1)
            self.assertEqual(persisted_tasks[0].status, "pending")
            self.assertIsNotNone(persisted_tasks[0].action_id)
            self.assertEqual(len(persisted_executions), 1)
            self.assertEqual(persisted_executions[0].status, "pending")
            self.assertEqual(persisted_executions[0].task_id, persisted_tasks[0].id)
            self.assertEqual(persisted_executions[0].action_id, persisted_tasks[0].action_id)
            execute.assert_not_called()
            self.assertEqual(handler_calls, [])


if __name__ == "__main__":
    unittest.main()
