from __future__ import annotations

import random
from datetime import datetime, timedelta


def compute_next_retry_at(
    retry_count: int,
    base_delay_seconds: int = 300,
    max_delay_seconds: int = 86400,
    jitter_seconds: int = 60,
) -> datetime:
    delay = min(base_delay_seconds * (2 ** max(retry_count - 1, 0)), max_delay_seconds)
    jitter = random.randint(0, max(0, jitter_seconds))
    return datetime.utcnow() + timedelta(seconds=delay + jitter)
