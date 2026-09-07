from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def new_memory_id() -> str:
    return str(uuid4())


@dataclass
class Memory:
    content: str
    source: str
    confidence: float = 0.5
    id: str = field(default_factory=new_memory_id)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
