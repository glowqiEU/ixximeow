from .memory import Memory


def retrieve_memories(
    query: str,
    memories: list[Memory],
) -> list[Memory]:
    query_words = set(query.lower().split())

    return [
        memory
        for memory in memories
        if query_words.intersection(memory.content.lower().split())
    ]
