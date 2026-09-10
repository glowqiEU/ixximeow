import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from core.models import Task
from core.task_store import claim_task_running, load_tasks, save_tasks


class TestTaskClaimConcurrency(unittest.TestCase):
    def test_only_one_resume_can_claim_waiting_approval_task(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tasks_file = Path(tmpdir) / "tasks.json"
            task = Task(
                title="publish post",
                status="waiting_approval",
                approval_id="approval-1",
                required_level="publish",
            )

            with patch("core.task_store.TASKS_FILE", tasks_file):
                save_tasks([task])

                def claim():
                    try:
                        claimed = claim_task_running(task.id, "approval-1")
                        return ("claimed", claimed.status)
                    except ValueError as exc:
                        return ("rejected", str(exc))

                with ThreadPoolExecutor(max_workers=2) as pool:
                    results = list(pool.map(lambda _: claim(), range(2)))

                self.assertEqual(
                    [result[0] for result in results].count("claimed"), 1
                )
                self.assertEqual(
                    [result[0] for result in results].count("rejected"), 1
                )
                persisted = load_tasks()
                self.assertEqual(len(persisted), 1)
                self.assertEqual(persisted[0].status, "running")


if __name__ == "__main__":
    unittest.main()
