import json
from pathlib import Path

from .memory import Memory


MEMORY_FILE = Path("memory.json")


def save_memories(memories: list[Memory]) -> None:
    MEMORY_FILE.write_text(
        json.dumps([memory.__dict__ for memory in memories], indent=2),
        encoding="utf-8",
    )


def load_memories() -> list[Memory]:
    if not MEMORY_FILE.exists():
        return []

    data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    return [Memory(**item) for item in data]
