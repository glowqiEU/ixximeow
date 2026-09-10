import unittest

from core.evidence import Evidence


class TestEvidence(unittest.TestCase):
    def test_evidence_has_explicit_provenance(self):
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="external_observation",
            content="post appears visible",
            verified=True,
        )

        self.assertEqual(evidence.result_id, "result-1")
        self.assertEqual(evidence.execution_id, "execution-1")
        self.assertEqual(evidence.kind, "external_observation")
        self.assertEqual(evidence.content, "post appears visible")
        self.assertTrue(evidence.verified)
        self.assertIsNotNone(evidence.id)

    def test_evidence_rejects_empty_provenance(self):
        with self.assertRaises(ValueError):
            Evidence(
                result_id="",
                execution_id="execution-1",
                kind="external_observation",
                content="post appears visible",
            )

        with self.assertRaises(ValueError):
            Evidence(
                result_id="result-1",
                execution_id="",
                kind="external_observation",
                content="post appears visible",
            )

    def test_evidence_rejects_empty_observation(self):
        with self.assertRaises(ValueError):
            Evidence(
                result_id="result-1",
                execution_id="execution-1",
                kind="external_observation",
                content="",
            )


if __name__ == "__main__":
    unittest.main()
