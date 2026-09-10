import json
from pathlib import Path
from typing import Any, Optional


def save_json(path: Path, data: Any) -> None:
    """Persist JSON atomically so interrupted writes do not corrupt the target."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(path.name + ".tmp")
    temporary_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary_path.replace(path)


def load_json(path: Path, default: Optional[Any] = None) -> Any:
    """Load JSON, returning default only when the persistence file is absent."""
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"invalid persistence file: {path}") from exc
