import unittest

from core.action import Action
from core.action_registry import ActionRegistry
from core.action_response import ActionResponse


class TestActionRegistry(unittest.TestCase):
    def test_registered_handler_executes_action(self):
        registry = ActionRegistry()
        registry.register(
            "inspect_state",
            lambda action: ActionResponse(
                success=True,
                summary="state inspected",
                output=action.input.get("value"),
            ),
        )

        result = registry.execute(
            Action(
                task_id="task-1",
                name="inspect_state",
                input={"value": "ok"},
            )
        )

        self.assertTrue(result.success)
        self.assertEqual(result.summary, "state inspected")
        self.assertEqual(result.output, "ok")

    def test_handler_must_return_action_response(self):
        registry = ActionRegistry()
        registry.register("inspect_state", lambda action: "ok")

        with self.assertRaises(TypeError):
            registry.execute(Action(task_id="task-1", name="inspect_state"))

    def test_unknown_action_fails_explicitly(self):
        registry = ActionRegistry()

        with self.assertRaises(ValueError):
            registry.execute(Action(task_id="task-1", name="missing"))

    def test_duplicate_registration_fails(self):
        registry = ActionRegistry()
        registry.register(
            "inspect_state",
            lambda action: ActionResponse(success=True, summary="done"),
        )

        with self.assertRaises(ValueError):
            registry.register(
                "inspect_state",
                lambda action: ActionResponse(success=True, summary="done"),
            )

    def test_empty_action_name_fails(self):
        registry = ActionRegistry()

        with self.assertRaises(ValueError):
            registry.register(
                "",
                lambda action: ActionResponse(success=True, summary="done"),
            )


if __name__ == "__main__":
    unittest.main()
