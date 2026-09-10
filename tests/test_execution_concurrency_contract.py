import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from core.action import Action
from core.action_registry import ActionRegistry
from core.execution_service import execute_action
import core.execution_store as execution_store
import core.evidence_store as evidence_store
import core.result_store as result_store


class TestExecutionConcurrencyContract(unittest.TestCase):
    def test_concurrent_same_action_reserves_only_one_execution(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            original = (
                execution_store.EXECUTIONS_FILE,
                evidence_store.EVIDENCE_FILE,
                result_store.RESULTS_FILE,
            )
            execution_store.EXECUTIONS_FILE = root / "executions.json"
            evidence_store.EVIDENCE_FILE = root / "evidence.json"
            result_store.RESULTS_FILE = root / "results.json"
            try:
                registry = ActionRegistry()
                calls = []

                def handler(action):
                    calls.append(action.id)
                    return {"summary": "published"}

                registry.register("publish_post", handler)
                action = Action(
                    task_id="task-1",
                    name="publish_post",
                    id="action-1",
                )

                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(execute_action, action, registry),
                        executor.submit(execute_action, action, registry),
                    ]
                    outcomes = []
                    for future in futures:
                        try:
                            outcomes.append(("success", future.result()))
                        except ValueError as exc:
                            outcomes.append(("rejected", exc))

                self.assertEqual(
                    [kind for kind, _ in outcomes].count("success"), 1
                )
                self.assertEqual(
                    [kind for kind, _ in outcomes].count("rejected"), 1
                )
                self.assertEqual(calls, ["action-1"])
                self.assertEqual(len(execution_store.load_executions()), 1)
            finally:
                (
                    execution_store.EXECUTIONS_FILE,
                    evidence_store.EVIDENCE_FILE,
                    result_store.RESULTS_FILE,
                ) = original


if __name__ == "__main__":
    unittest.main()
