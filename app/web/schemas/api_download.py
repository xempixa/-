from __future__ import annotations

from pydantic import BaseModel, Field


class EnqueueDownloadRequest(BaseModel):
    bvid: str = Field(min_length=3, max_length=32)
    priority: int = 100
    source_uid: int | None = None
    note: str | None = None


class RetryDownloadRequest(BaseModel):
    reset_retry_count: bool = False


class CancelDownloadRequest(BaseModel):
    reason: str | None = None
