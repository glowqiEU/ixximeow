import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .history import HistoryEvent
from .persistence import load_json, save_json


HISTORY_FILE = Path("history.json")


def append_event(event: HistoryEvent) -> None:
    events = load_events()
    events.append(event)
    save_json(HISTORY_FILE, [asdict(item) for item in events])


def load_events(limit: Optional[int] = None) -> list[HistoryEvent]:
    data = load_json(HISTORY_FILE, [])
    events = [HistoryEvent(**item) for item in data]

    if limit is not None:
        return events[-limit:]

    return events
