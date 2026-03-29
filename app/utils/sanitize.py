from __future__ import annotations

import re

_INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|\r\n]+')


def sanitize_filename(name: str) -> str:
    cleaned = _INVALID_FILENAME_CHARS.sub("_", name).strip()
    return cleaned or "untitled"
