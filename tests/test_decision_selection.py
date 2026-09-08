import unittest

from core.decision_evaluation import DecisionEvaluation
from core.decision_selection import calculate_selection_score, select_decision
from core.models import Decision


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

    def test_select_decision_uses_evaluation_score(self):
        lower = Decision(
            objective="goal-1",
            action="lower score action",
            reason="candidate",
            priority=10,
        )
        higher = Decision(
            objective="goal-1",
            action="higher score action",
            reason="candidate",
            priority=1,
        )

        evaluations = [
            DecisionEvaluation(
                decision_id=lower.id,
                relevance=0.4,
                confidence=0.4,
                risk=0.6,
                effort=0.6,
                reason="weaker evaluation",
            ),
            DecisionEvaluation(
                decision_id=higher.id,
                relevance=0.9,
                confidence=0.9,
                risk=0.1,
                effort=0.1,
                reason="stronger evaluation",
            ),
        ]

        result = select_decision([lower, higher], evaluations)

        self.assertEqual(result.id, higher.id)

    def test_select_decision_requires_evaluation_for_each_candidate(self):
        decision = Decision(
            objective="goal-1",
            action="candidate",
            reason="candidate",
        )

        with self.assertRaises(ValueError):
            select_decision([decision], [])


if __name__ == "__main__":
    unittest.main()
