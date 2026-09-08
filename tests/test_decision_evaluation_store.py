import unittest
from pathlib import Path

from core import decision_evaluation_store
from core.decision_evaluation import DecisionEvaluation


class TestDecisionEvaluationStore(unittest.TestCase):
    def test_save_and_load_evaluation(self):
        original_file = decision_evaluation_store.DECISION_EVALUATIONS_FILE

        try:
            decision_evaluation_store.DECISION_EVALUATIONS_FILE = Path(
                "test_decision_evaluations.json"
            )
            decision_evaluation_store.DECISION_EVALUATIONS_FILE.unlink(
                missing_ok=True
            )

            evaluation = DecisionEvaluation(
                decision_id="decision-123",
                relevance=0.9,
                confidence=0.8,
                risk=0.2,
                effort=0.3,
                reason="strong candidate",
            )

            decision_evaluation_store.save_decision_evaluations([evaluation])
            loaded = decision_evaluation_store.load_decision_evaluations()

            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].decision_id, "decision-123")
            self.assertEqual(loaded[0].relevance, 0.9)
            self.assertEqual(loaded[0].confidence, 0.8)
            self.assertEqual(loaded[0].risk, 0.2)
            self.assertEqual(loaded[0].effort, 0.3)
            self.assertEqual(loaded[0].reason, "strong candidate")
        finally:
            decision_evaluation_store.DECISION_EVALUATIONS_FILE.unlink(
                missing_ok=True
            )
            decision_evaluation_store.DECISION_EVALUATIONS_FILE = original_file


if __name__ == "__main__":
    unittest.main()
