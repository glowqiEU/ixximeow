import unittest
from contextlib import ExitStack
from unittest.mock import patch

from core.action import Action
from core.action_registry import ActionRegistry
from core.approval import Approval
from core.models import Decision, Task
from core.orchestrator import Orchestrator


class TestApprovalActionSnapshot(unittest.TestCase):
    def test_approved_action_is_resumed_from_snapshot_not_current_decision(self):
        orchestrator = Orchestrator(ActionRegistry())
        task = Task(
            title="publish post",
            status="waiting_approval",
            decision_id="decision-1",
            action_id="action-1",
            approval_id="approval-1",
            required_level="publish",
            id="task-1",
        )
        approval = Approval(
            action_id="action-1",
            task_id="task-1",
            required_level="publish",
            reason="publishing requires approval",
            id="approval-1",
            status="approved",
        )
        original_action = Action(
            id="action-1",
            task_id="task-1",
            name="publish_post",
            input={"text": "approved payload"},
            permission_level="publish",
        )
        mutated_decision = Decision(
            id="decision-1",
            objective="publish the post",
            action="delete_post",
            reason="mutated after approval",
        )

        captured = {}

        def finalize(task_arg, decision_arg, action_arg, execution_arg, state_arg, tasks_arg):
            captured["decision"] = decision_arg
            captured["action"] = action_arg
            captured["execution"] = execution_arg
            return task_arg, None

        with ExitStack() as stack:
            stack.enter_context(patch("core.orchestrator.load_approvals", return_value=[approval]))
            stack.enter_context(patch("core.orchestrator.load_tasks", return_value=[task]))
            stack.enter_context(patch("core.orchestrator.load_decisions", return_value=[mutated_decision]))
            stack.enter_context(patch("core.orchestrator.find_action_by_id", return_value=original_action))
            stack.enter_context(patch("core.orchestrator.transition_task", side_effect=lambda item, status: item))
            stack.enter_context(patch("core.orchestrator.save_tasks"))
            stack.enter_context(patch("core.orchestrator.save_approvals"))
            stack.enter_context(patch("core.orchestrator.reserve_execution", return_value=object()))
            stack.enter_context(patch.object(orchestrator, "_finalize", side_effect=finalize))
            orchestrator.resume_approval("approval-1")

        self.assertEqual(captured["decision"].action, "delete_post")
        self.assertEqual(captured["action"].name, "publish_post")
        self.assertEqual(captured["action"].input, {"text": "approved payload"})
        self.assertEqual(captured["action"].id, "action-1")
        self.assertIsNotNone(captured["execution"])

    def test_resume_rejects_snapshot_permission_mismatch(self):
        orchestrator = Orchestrator(ActionRegistry())
        task = Task(
            title="publish post",
            status="waiting_approval",
            decision_id="decision-1",
            action_id="action-1",
            approval_id="approval-1",
            required_level="publish",
            id="task-1",
        )
        approval = Approval(
            action_id="action-1",
            task_id="task-1",
            required_level="publish",
            reason="publishing requires approval",
            id="approval-1",
            status="approved",
        )
        action = Action(
            id="action-1",
            task_id="task-1",
            name="publish_post",
            permission_level="execute",
        )
        decision = Decision(
            id="decision-1",
            objective="publish the post",
            action="publish_post",
            reason="selected action",
        )

        with ExitStack() as stack:
            stack.enter_context(patch("core.orchestrator.load_approvals", return_value=[approval]))
            stack.enter_context(patch("core.orchestrator.load_tasks", return_value=[task]))
            stack.enter_context(patch("core.orchestrator.load_decisions", return_value=[decision]))
            stack.enter_context(patch("core.orchestrator.find_action_by_id", return_value=action))
            with self.assertRaises(ValueError):
                orchestrator.resume_approval("approval-1")


if __name__ == "__main__":
    unittest.main()
