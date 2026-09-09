import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.evidence import Evidence
from core.evidence_store import find_evidence_by_id, find_evidence_by_result_id, upsert_evidence
from core.models import Result
from core.outcome import Outcome
from core.outcome_store import find_outcome_by_id, find_outcome_by_task_id, upsert_outcome
from core.result_store import find_result_by_execution_id, find_result_by_id, upsert_result


class TestArtifactStoresContract(unittest.TestCase):
    def test_result_store_persists_and_indexes_result(self):
        result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="accepted",
            id="result-1",
        )

        with tempfile.TemporaryDirectory() as directory:
            result_file = Path(directory) / "results.json"
            with patch("core.result_store.RESULTS_FILE", result_file):
                upsert_result(result)
                by_id = find_result_by_id("result-1")
                by_execution = find_result_by_execution_id("execution-1")

        self.assertEqual(by_id.id, "result-1")
        self.assertEqual(by_execution.id, "result-1")

    def test_evidence_store_persists_and_indexes_result(self):
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="external_observation",
            claim="post_visible",
            value=True,
            content="post is visible",
            id="evidence-1",
        )

        with tempfile.TemporaryDirectory() as directory:
            evidence_file = Path(directory) / "evidence.json"
            with patch("core.evidence_store.EVIDENCE_FILE", evidence_file):
                upsert_evidence(evidence)
                by_id = find_evidence_by_id("evidence-1")
                by_result = find_evidence_by_result_id("result-1")

        self.assertEqual(by_id.id, "evidence-1")
        self.assertEqual([item.id for item in by_result], ["evidence-1"])

    def test_outcome_store_persists_and_indexes_task(self):
        outcome = Outcome(
            decision_id="decision-1",
            task_id="task-1",
            status="achieved",
            summary="all criteria passed",
            result_ids=["result-1"],
            evidence_ids=["evidence-1"],
            id="outcome-1",
        )

        with tempfile.TemporaryDirectory() as directory:
            outcome_file = Path(directory) / "outcomes.json"
            with patch("core.outcome_store.OUTCOMES_FILE", outcome_file):
                upsert_outcome(outcome)
                by_id = find_outcome_by_id("outcome-1")
                by_task = find_outcome_by_task_id("task-1")

        self.assertEqual(by_id.id, "outcome-1")
        self.assertEqual(by_task.id, "outcome-1")

    def test_outcome_store_upsert_does_not_duplicate_identity(self):
        outcome = Outcome(
            decision_id="decision-1",
            task_id="task-1",
            status="uncertain",
            summary="awaiting evidence",
            id="outcome-1",
        )

        with tempfile.TemporaryDirectory() as directory:
            outcome_file = Path(directory) / "outcomes.json"
            with patch("core.outcome_store.OUTCOMES_FILE", outcome_file):
                upsert_outcome(outcome)
                outcome.summary = "evidence received"
                upsert_outcome(outcome)
                found = find_outcome_by_id("outcome-1")

        self.assertEqual(found.summary, "evidence received")


if __name__ == "__main__":
    unittest.main()
