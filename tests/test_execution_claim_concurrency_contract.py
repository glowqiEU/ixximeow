import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier

from core.action import Action
from core.action_registry import ActionRegistry
from core.execution_service import reserve_execution, execute_reserved_action
from core.execution_store import load_executions


class TestExecutionClaimConcurrencyContract(unittest.TestCase):
    def test_only_one_worker_can_claim_pending_execution(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            import core.execution_store as execution_store
            import core.evidence_store as evidence_store
            import core.result_store as result_store

            original = (
                execution_store.EXECUTIONS_FILE,
                evidence_store.EVIDENCE_FILE,
                result_store.RESULTS_FILE,
            )
            execution_store.EXECUTIONS_FILE = root / "executions.json"
            evidence_store.EVIDENCE_FILE = root / "evidence.json"
            result_store.RESULTS_FILE = root / "results.json"
            try:
                action = Action(task_id="task-1", name="publish_post", id="action-1")
                execution = reserve_execution(action)
                registry = ActionRegistry()
                calls = []
                barrier = Barrier(2)

                def handler(current_action):
                    calls.append(current_action.id)
                    return {"summary": "published"}

                registry.register("publish_post", handler)

                def worker():
                    barrier.wait()
                    try:
                        execute_reserved_action(action, execution, registry)
                        return "succeeded"
                    except ValueError:
                        return "rejected"

                with ThreadPoolExecutor(max_workers=2) as pool:
                    outcomes = list(pool.map(lambda _: worker(), range(2)))

                self.assertEqual(sorted(outcomes), ["rejected", "succeeded"])
                self.assertEqual(calls, ["action-1"])
                persisted = load_executions()
                self.assertEqual(len(persisted), 1)
                self.assertEqual(persisted[0].status, "succeeded")
                self.assertEqual(persisted[0].attempt, 1)
            finally:
                (
                    execution_store.EXECUTIONS_FILE,
                    evidence_store.EVIDENCE_FILE,
                    result_store.RESULTS_FILE,
                ) = original


if __name__ == "__main__":
    unittest.main()
