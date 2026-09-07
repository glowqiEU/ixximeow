import unittest

from core.orchestrator import Orchestrator
from core.approval_store import load_approvals


class TestOrchestratorApproval(unittest.TestCase):
    def test_orchestrator_stops_for_required_approval(self):
        decision, task, result = Orchestrator().run()

        self.assertEqual(task.status, "waiting_approval")
        self.assertIsNone(result)

        approvals = load_approvals()

        self.assertTrue(
            any(
                approval.task_id == task.id
                and approval.status == "pending"
                for approval in approvals
            )
        )


if __name__ == "__main__":
    unittest.main()
