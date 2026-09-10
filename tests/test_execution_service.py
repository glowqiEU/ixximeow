import unittest
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from core.action import Action
from core.action_registry import ActionRegistry
from core.execution_service import execute_action, upsert_evidence as persist_real_evidence
from core.execution_store import load_executions
from core.evidence_store import find_evidence_by_result_id
from core.result_store import find_result_by_execution_id


class TestExecutionService(unittest.TestCase):
    def _patch_stores(self, root):
        from core import execution_store, evidence_store, result_store

        original = (
            execution_store.EXECUTIONS_FILE,
            evidence_store.EVIDENCE_FILE,
            result_store.RESULTS_FILE,
        )
        execution_store.EXECUTIONS_FILE = root / "executions.json"
        evidence_store.EVIDENCE_FILE = root / "evidence.json"
        result_store.RESULTS_FILE = root / "results.json"
        return (execution_store, evidence_store, result_store), original

    def _restore_stores(self, stores, original):
        for store, value in zip(stores, original):
            if stores.index(store) == 0:
                store.EXECUTIONS_FILE = value
            elif stores.index(store) == 1:
                store.EVIDENCE_FILE = value
            else:
                store.RESULTS_FILE = value

    def test_partial_evidence_persistence_does_not_commit_terminal_execution(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            registry = ActionRegistry()
            registry.register(
                "publish_post",
                lambda action: {
                    "summary": "published",
                    "evidence": [
                        {
                            "claim": "post_published",
                            "kind": "execution_output",
                            "value": True,
                            "content": "the post was published",
                            "verified": True,
                        }
                    ],
                },
            )
            action = Action(task_id="task-1", name="publish_post", id="action-1")
            stores, original = self._patch_stores(root)
            calls = []

            def persist_evidence(item):
                calls.append(item.claim)
                if len(calls) == 2:
                    raise RuntimeError("second evidence persistence failure")
                persist_real_evidence(item)

            try:
                with patch(
                    "core.execution_service.upsert_evidence",
                    side_effect=persist_evidence,
                ):
                    with self.assertRaises(RuntimeError):
                        execute_action(action, registry)

                execution = load_executions()[0]
                self.assertEqual(execution.status, "running")
                result = find_result_by_execution_id(execution.id)
                self.assertIsNotNone(result)
                persisted_evidence = find_evidence_by_result_id(result.id)
                self.assertEqual(len(persisted_evidence), 1)
                self.assertEqual(persisted_evidence[0].claim, "execution_succeeded")
                self.assertEqual(calls, ["execution_succeeded", "post_published"])
            finally:
                self._restore_stores(stores, original)
