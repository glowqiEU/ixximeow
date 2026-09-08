import unittest

from core.context import AgentContext
from core.memory_query import build_memory_query
from core.models import Task


class TestMemoryQueryContract(unittest.TestCase):
    def test_query_uses_task_title(self):
        task = Task(title="create X content", id="task-123")
        context = AgentContext(task=task)

        self.assertEqual(build_memory_query(context), "create X content")
        self.assertNotEqual(build_memory_query(context), task.id)


if __name__ == "__main__":
    unittest.main()
