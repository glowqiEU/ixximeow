import unittest
from unittest.mock import patch

from core.action import Action
from core.action_registry import ActionRegistry
from core.action_response import ActionResponse
from core.approval import Approval
from core.executor import execute_task
from core.models import Task


class TestExecutorActionBoundary(unittest.TestCase):
    def test_executor_delegates_to_registry_and_builds_result_from_response(self):
        registry = ActionRegistry()
        seen = []

        def handler(action):
            seen.append(action)
            return ActionResponse(
                success=True,
                summary="handler completed",
                output={"verified_by_handler": True},
            )

        registry.register("execute_task", handler)
        task = Task(title="create post", id="task-1")

        with patch("core.executor.load_actions", return_value=[]), \
             patch("core.executor.save_actions"), \
             patch("core.executor.load_results", return_value=[]), \
             patch("core.executor.save_results"), \
             patch("core.executor.verify_execution_result"):
            completed_task, result = execute_task(task, registry=registry)

        self.assertEqual(completed_task.status, "completed")
        self.assertTrue(result.success)
        self.assertEqual(result.summary, "handler completed")
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0].task_id, "task-1")
        self.assertEqual(seen[0].name, "execute_task")
        self.assertEqual(seen[0].input, {"title": "create post"})
        self.assertEqual(seen[0].permission_level, "execute")
        self.assertEqual(result.action_id, seen[0].id)
        self.assertTrue(result.execution_id)

    def test_executor_preserves_task_required_permission_on_action_after_approval(self):
        registry = ActionRegistry()
        seen = []

        def handler(action):
            seen.append(action)
            return ActionResponse(success=True, summary="published")

        registry.register("execute_task", handler)
        task = Task(
            title="publish post",
            id="task-1",
            approval_id="approval-1",
            required_level="publish",
        )
        approval = Approval(
            task_id="task-1",
            required_level="publish",
            reason="publishing requires approval",
            status="approved",
            id="approval-1",
        )

        with patch("core.executor.load_approvals", return_value=[approval]), \
             patch("core.executor.load_actions", return_value=[]), \
             patch("core.executor.save_actions"), \
             patch("core.executor.load_results", return_value=[]), \
             patch("core.executor.save_results"), \
             patch("core.executor.verify_execution_result"):
            execute_task(task, approval=approval, registry=registry)

        self.assertEqual(seen[0].permission_level, "publish")

    def test_executor_rejects_higher_permission_without_approval(self):
        registry = ActionRegistry()
        seen = []

        def handler(action):
            seen.append(action)
            return ActionResponse(success=True, summary="should not run")

        registry.register("execute_task", handler)
        task = Task(
            title="publish post",
            id="task-1",
            required_level="publish",
        )

        with patch("core.executor.load_actions", return_value=[]), \
             patch("core.executor.load_results"), \
             patch("core.executor.save_results"):
            with self.assertRaises(PermissionError):
                execute_task(task, registry=registry)

        self.assertEqual(seen, [])

    def test_executor_rejects_unpersisted_approved_permission(self):
        registry = ActionRegistry()
        seen = []

        def handler(action):
            seen.append(action)
            return ActionResponse(success=True, summary="should not run")

        registry.register("execute_task", handler)
        task = Task(
            title="publish post",
            id="task-1",
            approval_id="approval-1",
            required_level="publish",
        )
        approval = Approval(
            task_id="task-1",
            required_level="publish",
            reason="publishing requires approval",
            status="approved",
            id="approval-1",
        )

        with patch("core.executor.load_approvals", return_value=[]), \
             patch("core.executor.load_actions", return_value=[]), \
             patch("core.executor.load_results"), \
             patch("core.executor.save_results"):
            with self.assertRaises(PermissionError):
                execute_task(task, approval=approval, registry=registry)

        self.assertEqual(seen, [])

    def test_action_permission_level_is_validated(self):
        with self.assertRaises(ValueError):
            Action(task_id="task-1", name="execute_task", permission_level="invalid")

    def test_failed_handler_response_produces_failed_task_and_result(self):
        registry = ActionRegistry()
        registry.register(
            "execute_task",
            lambda action: ActionResponse(
                success=False,
                summary="handler reported failure",
            ),
        )
        task = Task(title="create post", id="task-1")

        with patch("core.executor.load_actions", return_value=[]), \
             patch("core.executor.save_actions"), \
             patch("core.executor.load_results", return_value=[]), \
             patch("core.executor.save_results"), \
             patch("core.executor.verify_execution_result"):
            failed_task, result = execute_task(task, registry=registry)

        self.assertEqual(failed_task.status, "failed")
        self.assertFalse(result.success)
        self.assertEqual(result.summary, "handler reported failure")


if __name__ == "__main__":
    unittest.main()
