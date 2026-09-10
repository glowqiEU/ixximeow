import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.action import Action
import core.action_store as action_store


class TestActionStore(unittest.TestCase):
    def test_action_round_trips_with_full_definition(self):
        with TemporaryDirectory() as directory:
            original = action_store.ACTIONS_FILE
            action_store.ACTIONS_FILE = Path(directory) / "actions.json"
            try:
                action = Action(
                    task_id="task-1",
                    name="publish_post",
                    input={"text": "hello"},
                    permission_level="publish",
                    id="action-1",
                )
                action_store.upsert_action(action)
                loaded = action_store.find_action_by_id("action-1")
            finally:
                action_store.ACTIONS_FILE = original

            self.assertIsNotNone(loaded)
            self.assertEqual(loaded.task_id, "task-1")
            self.assertEqual(loaded.name, "publish_post")
            self.assertEqual(loaded.input, {"text": "hello"})
            self.assertEqual(loaded.permission_level, "publish")
            self.assertEqual(loaded.id, "action-1")

    def test_missing_action_is_not_silently_reconstructed(self):
        with TemporaryDirectory() as directory:
            original = action_store.ACTIONS_FILE
            action_store.ACTIONS_FILE = Path(directory) / "actions.json"
            try:
                loaded = action_store.find_action_by_id("missing")
            finally:
                action_store.ACTIONS_FILE = original

            self.assertIsNone(loaded)


if __name__ == "__main__":
    unittest.main()
