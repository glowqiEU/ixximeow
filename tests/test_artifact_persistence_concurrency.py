import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from core.evidence import Evidence
from core.evidence_store import find_evidence_by_result_id, upsert_evidence
from core.models import Result
from core.result_store import find_result_by_execution_id, upsert_result
import core.evidence_store as evidence_store
import core.result_store as result_store


class TestArtifactPersistenceConcurrency(unittest.TestCase):
    def test_concurrent_results_for_same_execution_commit_only_one(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            original = result_store.RESULTS_FILE
            result_store.RESULTS_FILE = root / "results.json"
            try:
                results = [
                    Result(
                        task_id="task-1",
                        action_id="action-1",
                        execution_id="execution-1",
                        success=True,
                        summary=f"result-{index}",
                        id=f"result-{index}",
                    )
                    for index in range(2)
                ]

                def attempt(result):
                    try:
                        upsert_result(result)
                        return "accepted"
                    except ValueError:
                        return "rejected"

                with ThreadPoolExecutor(max_workers=2) as pool:
                    outcomes = list(pool.map(attempt, results))

                self.assertEqual(sorted(outcomes), ["accepted", "rejected"])
                persisted = find_result_by_execution_id("execution-1")
                self.assertIsNotNone(persisted)
            finally:
                result_store.RESULTS_FILE = original

    def test_concurrent_evidence_inserts_do_not_lose_distinct_items(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            original = evidence_store.EVIDENCE_FILE
            evidence_store.EVIDENCE_FILE = root / "evidence.json"
            try:
                evidence = [
                    Evidence(
                        result_id="result-1",
                        execution_id="execution-1",
                        kind="execution_output",
                        claim=f"claim-{index}",
                        value=index,
                        content=f"evidence-{index}",
                        id=f"evidence-{index}",
                    )
                    for index in range(8)
                ]

                with ThreadPoolExecutor(max_workers=8) as pool:
                    list(pool.map(upsert_evidence, evidence))

                persisted = find_evidence_by_result_id("result-1")
                self.assertEqual(len(persisted), 8)
                self.assertEqual(
                    {item.id for item in persisted},
                    {f"evidence-{index}" for index in range(8)},
                )
            finally:
                evidence_store.EVIDENCE_FILE = original


if __name__ == "__main__":
    unittest.main()
