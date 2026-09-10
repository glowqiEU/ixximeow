import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.evidence import Evidence
from core.evidence_store import load_evidence, save_evidence


class TestEvidenceStore(unittest.TestCase):
    def test_save_and_load_preserves_evidence(self):
        evidence = Evidence(
            result_id="result-1",
            execution_id="execution-1",
            kind="text",
            content="completed",
            verified=True,
            id="evidence-1",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "evidence.json"
            with patch("core.evidence_store.EVIDENCE_FILE", path):
                save_evidence([evidence])
                loaded = load_evidence()

        self.assertEqual(loaded, [evidence])

    def test_load_empty_store_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "evidence.json"
            with patch("core.evidence_store.EVIDENCE_FILE", path):
                self.assertEqual(load_evidence(), [])


if __name__ == "__main__":
    unittest.main()
