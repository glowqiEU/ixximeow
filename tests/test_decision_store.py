import unittest
from pathlib import Path

from core import decision_store
from core.models import Decision


class TestDecisionStore(unittest.TestCase):
    def test_save_and_load_decision(self):
        original_file = decision_store.DECISIONS_FILE

        try:
            decision_store.DECISIONS_FILE = Path("test_decisions.json")
            decision_store.DECISIONS_FILE.unlink(missing_ok=True)

            decision = Decision(
                objective="goal-1",
                action="create content",
                reason="useful next action",
                priority=5,
            )

            decision_store.save_decisions([decision])
            loaded = decision_store.load_decisions()

            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].id, decision.id)
            self.assertEqual(loaded[0].objective, "goal-1")
            self.assertEqual(loaded[0].action, "create content")
            self.assertEqual(loaded[0].reason, "useful next action")
            self.assertEqual(loaded[0].priority, 5)
            self.assertEqual(loaded[0].status, "proposed")
        finally:
            decision_store.DECISIONS_FILE.unlink(missing_ok=True)
            decision_store.DECISIONS_FILE = original_file


if __name__ == "__main__":
    unittest.main()
