import json
from pathlib import Path
from typing import Any

from app.config import settings


def storage_state_exists(path: Path | None = None) -> bool:
    target = path or settings.storage_state_path
    return target.exists() and target.stat().st_size > 0


def load_storage_state(path: Path | None = None) -> dict[str, Any]:
    target = path or settings.storage_state_path
    if not target.exists():
        raise FileNotFoundError(f"storage state not found: {target}")
    return json.loads(target.read_text(encoding="utf-8"))
