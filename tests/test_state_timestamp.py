import unittest
from datetime import datetime, timezone

from core.models import Decision, Task
from core.state import SystemState
from core.state_manager import apply_decision


class TestStateTimestamp(unittest.TestCase):
    def test_transition_updates_timestamp(self):
        state = SystemState(updated_at="2000-01-01T00:00:00+00:00")
        decision = Decision("goal-1", "post", "useful action")
        task = Task("post", decision_id=decision.id)

        apply_decision(state, decision, task)

        updated = datetime.fromisoformat(state.updated_at)
        self.assertGreater(
            updated,
            datetime(2000, 1, 1, tzinfo=timezone.utc),
        )


if __name__ == "__main__":
    unittest.main()
