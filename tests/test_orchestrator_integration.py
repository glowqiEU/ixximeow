import unittest
from unittest.mock import patch

from core.action_registry import ActionRegistry
from core.approval import Approval
from core.context import AgentContext
from core.decision_evaluation import DecisionEvaluation
from core.evidence import Evidence
from core.execution import Execution
from core.models import Decision, Result
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

    def _decision(self):
        return Decision(
            objective="publish the post",
            action="publish_post",
            reason="selected action",
            goal_id="goal-1",
            criteria=[
                {"claim": "post_published", "kind": "boolean", "expected": True}
            ],
        )

    def _patches(self, context, decision, state, execute_result, check_approval):
        return [
            patch("core.orchestrator_v2.build_context", return_value=context),
            patch("core.orchestrator_v2.generate_candidates", return_value=[decision]),
            patch(
                "core.orchestrator_v2.evaluate_decision",
                return_value=DecisionEvaluation(
                    decision_id=decision.id,
                    relevance=1.0,
                    confidence=1.0,
                    risk=0.0,
                    effort=0.0,
                    reason="strong candidate",
                ),
            ),
            patch("core.orchestrator_v2.select_decision", return_value=decision),
            patch("core.orchestrator_v2.load_decisions", return_value=[]),
            patch("core.orchestrator_v2.save_decisions"),
            patch("core.orchestrator_v2.load_plans", return_value=[]),
            patch("core.orchestrator_v2.save_plans"),
            patch("core.orchestrator_v2.load_tasks", return_value=[]),
            patch("core.orchestrator_v2.save_tasks"),
            patch("core.orchestrator_v2.load_state", return_value=state),
            patch("core.orchestrator_v2.save_state"),
            patch("core.orchestrator_v2.check_approval", side_effect=check_approval),
            patch("core.orchestrator_v2.execute_action", return_value=execute_result),
            patch("core.orchestrator_v2.upsert_evidence"),
            patch("core.orchestrator_v2.upsert_outcome"),
            patch("core.orchestrator_v2.append_event"),
            patch("core.orchestrator_v2.apply_decision", return_value=state),
            patch("core.orchestrator_v2.apply_result", return_value=state),
        ]

    def _execute_with_evidence(self, action, claim, value, content):
        execution = Execution(action_id=action.id, task_id=action.task_id)
        execution.transition("running")
        execution.transition("succeeded")
        result = Result(
            task_id=action.task_id,
            action_id=action.id,
            execution_id=execution.id,
            success=True,
            summary="published",
        )
        evidence = Evidence(
            result_id=result.id,
            execution_id=execution.id,
            kind="execution_output",
            claim=claim,
            value=value,
            content=content,
            verified=True,
        )
        return execution, result, [evidence]

    def test_full_lifecycle_resolves_achieved_from_evidence(self):
        context = AgentContext(goal_id="goal-1", task=None)
        decision = self._decision()
        state = SystemState(active_goal_id="goal-1")

        def execute_result(action, registry):
            return self._execute_with_evidence(
                action, "post_published", True, "the post was published"
            )

        with patch("core.orchestrator_v2.execute_action", side_effect=execute_result), \
             patch("core.orchestrator_v2.build_context", return_value=context), \
             patch("core.orchestrator_v2.generate_candidates", return_value=[decision]), \
             patch("core.orchestrator_v2.evaluate_decision", return_value=DecisionEvaluation(
                 decision_id=decision.id, relevance=1.0, confidence=1.0,
                 risk=0.0, effort=0.0, reason="strong candidate",
             )), \
             patch("core.orchestrator_v2.select_decision", return_value=decision), \
             patch("core.orchestrator_v2.load_decisions", return_value=[]), \
             patch("core.orchestrator_v2.save_decisions"), \
             patch("core.orchestrator_v2.load_plans", return_value=[]), \
             patch("core.orchestrator_v2.save_plans"), \
             patch("core.orchestrator_v2.load_tasks", return_value=[]), \
             patch("core.orchestrator_v2.save_tasks"), \
             patch("core.orchestrator_v2.load_state", return_value=state), \
             patch("core.orchestrator_v2.check_approval", return_value=None), \
             patch("core.orchestrator_v2.upsert_evidence"), \
             patch("core.orchestrator_v2.upsert_outcome"), \
             patch("core.orchestrator_v2.append_event"), \
             patch("core.orchestrator_v2.apply_decision", return_value=state), \
             patch("core.orchestrator_v2.apply_result", return_value=state):
            task, result_result = Orchestrator(self._registry()).run()

        self.assertEqual(task.decision_id, decision.id)
        self.assertIsNotNone(task.action_id)
        self.assertEqual(task.status, "completed")
        self.assertEqual(result_result.task_id, task.id)
        self.assertEqual(result_result.action_id, task.action_id)

    def test_successful_execution_without_objective_evidence_is_uncertain(self):
        context = AgentContext(goal_id="goal-1", task=None)
        decision = self._decision()
        state = SystemState(active_goal_id="goal-1")

        def execute_without_objective_evidence(action, registry):
            return self._execute_with_evidence(
                action, "execution_succeeded", True, "handler completed"
            )

        with patch("core.orchestrator_v2.execute_action", side_effect=execute_without_objective_evidence), \
             patch("core.orchestrator_v2.build_context", return_value=context), \
             patch("core.orchestrator_v2.generate_candidates", return_value=[decision]), \
             patch("core.orchestrator_v2.evaluate_decision", return_value=DecisionEvaluation(
                 decision_id=decision.id, relevance=1.0, confidence=1.0,
                 risk=0.0, effort=0.0, reason="strong candidate",
             )), \
             patch("core.orchestrator_v2.select_decision", return_value=decision), \
             patch("core.orchestrator_v2.load_decisions", return_value=[]), \
             patch("core.orchestrator_v2.save_decisions"), \
             patch("core.orchestrator_v2.load_plans", return_value=[]), \
             patch("core.orchestrator_v2.save_plans"), \
             patch("core.orchestrator_v2.load_tasks", return_value=[]), \
             patch("core.orchestrator_v2.save_tasks"), \
             patch("core.orchestrator_v2.load_state", return_value=state), \
             patch("core.orchestrator_v2.check_approval", return_value=None), \
             patch("core.orchestrator_v2.upsert_evidence"), \
             patch("core.orchestrator_v2.upsert_outcome"), \
             patch("core.orchestrator_v2.append_event"), \
             patch("core.orchestrator_v2.apply_decision", return_value=state), \
             patch("core.orchestrator_v2.apply_result", return_value=state):
            task, result_result = Orchestrator(self._registry()).run()

        self.assertEqual(task.status, "uncertain")
        self.assertIsNotNone(result_result)
        self.assertEqual(result_result.task_id, task.id)

    def test_approval_is_waiting_state_not_blocked_outcome(self):
        context = AgentContext(goal_id="goal-1", task=None)
        decision = self._decision()
        state = SystemState(active_goal_id="goal-1")
        approval = Approval(
            action_id="placeholder", task_id="placeholder",
            required_level="publish", reason="publishing requires approval",
        )

        def make_approval(action):
            approval.action_id = action.id
            approval.task_id = action.task_id
            return approval

        with patch("core.orchestrator_v2.build_context", return_value=context), \
             patch("core.orchestrator_v2.generate_candidates", return_value=[decision]), \
             patch("core.orchestrator_v2.evaluate_decision", return_value=DecisionEvaluation(
                 decision_id=decision.id, relevance=1.0, confidence=1.0,
                 risk=0.0, effort=0.0, reason="strong candidate",
             )), \
             patch("core.orchestrator_v2.select_decision", return_value=decision), \
             patch("core.orchestrator_v2.load_decisions", return_value=[]), \
             patch("core.orchestrator_v2.save_decisions"), \
             patch("core.orchestrator_v2.load_plans", return_value=[]), \
             patch("core.orchestrator_v2.save_plans"), \
             patch("core.orchestrator_v2.load_tasks", return_value=[]), \
             patch("core.orchestrator_v2.save_tasks"), \
             patch("core.orchestrator_v2.load_state", return_value=state), \
             patch("core.orchestrator_v2.check_approval", side_effect=make_approval), \
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
