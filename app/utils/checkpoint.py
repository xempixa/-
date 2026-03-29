from __future__ import annotations


def build_checkpoint_scope(prefix: str, target_id: str | int) -> str:
    return f"{prefix}:{target_id}"
