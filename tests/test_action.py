import unittest

from core.action import Action


class TestAction(unittest.TestCase):
    def test_action_has_explicit_execution_contract(self):
        action = Action(
            task_id="task-1",
            name="publish_post",
            input={"text": "hello"},
            permission_level="execute",
        )

        self.assertIsNotNone(action.id)
        self.assertEqual(action.task_id, "task-1")
        self.assertEqual(action.name, "publish_post")
        self.assertEqual(action.input, {"text": "hello"})
        self.assertEqual(action.permission_level, "execute")

    def test_action_defaults_to_empty_input(self):
        action = Action(task_id="task-1", name="inspect_state")

        self.assertEqual(action.input, {})


if __name__ == "__main__":
    unittest.main()
