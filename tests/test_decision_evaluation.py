import unittest

from core.decision_evaluation import DecisionEvaluation


class TestDecisionEvaluation(unittest.TestCase):

    def test_evaluation_stores_decision_assessment(self):
        evaluation = DecisionEvaluation(
            decision_id="decision-1",
            relevance=0.9,
            confidence=0.8,
            risk=0.1,
            effort=0.3,
            score=0.82,
            reason="highly relevant and well supported",
        )

        self.assertEqual(evaluation.decision_id, "decision-1")
        self.assertEqual(evaluation.relevance, 0.9)
        self.assertEqual(evaluation.confidence, 0.8)
        self.assertEqual(evaluation.risk, 0.1)
        self.assertEqual(evaluation.effort, 0.3)
        self.assertEqual(evaluation.score, 0.82)
        self.assertEqual(
            evaluation.reason,
            "highly relevant and well supported",
        )


if __name__ == "__main__":
    unittest.main()
