import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from core.action import Action
from core.action_registry import ActionRegistry
from core.execution import Execution
from core.execution_service import (
    execute_action,
    execute_reserved_action,
    recover_uncertain_execution,
    reserve_execution,
)
from core.execution_store import load_executions, upsert_execution
from core.evidence_store import find_evidence_by_result_id
from core.reconciliation import Reconciliation
from core.result_store import find_result_by_execution_id


class TestExecutionService(unittest.TestCase):
    def _patch_stores(self, root):
        import core.evidence_store as evidence_store
        import core.execution_store as execution_store
        import core.result_store as result_store

        original = (
            evidence_store.EVIDENCE_FILE,
            execution_store.EXECUTIONS_FILE,
            result_store.RESULTS_FILE,
        )
        evidence_store.EVIDENCE_FILE = root / "evidence.json"
        execution_store.EXECUTIONS_FILE = root / "executions.json"
        result_store.RESULTS_FILE = root / "results.json"
        return (evidence_store, execution_store, result_store), original

    def _restore_stores(self, stores, original):
        evidence_store, execution_store, result_store = stores
        (
            evidence_store.EVIDENCE_FILE,
            execution_store.EXECUTIONS_FILE,
            result_store.RESULTS_FILE,
        ) = original

    def test_reservation_is_pending_before_execution(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execution = reserve_execution(action)
                persisted = load_executions()
            finally:
                self._restore_stores(stores, original)

            self.assertEqual(execution.status, "pending")
            self.assertEqual(len(persisted), 1)
            self.assertEqual(persisted[0].status, "pending")
            self.assertEqual(persisted[0].idempotency_key, action.id)

    def test_crash_between_reservation_and_task_running_leaves_safe_pending_execution(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execution = reserve_execution(action)
                with patch("core.execution_service.execute_reserved_action") as execute:
                    # Simulate the orchestrator crashing before it can start execution.
                    raise RuntimeError("simulated task persistence crash")
            except RuntimeError:
                pass
            finally:
                self._restore_stores(stores, original)

            self.assertEqual(load_executions()[0].status, "pending")
            execute.assert_not_called()
            self.assertEqual(execution.action_id, action.id)

    def test_reserved_execution_transitions_to_running_only_before_handler(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            registry = ActionRegistry()
            calls = []

            def handler(action):
                calls.append(action.id)
                return {"summary": "published"}

            registry.register("publish_post", handler)
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execution = reserve_execution(action)
                completed, result, _ = execute_reserved_action(action, execution, registry)
            finally:
                self._restore_stores(stores, original)

            self.assertEqual(completed.status, "succeeded")
            self.assertEqual(completed.attempt, 1)
            self.assertEqual(result.execution_id, execution.id)
            self.assertEqual(calls, [action.id])

    def test_action_runs_through_execution_result_evidence_chain(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            registry = ActionRegistry()
            registry.register("publish_post", lambda action: {"summary": "published"})
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execution, result, evidence = execute_action(action, registry)
            finally:
                self._restore_stores(stores, original)

            self.assertEqual(execution.action_id, action.id)
            self.assertEqual(execution.task_id, action.task_id)
            self.assertEqual(execution.status, "succeeded")
            self.assertEqual(result.action_id, action.id)
            self.assertEqual(result.execution_id, execution.id)
            self.assertTrue(result.success)
            self.assertEqual(evidence[0].result_id, result.id)
            self.assertEqual(evidence[0].execution_id, execution.id)
            self.assertTrue(evidence[0].verified)

    def test_handler_failure_is_recorded_as_technical_failure(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            registry = ActionRegistry()
            registry.register("publish_post", lambda action: (_ for _ in ()).throw(RuntimeError("boom")))
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execution, result, evidence = execute_action(action, registry)
            finally:
                self._restore_stores(stores, original)

            self.assertEqual(execution.status, "failed")
            self.assertFalse(result.success)
            self.assertEqual(evidence[0].value, False)

    def test_duplicate_action_is_rejected_before_handler_runs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            registry = ActionRegistry()
            calls = []

            def handler(action):
                calls.append(action.id)
                return {"summary": "published"}

            registry.register("publish_post", handler)
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execute_action(action, registry)
                with self.assertRaises(ValueError):
                    execute_action(action, registry)
            finally:
                self._restore_stores(stores, original)

            self.assertEqual(calls, ["action-1"])

    def test_duplicate_action_execution_is_rejected_by_idempotency(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            registry = ActionRegistry()
            registry.register("publish_post", lambda action: {"summary": "published"})
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                first, _, _ = execute_action(action, registry)
                with self.assertRaises(ValueError):
                    execute_action(action, registry)
            finally:
                self._restore_stores(stores, original)

            self.assertEqual(first.status, "succeeded")
            self.assertEqual(first.idempotency_key, action.id)

    def test_artifact_failure_leaves_durable_execution_running_for_recovery(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            registry = ActionRegistry()
            registry.register("publish_post", lambda action: {"summary": "published"})
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                with patch("core.execution_service._build_evidence", side_effect=RuntimeError("artifact failure")):
                    with self.assertRaises(RuntimeError):
                        execute_action(action, registry)

                executions = load_executions()
                self.assertEqual(len(executions), 1)
                self.assertEqual(executions[0].action_id, action.id)
                self.assertEqual(executions[0].task_id, action.task_id)
                self.assertEqual(executions[0].status, "running")
                self.assertEqual(executions[0].attempt, 1)
                self.assertIsNone(executions[0].finished_at)
            finally:
                self._restore_stores(stores, original)

    def _uncertain_execution(self, action):
        return Execution(
            action_id=action.id,
            task_id=action.task_id,
            status="uncertain",
            attempt=1,
            id="execution-1",
        )

    def test_recover_already_succeeded_never_reruns_handler(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            registry = ActionRegistry()
            calls = []

            def handler(action):
                calls.append(action.id)
                return {"summary": "published"}

            registry.register("publish_post", handler)
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execution = self._uncertain_execution(action)
                upsert_execution(execution)

                recovered, result, evidence = recover_uncertain_execution(
                    execution.id,
                    action,
                    lambda current_action: Reconciliation(
                        status="already_succeeded",
                        summary="remote post already exists",
                        source="platform-api",
                    ),
                )

                self.assertEqual(recovered.id, execution.id)
                self.assertEqual(recovered.status, "succeeded")
                self.assertEqual(recovered.attempt, 1)
                self.assertIsNotNone(result)
                self.assertTrue(result.success)
                self.assertEqual(len(evidence), 1)
                self.assertEqual(evidence[0].source, "platform-api")
                self.assertEqual(calls, [])
            finally:
                self._restore_stores(stores, original)

    def test_recovery_resumes_after_final_execution_persistence_failure(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execution = self._uncertain_execution(action)
                upsert_execution(execution)
                reconciliation = Reconciliation(
                    status="already_succeeded",
                    summary="remote post already exists",
                    source="platform-api",
                )

                with patch(
                    "core.execution_service.upsert_execution",
                    side_effect=RuntimeError("execution persistence failure"),
                ):
                    with self.assertRaises(RuntimeError):
                        recover_uncertain_execution(
                            execution.id,
                            action,
                            lambda current_action: reconciliation,
                        )

                persisted_execution = load_executions()[0]
                self.assertEqual(persisted_execution.status, "uncertain")
                persisted_result = find_result_by_execution_id(execution.id)
                self.assertIsNotNone(persisted_result)
                persisted_evidence = find_evidence_by_result_id(persisted_result.id)
                self.assertEqual(len(persisted_evidence), 1)

                recovered, result, evidence = recover_uncertain_execution(
                    execution.id,
                    action,
                    lambda current_action: reconciliation,
                )

                self.assertEqual(recovered.status, "succeeded")
                self.assertEqual(result.id, persisted_result.id)
                self.assertEqual(evidence[0].id, persisted_evidence[0].id)
                self.assertEqual(len(find_evidence_by_result_id(result.id)), 1)
            finally:
                self._restore_stores(stores, original)

    def test_recover_unknown_keeps_execution_uncertain(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execution = self._uncertain_execution(action)
                upsert_execution(execution)

                recovered, result, evidence = recover_uncertain_execution(
                    execution.id,
                    action,
                    lambda current_action: Reconciliation(
                        status="unknown",
                        summary="remote state could not be determined",
                        source="platform-api",
                    ),
                )

                self.assertEqual(recovered.id, execution.id)
                self.assertEqual(recovered.status, "uncertain")
                self.assertIsNone(result)
                self.assertEqual(evidence, [])
            finally:
                self._restore_stores(stores, original)

    def test_recover_not_executed_keeps_execution_uncertain_until_retry_contract_exists(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execution = self._uncertain_execution(action)
                upsert_execution(execution)

                recovered, result, evidence = recover_uncertain_execution(
                    execution.id,
                    action,
                    lambda current_action: Reconciliation(
                        status="not_executed",
                        summary="platform reports no matching side effect",
                        source="platform-api",
                    ),
                )

                self.assertEqual(recovered.id, execution.id)
                self.assertEqual(recovered.status, "uncertain")
                self.assertIsNone(result)
                self.assertEqual(evidence, [])
            finally:
                self._restore_stores(stores, original)

    def test_recover_rejects_unstructured_reconciliation(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            try:
                execution = self._uncertain_execution(action)
                upsert_execution(execution)

                with self.assertRaises(ValueError):
                    recover_uncertain_execution(
                        execution.id,
                        action,
                        lambda current_action: "already_succeeded",
                    )
            finally:
                self._restore_stores(stores, original)


if __name__ == "__main__":
    unittest.main()
