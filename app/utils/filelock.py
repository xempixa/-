from __future__ import annotations

import os
from pathlib import Path


class SingleInstanceLock:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False

        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
        except Exception:
            try:
                self.path.unlink(missing_ok=True)
            finally:
                raise

        return True

    def release(self) -> None:
        self.path.unlink(missing_ok=True)
