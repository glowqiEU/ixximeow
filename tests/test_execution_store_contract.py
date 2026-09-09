import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.execution import Execution
from core.execution_store import (
    find_execution_by_id,
    find_execution_by_idempotency_key,
    load_executions,
    upsert_execution,
)


class TestExecutionStoreContract(unittest.TestCase):
    def test_execution_is_durable_and_reloaded_with_identity(self):
        execution = Execution(action_id="action-1", task_id="task-1")

        with tempfile.TemporaryDirectory() as directory:
            execution_file = Path(directory) / "executions.json"
            with patch("core.execution_store.EXECUTIONS_FILE", execution_file):
                upsert_execution(execution)
                loaded = find_execution_by_id(execution.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, execution.id)
        self.assertEqual(loaded.action_id, execution.action_id)
        self.assertEqual(loaded.idempotency_key, execution.idempotency_key)

    def test_upsert_updates_existing_execution_instead_of_creating_duplicate(self):
        execution = Execution(action_id="action-1", task_id="task-1")

        with tempfile.TemporaryDirectory() as directory:
            execution_file = Path(directory) / "executions.json"
            with patch("core.execution_store.EXECUTIONS_FILE", execution_file):
                upsert_execution(execution)
                execution.transition("running")
                upsert_execution(execution)
                loaded = load_executions()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].id, execution.id)
        self.assertEqual(loaded[0].attempt, 1)
        self.assertEqual(loaded[0].status, "running")

    def test_idempotency_key_resolves_to_same_execution(self):
        execution = Execution(action_id="action-1", task_id="task-1")

        with tempfile.TemporaryDirectory() as directory:
            execution_file = Path(directory) / "executions.json"
            with patch("core.execution_store.EXECUTIONS_FILE", execution_file):
                upsert_execution(execution)
                found = find_execution_by_idempotency_key(
                    execution.idempotency_key
                )

        self.assertIsNotNone(found)
        self.assertEqual(found.id, execution.id)

    def test_duplicate_idempotency_key_cannot_create_second_execution(self):
        first = Execution(action_id="action-1", task_id="task-1")
        second = Execution(
            action_id="action-2",
            task_id="task-2",
            idempotency_key=first.idempotency_key,
        )

        with tempfile.TemporaryDirectory() as directory:
            execution_file = Path(directory) / "executions.json"
            with patch("core.execution_store.EXECUTIONS_FILE", execution_file):
                upsert_execution(first)
                with self.assertRaises(ValueError):
                    upsert_execution(second)

        self.assertNotEqual(first.id, second.id)


if __name__ == "__main__":
    unittest.main()
