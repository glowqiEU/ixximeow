import unittest

from core.memory import Memory


class TestMemory(unittest.TestCase):
    def test_memory_has_stable_id(self):
        memory = Memory(
            content="flash photos perform better",
            source="observed_result",
            confidence=0.8,
        )

        self.assertIsNotNone(memory.id)
        self.assertEqual(memory.content, "flash photos perform better")
        self.assertEqual(memory.source, "observed_result")
        self.assertEqual(memory.confidence, 0.8)
        self.assertIsNotNone(memory.created_at)


if __name__ == "__main__":
    unittest.main()
