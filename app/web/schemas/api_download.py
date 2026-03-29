from __future__ import annotations

from pydantic import BaseModel, Field


class EnqueueDownloadRequest(BaseModel):
    bvid: str = Field(min_length=12, max_length=12, pattern=r"^BV[0-9A-Za-z]{10}$")
    priority: int = Field(default=100, ge=1, le=1000)
    source_uid: int | None = Field(default=None, ge=1)
    note: str | None = Field(default=None, max_length=500)


class RetryDownloadRequest(BaseModel):
    reset_retry_count: bool = False


class CancelDownloadRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=200)
