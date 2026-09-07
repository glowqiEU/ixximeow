import unittest

from core.history import HistoryEvent
from core import history_store


class TestHistoryStore(unittest.TestCase):
    def test_append_and_load_event(self):
        original_file = history_store.HISTORY_FILE

        try:
            history_store.HISTORY_FILE = original_file.parent / "test_history.json"
            history_store.HISTORY_FILE.unlink(missing_ok=True)

            event = HistoryEvent(
                event_type="task_executed",
                summary="test event",
                decision_id="decision-1",
                task_id="task-1",
                result_id="result-1",
            )

            history_store.append_event(event)

            events = history_store.load_events()

            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].event_type, "task_executed")
            self.assertEqual(events[0].task_id, "task-1")

        finally:
            history_store.HISTORY_FILE.unlink(missing_ok=True)
            history_store.HISTORY_FILE = original_file


if __name__ == "__main__":
    unittest.main()
