import unittest
from unittest.mock import patch

from core.action_registry import ActionRegistry
from core.action_response import ActionResponse
from core.executor import execute_task
from core.models import Task


class TestExecutorFailureSemantics(unittest.TestCase):
    def _execute(self, registry):
        task = Task(title="create post", id="task-1")
        with patch("core.agent_config.CURRENT_AUTONOMY_LEVEL", 3), \
             patch("core.executor.load_actions", return_value=[]), \
             patch("core.executor.save_actions"), \
             patch("core.executor.load_results", return_value=[]), \
             patch("core.executor.save_results"), \
             patch("core.executor.verify_execution_result"):
            return execute_task(task, registry=registry)

    def test_handler_reported_failure_is_action_failure(self):
        registry = ActionRegistry()
        registry.register(
            "execute_task",
            lambda action: ActionResponse(
                success=False,
                summary="destination rejected payload",
            ),
        )

        failed_task, result = self._execute(registry)

        self.assertEqual(failed_task.status, "failed")
        self.assertFalse(result.success)
        self.assertEqual(result.summary, "destination rejected payload")
        self.assertEqual(result.failure_kind, "action_failed")

    def test_handler_exception_is_execution_error(self):
        registry = ActionRegistry()

        def handler(action):
            raise RuntimeError("network unavailable")

        registry.register("execute_task", handler)

        failed_task, result = self._execute(registry)

        self.assertEqual(failed_task.status, "failed")
        self.assertFalse(result.success)
        self.assertEqual(result.failure_kind, "execution_error")
        self.assertIn("network unavailable", result.summary)

    def test_unknown_action_is_dispatch_error(self):
        registry = ActionRegistry()
        registry.register("different_action", lambda action: ActionResponse(True, "ok"))

        failed_task, result = self._execute(registry)

        self.assertEqual(failed_task.status, "failed")
        self.assertFalse(result.success)
        self.assertEqual(result.failure_kind, "dispatch_error")
        self.assertIn("action not registered", result.summary)

    def test_invalid_handler_response_is_contract_error(self):
        registry = ActionRegistry()
        registry.register("execute_task", lambda action: "not an ActionResponse")

        failed_task, result = self._execute(registry)

        self.assertEqual(failed_task.status, "failed")
        self.assertFalse(result.success)
        self.assertEqual(result.failure_kind, "contract_error")
        self.assertIn("ActionResponse", result.summary)

    def test_verification_failure_is_not_converted_into_execution_failure(self):
        registry = ActionRegistry()
        registry.register(
            "execute_task",
            lambda action: ActionResponse(True, "handler completed"),
        )
        task = Task(title="create post", id="task-1")

        with patch("core.agent_config.CURRENT_AUTONOMY_LEVEL", 3), \
             patch("core.executor.load_actions", return_value=[]), \
             patch("core.executor.save_actions"), \
             patch("core.executor.load_results", return_value=[]), \
             patch("core.executor.save_results") as save_results, \
             patch(
                 "core.executor.verify_execution_result",
                 side_effect=ValueError("verification rejected result"),
             ):
            with self.assertRaisesRegex(ValueError, "verification rejected result"):
                execute_task(task, registry=registry)

        save_results.assert_not_called()


if __name__ == "__main__":
    unittest.main()
