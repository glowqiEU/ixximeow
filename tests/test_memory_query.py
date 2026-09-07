import unittest

from core.context import AgentContext
from core.memory_query import build_memory_query


class TestMemoryQuery(unittest.TestCase):
    def test_build_memory_query_uses_active_task(self):
        context = AgentContext(task="create X content")

        query = build_memory_query(context)

        self.assertEqual(query, "create X content")

    def test_build_memory_query_returns_none_without_task(self):
        context = AgentContext()

        query = build_memory_query(context)

        self.assertIsNone(query)


if __name__ == "__main__":
    unittest.main()
