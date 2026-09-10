import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from core.action import Action
from core.action_registry import ActionRegistry
from core.execution_service import execute_action
from core.execution_store import load_executions
from core.evidence_store import find_evidence_by_result_id
from core.result_store import find_result_by_execution_id


class TestExecutionTerminalPersistence(unittest.TestCase):
    def test_terminal_execution_persistence_failure_leaves_all_artifacts_durable(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
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
                registry = ActionRegistry()
                registry.register("publish_post", lambda action: {"summary": "published"})
                action = Action(task_id="task-1", name="publish_post", id="action-1")

                with patch(
                    "core.execution_service.upsert_execution",
                    side_effect=RuntimeError("terminal execution persistence failure"),
                ):
                    with self.assertRaises(RuntimeError):
                        execute_action(action, registry)

                execution = load_executions()[0]
                self.assertEqual(execution.status, "running")
                result = find_result_by_execution_id(execution.id)
                self.assertIsNotNone(result)
                self.assertEqual(result.execution_id, execution.id)
                evidence = find_evidence_by_result_id(result.id)
                self.assertGreaterEqual(len(evidence), 1)
                self.assertTrue(all(item.execution_id == execution.id for item in evidence))
            finally:
                (
                    evidence_store.EVIDENCE_FILE,
                    execution_store.EXECUTIONS_FILE,
                    result_store.RESULTS_FILE,
                ) = original


if __name__ == "__main__":
    unittest.main()
