import unittest
from pathlib import Path

from core import outcome_store
from core.outcome import Outcome


class TestOutcomeStore(unittest.TestCase):
    def test_save_and_load_outcome(self):
        original_file = outcome_store.OUTCOMES_FILE

        try:
            outcome_store.OUTCOMES_FILE = Path("test_outcomes.json")
            outcome_store.OUTCOMES_FILE.unlink(missing_ok=True)

            outcome = Outcome(
                decision_id="decision-123",
                task_id="task-123",
                status="achieved",
                summary="objective was achieved",
                result_ids=["result-123"],
                evidence_ids=["evidence-123"],
            )

            outcome_store.save_outcomes([outcome])
            loaded = outcome_store.load_outcomes()

            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].id, outcome.id)
            self.assertEqual(loaded[0].decision_id, "decision-123")
            self.assertEqual(loaded[0].task_id, "task-123")
            self.assertEqual(loaded[0].status, "achieved")
            self.assertEqual(loaded[0].summary, "objective was achieved")
        finally:
            outcome_store.OUTCOMES_FILE.unlink(missing_ok=True)
            outcome_store.OUTCOMES_FILE = original_file


if __name__ == "__main__":
    unittest.main()
