import unittest
from unittest.mock import patch

from core.action_registry import ActionRegistry
from core.approval import Approval
from core.context import AgentContext
from core.decision_evaluation import DecisionEvaluation
from core.evidence import Evidence
from core.execution import Execution
from core.models import Decision, Result, Task
from core.orchestrator import Orchestrator
from core.state import SystemState


class TestOrchestratorIntegration(unittest.TestCase):
    def _registry(self):
        registry = ActionRegistry()
        registry.register(
            "publish_post",
            lambda action: {
                "summary": "published",
                "evidence": [
                    {
                        "claim": "post_published",
                        "kind": "execution_output",
                        "value": True,
                        "content": "the post was published",
                        "verified": True,
                    }
                ],
            },
        )
        return registry

    def test_full_lifecycle_resolves_achieved_from_evidence(self):
        context = AgentContext(goal_id="goal-1", task=None)
        decision = Decision(
            objective="publish the post",
            action="publish_post",
            reason="selected action",
            goal_id="goal-1",
            criteria=[
                {
                    "claim": "post_published",
                    "kind": "boolean",
                    "expected": True,
                }
            ],
        )
        state = SystemState(active_goal_id="goal-1")
        task_store = []

        execution = Execution(action_id="action-1", task_id="task-1")
        execution.transition("running")
        execution.transition("succeeded")
        result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id=execution.id,
            success=True,
            summary="published",
        )
        evidence = Evidence(
            result_id=result.id,
            execution_id=execution.id,
            kind="execution_output",
            claim="post_published",
            value=True,
            content="the post was published",
            verified=True,
        )

        with patch("core.approval_gate.CURRENT_AUTONOMY_LEVEL", "execute"), \
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
             patch("core.orchestrator_v2.load_tasks", return_value=task_store), \
             patch("core.orchestrator_v2.save_tasks"), \
             patch("core.orchestrator_v2.load_state", return_value=state), \
             patch("core.orchestrator_v2.save_state"), \
             patch("core.orchestrator_v2.check_approval", return_value=None), \
             patch("core.orchestrator_v2.execute_action", return_value=(execution, result, [evidence])), \
             patch("core.orchestrator_v2.upsert_evidence"), \
             patch("core.orchestrator_v2.upsert_outcome"), \
             patch("core.orchestrator_v2.append_event"), \
             patch("core.orchestrator_v2.apply_decision", return_value=state), \
             patch("core.orchestrator_v2.apply_result", return_value=state):
            decision_result, task, result_result = Orchestrator(self._registry()).run()

        self.assertEqual(decision_result.id, decision.id)
        self.assertEqual(task.action_id, "action-1")
        self.assertEqual(task.status, "completed")
        self.assertEqual(result_result.id, result.id)

    def test_successful_execution_without_objective_evidence_is_uncertain(self):
        context = AgentContext(goal_id="goal-1", task=None)
        decision = Decision(
            objective="post published",
            action="publish_post",
            reason="selected action",
            goal_id="goal-1",
            criteria=[
                {
                    "claim": "post_published",
                    "kind": "boolean",
                    "expected": True,
                }
            ],
        )
        state = SystemState(active_goal_id="goal-1")
        execution = Execution(action_id="action-1", task_id="task-1")
        execution.transition("running")
        execution.transition("succeeded")
        result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id=execution.id,
            success=True,
            summary="handler completed",
        )
        evidence = Evidence(
            result_id=result.id,
            execution_id=execution.id,
            kind="execution_output",
            claim="execution_succeeded",
            value=True,
            content="handler completed",
            verified=True,
        )

        with patch("core.approval_gate.CURRENT_AUTONOMY_LEVEL", "execute"), \
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
             patch("core.orchestrator_v2.save_tasks"), \
             patch("core.orchestrator_v2.load_state", return_value=state), \
             patch("core.orchestrator_v2.save_state"), \
             patch("core.orchestrator_v2.check_approval", return_value=None), \
             patch("core.orchestrator_v2.execute_action", return_value=(execution, result, [evidence])), \
             patch("core.orchestrator_v2.upsert_evidence"), \
             patch("core.orchestrator_v2.upsert_outcome"), \
             patch("core.orchestrator_v2.append_event"), \
             patch("core.orchestrator_v2.apply_decision", return_value=state), \
             patch("core.orchestrator_v2.apply_result", return_value=state):
            _, task, _ = Orchestrator(self._registry()).run()

        self.assertEqual(task.status, "uncertain")

    def test_approval_is_waiting_state_not_blocked_outcome(self):
        context = AgentContext(goal_id="goal-1", task=None)
        decision = Decision(
            objective="publish the post",
            action="publish_post",
            reason="selected action",
            goal_id="goal-1",
            criteria=[
                {
                    "claim": "post_published",
                    "kind": "boolean",
                    "expected": True,
                }
            ],
        )
        state = SystemState(active_goal_id="goal-1")
        approval = Approval(
            action_id="action-1",
            task_id="task-1",
            required_level="publish",
            reason="publishing requires approval",
        )

        with patch("core.orchestrator_v2.build_context", return_value=context), \
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
             patch("core.orchestrator_v2.save_tasks"), \
             patch("core.orchestrator_v2.load_state", return_value=state), \
             patch("core.orchestrator_v2.save_state"), \
             patch("core.orchestrator_v2.check_approval", return_value=approval), \
             patch("core.orchestrator_v2.save_approvals"), \
             patch("core.orchestrator_v2.load_approvals", return_value=[]), \
             patch("core.orchestrator_v2.append_event"), \
             patch("core.orchestrator_v2.apply_decision", return_value=state):
            _, task, result = Orchestrator(self._registry()).run()

        self.assertEqual(task.status, "waiting_approval")
        self.assertEqual(task.approval_id, approval.id)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
