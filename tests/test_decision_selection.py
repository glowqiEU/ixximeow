import unittest

from core.decision_evaluation import DecisionEvaluation
from core.decision_selection import calculate_selection_score


class TestDecisionSelection(unittest.TestCase):

    def test_selection_score_is_normalized(self):
        evaluation = DecisionEvaluation(
            decision_id="decision-1",
            relevance=1.0,
            confidence=1.0,
            risk=0.0,
            effort=0.0,
            reason="best possible evaluation",
        )

        self.assertEqual(calculate_selection_score(evaluation), 1.0)

    def test_selection_score_rewards_relevance_and_confidence(self):
        baseline = DecisionEvaluation(
            decision_id="decision-1",
            relevance=0.5,
            confidence=0.5,
            risk=0.5,
            effort=0.5,
            reason="baseline",
        )
        stronger = DecisionEvaluation(
            decision_id="decision-2",
            relevance=0.8,
            confidence=0.8,
            risk=0.5,
            effort=0.5,
            reason="stronger support",
        )

        self.assertGreater(
            calculate_selection_score(stronger),
            calculate_selection_score(baseline),
        )

    def test_selection_score_penalizes_risk_and_effort(self):
        baseline = DecisionEvaluation(
            decision_id="decision-1",
            relevance=0.5,
            confidence=0.5,
            risk=0.5,
            effort=0.5,
            reason="baseline",
        )
        riskier = DecisionEvaluation(
            decision_id="decision-2",
            relevance=0.5,
            confidence=0.5,
            risk=0.8,
            effort=0.8,
            reason="higher downside and effort",
        )

        self.assertLess(
            calculate_selection_score(riskier),
            calculate_selection_score(baseline),
        )

    def test_equal_evaluation_signals_produce_neutral_score(self):
        evaluation = DecisionEvaluation(
            decision_id="decision-1",
            relevance=0.5,
            confidence=0.5,
            risk=0.5,
            effort=0.5,
            reason="neutral evaluation",
        )

        self.assertEqual(calculate_selection_score(evaluation), 0.5)


if __name__ == "__main__":
    unittest.main()
