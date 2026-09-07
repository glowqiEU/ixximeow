import unittest

from core.models import Task


class TestTaskPermissions(unittest.TestCase):
    def test_task_defaults_to_execute_level(self):
        task = Task(title="generate image")
        self.assertEqual(task.required_level, "execute")

    def test_task_can_require_publish_level(self):
        task = Task(
            title="publish post",
            required_level="publish",
        )
        self.assertEqual(task.required_level, "publish")


if __name__ == "__main__":
    unittest.main()
