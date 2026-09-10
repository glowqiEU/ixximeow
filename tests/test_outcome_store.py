import unittest
from pathlib import Path

from core import outcome_store
from core.outcome import Outcome


class TestOutcomeStore(unittest.TestCase):
    def test_save_and_load_outcome_preserves_full_lineage(self):
        original_file = outcome_store.OUTCOMES_FILE

        try:
            outcome_store.OUTCOMES_FILE = Path("test_outcomes.json")
            outcome_store.OUTCOMES_FILE.unlink(missing_ok=True)

            outcome = Outcome(
                task_id="task-123",
                decision_id="decision-456",
                status="success",
                summary="objective was achieved",
                result_ids=["result-789"],
                evidence_ids=["evidence-012"],
            )

            outcome_store.save_outcomes([outcome])
            loaded = outcome_store.load_outcomes()

            self.assertEqual(loaded, [outcome])
            self.assertEqual(loaded[0].id, outcome.id)
            self.assertEqual(loaded[0].task_id, "task-123")
            self.assertEqual(loaded[0].decision_id, "decision-456")
            self.assertIsNone(loaded[0].success)
            self.assertEqual(loaded[0].status, "success")
            self.assertEqual(loaded[0].summary, "objective was achieved")
            self.assertEqual(loaded[0].result_ids, ["result-789"])
            self.assertEqual(loaded[0].evidence_ids, ["evidence-012"])
            self.assertEqual(loaded[0].created_at, outcome.created_at)
        finally:
            outcome_store.OUTCOMES_FILE.unlink(missing_ok=True)
            outcome_store.OUTCOMES_FILE = original_file

    def test_load_returns_empty_when_store_is_missing(self):
        original_file = outcome_store.OUTCOMES_FILE

        try:
            outcome_store.OUTCOMES_FILE = Path("missing_outcomes.json")
            outcome_store.OUTCOMES_FILE.unlink(missing_ok=True)

            self.assertEqual(outcome_store.load_outcomes(), [])
        finally:
            outcome_store.OUTCOMES_FILE = original_file


if __name__ == "__main__":
    unittest.main()
