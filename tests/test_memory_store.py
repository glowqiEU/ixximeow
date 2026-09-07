import unittest

from core.memory import Memory
from core.memory_store import load_memories, save_memories


class TestMemoryStore(unittest.TestCase):
    def test_save_and_load_memory(self):
        memories = [
            Memory(
                content="flash photos perform better",
                source="observed_result",
                confidence=0.8,
            )
        ]

        save_memories(memories)
        loaded = load_memories()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].content, "flash photos perform better")
        self.assertEqual(loaded[0].source, "observed_result")
        self.assertEqual(loaded[0].confidence, 0.8)
        self.assertEqual(loaded[0].id, memories[0].id)


if __name__ == "__main__":
    unittest.main()
