import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from core.persistence import load_json, load_record, load_record_list, save_json


class TestPersistence(unittest.TestCase):
    def test_save_json_is_readable(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"

            save_json(path, {"status": "active", "count": 2})

            self.assertEqual(
                load_json(path),
                {"status": "active", "count": 2},
            )

    def test_missing_file_returns_default(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "missing.json"

            self.assertEqual(load_json(path, []), [])

    def test_corrupt_json_raises_value_error(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "corrupt.json"
            path.write_text("{not valid json", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_json(path)

    def test_save_json_replaces_target_atomically(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps({"old": True}), encoding="utf-8")

            save_json(path, {"new": True})

            self.assertEqual(load_json(path), {"new": True})
            self.assertFalse(path.with_name("state.json.tmp").exists())

    def test_record_list_rejects_wrong_top_level_shape(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "records.json"
            save_json(path, {"not": "a list"})
            with self.assertRaisesRegex(ValueError, "invalid record collection"):
                load_record_list(path)

    def test_record_list_rejects_non_mapping_items(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "records.json"
            save_json(path, [{"valid": True}, "invalid"])
            with self.assertRaisesRegex(ValueError, "invalid record collection"):
                load_record_list(path)

    def test_single_record_rejects_wrong_shape(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            save_json(path, [])
            with self.assertRaisesRegex(ValueError, "invalid record"):
                load_record(path)

    def test_failed_replace_preserves_target_and_removes_temporary_file(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            save_json(path, {"stable": True})

            with patch.object(Path, "replace", side_effect=OSError("disk failure")):
                with self.assertRaisesRegex(OSError, "disk failure"):
                    save_json(path, {"partial": True})

            self.assertEqual(load_json(path), {"stable": True})
            self.assertFalse(path.with_name("state.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
