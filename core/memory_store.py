from .memory import Memory
from .persistence import load_json, save_json
from .runtime_paths import runtime_file


MEMORY_FILE = runtime_file("memory.json")


def save_memories(memories: list[Memory]) -> None:
    save_json(MEMORY_FILE, [memory.__dict__ for memory in memories])


def load_memories() -> list[Memory]:
    data = load_json(MEMORY_FILE, [])
    return [Memory(**item) for item in data]
