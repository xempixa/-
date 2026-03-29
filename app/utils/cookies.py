from __future__ import annotations

from pathlib import Path

from app.config import settings


def get_default_cookies_path() -> Path:
    return settings.data_dir / "cookies.txt"
