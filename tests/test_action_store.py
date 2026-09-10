import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.action import Action
from core.action_store import load_actions, save_actions


class TestActionStore(unittest.TestCase):
    def test_save_and_load_preserves_action(self):
        action = Action(
            task_id="task-1",
            name="post",
            input={"text": "hello"},
            permission_level="execute",
            id="action-1",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "actions.json"
            with patch("core.action_store.ACTIONS_FILE", path):
                save_actions([action])
                loaded = load_actions()

        self.assertEqual(loaded, [action])

    def test_load_empty_store_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "actions.json"
            with patch("core.action_store.ACTIONS_FILE", path):
                self.assertEqual(load_actions(), [])


if __name__ == "__main__":
    unittest.main()
