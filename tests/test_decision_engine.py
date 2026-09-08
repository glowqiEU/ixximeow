import unittest

from core.decision_engine import choose_decision
from core.models import Decision


class TestDecisionEngine(unittest.TestCase):

    def test_choose_highest_priority(self):
        low = Decision(
            objective="goal-1",
            action="low priority action",
            reason="less important",
            priority=1,
        )

        high = Decision(
            objective="goal-1",
            action="high priority action",
            reason="more important",
            priority=10,
        )

        result = choose_decision([low, high])

        self.assertEqual(result.id, high.id)

    def test_empty_options_raise_error(self):
        with self.assertRaises(ValueError):
            choose_decision([])


if __name__ == "__main__":
    unittest.main()
