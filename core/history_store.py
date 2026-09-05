import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .history import HistoryEvent


HISTORY_FILE = Path("history.json")


def append_event(event: HistoryEvent) -> None:
    events = load_events()
    events.append(event)

    HISTORY_FILE.write_text(
        json.dumps(
            [asdict(item) for item in events],
            indent=2,
        ),
        encoding="utf-8",
    )


def load_events(limit: Optional[int] = None) -> list[HistoryEvent]:
    if not HISTORY_FILE.exists():
        return []

    data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    events = [HistoryEvent(**item) for item in data]

    if limit is not None:
        return events[-limit:]

    return events
