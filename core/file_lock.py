from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import fcntl


@contextmanager
def exclusive_file_lock(path: Path) -> Iterator[None]:
    """Serialize cooperating processes through an advisory filesystem lock."""
    lock_path = path.with_name(path.name + ".lock")
    with lock_path.open("a+") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
