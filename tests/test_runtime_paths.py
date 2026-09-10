import tempfile
import unittest
from pathlib import Path

from core.persistence import load_json, save_json
from core.runtime_paths import DATA_DIR, runtime_file


class TestRuntimePaths(unittest.TestCase):
    def test_default_runtime_files_share_authoritative_directory(self):
        self.assertEqual(runtime_file("state.json"), DATA_DIR / "state.json")

    def test_runtime_file_rejects_path_escape(self):
        for name in ("", "../state.json", "nested/state.json"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    runtime_file(name)

    def test_save_json_creates_runtime_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "state.json"
            save_json(path, {"status": "active"})
            self.assertEqual(load_json(path), {"status": "active"})


if __name__ == "__main__":
    unittest.main()
