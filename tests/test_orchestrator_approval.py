import unittest

from core.orchestrator import Orchestrator
from core.approval_store import load_approvals
from core.task_store import load_tasks


class TestOrchestratorApproval(unittest.TestCase):
    def test_orchestrator_stops_for_required_approval(self):
        decision, task, result = Orchestrator().run()

        self.assertEqual(task.status, "waiting_approval")
        self.assertIsNone(result)

        approvals = load_approvals()

        matching_approvals = [
            approval
            for approval in approvals
            if approval.task_id == task.id
        ]

        self.assertEqual(len(matching_approvals), 1)

        approval = matching_approvals[0]
        self.assertEqual(approval.status, "pending")
        self.assertEqual(task.approval_id, approval.id)

        tasks = load_tasks()
        persisted_task = next(
            item for item in tasks if item.id == task.id
        )

        self.assertEqual(persisted_task.status, "waiting_approval")
        self.assertEqual(persisted_task.approval_id, approval.id)


if __name__ == "__main__":
    unittest.main()
