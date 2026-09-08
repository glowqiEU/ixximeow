import unittest

from core.context import AgentContext
from core.decision_evaluation import DecisionEvaluation
from core.decision_evaluator import evaluate_decision
from core.models import Decision


class TestDecisionEvaluator(unittest.TestCase):

    def test_evaluate_decision_returns_evaluation(self):
        decision = Decision(
            objective="goal-1",
            action="continue: create X content",
            reason="an active task already exists",
            priority=10,
        )

        context = AgentContext(
            goal_id="goal-1",
            task="create X content",
        )

        evaluation = evaluate_decision(decision, context)

        self.assertIsInstance(evaluation, DecisionEvaluation)
        self.assertEqual(evaluation.decision_id, decision.id)

        self.assertGreaterEqual(evaluation.relevance, 0.0)
        self.assertLessEqual(evaluation.relevance, 1.0)

        self.assertGreaterEqual(evaluation.confidence, 0.0)
        self.assertLessEqual(evaluation.confidence, 1.0)

        self.assertGreaterEqual(evaluation.risk, 0.0)
        self.assertLessEqual(evaluation.risk, 1.0)

        self.assertGreaterEqual(evaluation.effort, 0.0)
        self.assertLessEqual(evaluation.effort, 1.0)

        self.assertTrue(evaluation.reason)

    def test_matching_goal_has_higher_relevance(self):
        decision = Decision(
            objective="goal-1",
            action="continue: create X content",
            reason="an active task already exists",
            priority=10,
        )

        matching_context = AgentContext(
            goal_id="goal-1",
            task="create X content",
        )

        different_context = AgentContext(
            goal_id="goal-2",
            task="create X content",
        )

        matching = evaluate_decision(decision, matching_context)
        different = evaluate_decision(decision, different_context)

        self.assertGreater(
            matching.relevance,
            different.relevance,
        )


if __name__ == "__main__":
    unittest.main()
