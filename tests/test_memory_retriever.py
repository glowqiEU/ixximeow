import unittest

from core.memory import Memory
from core.memory_retriever import retrieve_memories


class TestMemoryRetriever(unittest.TestCase):

    def test_retrieves_relevant_memories(self):
        memories = [
            Memory(
                content="flash photos perform better",
                source="observed_result",
                confidence=0.8,
            ),
            Memory(
                content="morning posts get fewer replies",
                source="observed_result",
                confidence=0.7,
            ),
            Memory(
                content="people respond well to direct questions",
                source="observed_result",
                confidence=0.9,
            ),
        ]

        results = retrieve_memories(
            query="flash photos",
            memories=memories,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "flash photos perform better")


if __name__ == "__main__":
    unittest.main()
