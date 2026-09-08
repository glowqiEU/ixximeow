import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from core.persistence import load_json, save_json


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


if __name__ == "__main__":
    unittest.main()
