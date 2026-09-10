import unittest
from unittest.mock import patch

from core.action import Action
from core.action_registry import ActionRegistry
from core.context import AgentContext
from core.decision import Decision
from core.execution import Execution
from core.state import SystemState
from core.models import Task
from core.orchestrator_v2 import OrchestratorV2


class TestOrchestratorUncertainExecution(unittest.TestCase):
    def test_uncertain_execution_moves_task_out_of_running_without_false_result(self):
        decision = Decision(
            objective="publish the post",
            action="publish_post",
            reason="selected action",
            goal_id="goal-1",
        )
        task = Task(
            title="publish",
            decision_id=decision.id,
            goal_id="goal-1",
            action_id="action-1",
            status="running",
            id="task-1",
        )
        action = Action(
            task_id=task.id,
            name="publish_post",
            id="action-1",
        )
        execution = Execution(
            action_id=action.id,
            task_id=task.id,
            status="uncertain",
            attempt=1,
            id="execution-1",
        )
        state = SystemState(active_task=task.id, last_decision_id=decision.id)
        registry = ActionRegistry()
        orchestrator = OrchestratorV2(registry)

        with patch(
            "core.orchestrator_v2.execute_reserved_action",
            return_value=(execution, None, []),
        ), patch("core.orchestrator_v2.save_tasks"), patch(
            "core.orchestrator_v2.save_state"
        ), patch("core.orchestrator_v2.append_event"):
            updated_task, result = orchestrator._finalize(
                task,
                decision,
                action,
                execution,
                state,
                [task],
            )

        self.assertEqual(updated_task.status, "uncertain")
        self.assertIsNone(result)
        self.assertIsNone(state.active_task)
        self.assertIsNone(state.last_result_id)


if __name__ == "__main__":
    unittest.main()
