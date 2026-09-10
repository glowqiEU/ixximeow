import unittest

from core.evidence_recorder import record_evidence
from core.models import Result


class TestEvidenceRecorder(unittest.TestCase):
    def test_record_evidence_derives_provenance_from_result(self):
        result = Result(
            task_id="task-1",
            action_id="action-1",
            execution_id="execution-1",
            success=True,
            summary="platform accepted publication",
            id="result-1",
        )

        evidence = record_evidence(
            result,
            kind="external_observation",
            content="post appears visible",
        )

        self.assertEqual(evidence.result_id, result.id)
        self.assertEqual(evidence.execution_id, result.execution_id)
        self.assertEqual(evidence.kind, "external_observation")
        self.assertEqual(evidence.content, "post appears visible")
        self.assertFalse(evidence.verified)

    def test_record_evidence_rejects_result_without_execution_provenance(self):
        result = Result(
            task_id="task-1",
            action_id="action-1",
            success=True,
            summary="platform accepted publication",
            id="result-1",
        )

        with self.assertRaises(ValueError):
            record_evidence(
                result,
                kind="external_observation",
                content="post appears visible",
            )

    def test_record_evidence_rejects_empty_kind(self):
        result = Result(
            task_id="task-1",
            execution_id="execution-1",
            success=True,
            summary="completed",
            id="result-1",
        )

        with self.assertRaises(ValueError):
            record_evidence(result, kind="   ", content="observation")

    def test_record_evidence_rejects_empty_content(self):
        result = Result(
            task_id="task-1",
            execution_id="execution-1",
            success=True,
            summary="completed",
            id="result-1",
        )

        with self.assertRaises(ValueError):
            record_evidence(result, kind="external_observation", content="   ")


if __name__ == "__main__":
    unittest.main()
