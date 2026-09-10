"""Authoritative filesystem locations for runtime persistence."""

import os
from pathlib import Path


DATA_DIR = Path(os.environ.get("IXXIMEOW_DATA_DIR", "runtime_data"))


def runtime_file(name: str) -> Path:
    """Return a path inside the configured runtime data directory."""
    if not name or Path(name).name != name:
        raise ValueError("runtime filename must be a non-empty basename")
    return DATA_DIR / name
