import unittest

from core.action import Action
from core.action_registry import ActionRegistry


class TestActionRegistry(unittest.TestCase):
    def test_registered_handler_executes_action(self):
        registry = ActionRegistry()
        registry.register("inspect_state", lambda action: action.input.get("value"))

        result = registry.execute(
            Action(
                task_id="task-1",
                name="inspect_state",
                input={"value": "ok"},
            )
        )

        self.assertEqual(result, "ok")

    def test_unknown_action_fails_explicitly(self):
        registry = ActionRegistry()

        with self.assertRaises(ValueError):
            registry.execute(Action(task_id="task-1", name="missing"))

    def test_duplicate_registration_fails(self):
        registry = ActionRegistry()
        registry.register("inspect_state", lambda action: None)

        with self.assertRaises(ValueError):
            registry.register("inspect_state", lambda action: None)

    def test_empty_action_name_fails(self):
        registry = ActionRegistry()

        with self.assertRaises(ValueError):
            registry.register("", lambda action: None)


if __name__ == "__main__":
    unittest.main()
