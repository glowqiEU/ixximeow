import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.action import Action
from core.action_registry import ActionRegistry
from core.evidence_store import load_evidence
from core.execution_service import execute_action
from core.execution_store import load_executions
from core.result_store import load_results


class TestExecutionService(unittest.TestCase):
    def test_action_runs_through_execution_result_evidence_chain(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            registry = ActionRegistry()
            registry.register("publish_post", lambda action: {"summary": "published"})
            action = Action(task_id="task-1", name="publish_post", id="action-1")

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
            try:
                execution, result, evidence = execute_action(action, registry)
            finally:
                evidence_store.EVIDENCE_FILE, execution_store.EXECUTIONS_FILE, result_store.RESULTS_FILE = original

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
            try:
                execution, result, evidence = execute_action(action, registry)
            finally:
                evidence_store.EVIDENCE_FILE, execution_store.EXECUTIONS_FILE, result_store.RESULTS_FILE = original

            self.assertEqual(execution.status, "failed")
            self.assertFalse(result.success)
            self.assertEqual(evidence[0].value, False)


if __name__ == "__main__":
    unittest.main()
