from __future__ import annotations

from pathlib import Path


class SingleInstanceLock:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def acquire(self) -> bool:
        if self.path.exists():
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("locked", encoding="utf-8")
        return True

    def release(self) -> None:
        if self.path.exists():
            self.path.unlink()
