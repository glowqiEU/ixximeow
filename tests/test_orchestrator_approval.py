import unittest

from core.orchestrator import Orchestrator
from core.approval_lifecycle import transition_approval
from core.approval_store import load_approvals, save_approvals
from core.history_store import load_events
from core.state_store import load_state
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

    def test_approved_task_resumes_and_persists(self):
        _, task, result = Orchestrator().run()
        self.assertIsNone(result)

        approvals = load_approvals()
        approval = next(
            item for item in approvals if item.task_id == task.id
        )

        approval = transition_approval(approval, "approved")
        save_approvals(approvals)

        resumed_task, resumed_result = Orchestrator().resume_approval(
            approval.id
        )

        self.assertEqual(resumed_task.id, task.id)
        self.assertEqual(resumed_task.status, "completed")
        self.assertIsNotNone(resumed_result)
        self.assertEqual(resumed_result.task_id, task.id)
        self.assertTrue(resumed_result.success)

        persisted_task = next(
            item for item in load_tasks() if item.id == task.id
        )
        self.assertEqual(persisted_task.status, "completed")
        self.assertEqual(persisted_task.approval_id, approval.id)

        state = load_state()
        self.assertIsNone(state.active_task)
        self.assertEqual(state.last_result_id, resumed_result.id)

        persisted_approval = next(
            item for item in load_approvals() if item.id == approval.id
        )
        self.assertEqual(persisted_approval.status, "approved")

        self.assertTrue(
            any(
                event.event_type == "task_executed"
                and event.task_id == task.id
                and event.result_id == resumed_result.id
                for event in load_events()
            )
        )

    def test_rejected_task_resumes_and_is_cancelled(self):
        _, task, result = Orchestrator().run()
        self.assertIsNone(result)

        approvals = load_approvals()
        approval = next(
            item for item in approvals if item.task_id == task.id
        )

        approval = transition_approval(approval, "rejected")
        save_approvals(approvals)

        resumed_task, resumed_result = Orchestrator().resume_approval(
            approval.id
        )

        self.assertEqual(resumed_task.id, task.id)
        self.assertEqual(resumed_task.status, "cancelled")
        self.assertIsNone(resumed_result)

        persisted_task = next(
            item for item in load_tasks() if item.id == task.id
        )
        self.assertEqual(persisted_task.status, "cancelled")
        self.assertEqual(persisted_task.approval_id, approval.id)

        state = load_state()
        self.assertIsNone(state.active_task)

        self.assertTrue(
            any(
                event.event_type == "task_cancelled"
                and event.task_id == task.id
                for event in load_events()
            )
        )


if __name__ == "__main__":
    unittest.main()
