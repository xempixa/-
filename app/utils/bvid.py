from __future__ import annotations

import re

_BVID_PATTERN = re.compile(r"^BV[0-9A-Za-z]{10}$")


def is_valid_bvid(value: str) -> bool:
    return bool(_BVID_PATTERN.fullmatch(value.strip()))


def normalize_bvid(value: str) -> str:
    return value.strip()
