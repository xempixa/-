from datetime import datetime

from pydantic import BaseModel


class VideoItem(BaseModel):
    bvid: str
    aid: int | None = None
    cid: int | None = None
    uid: int | None = None
    title: str | None = None
    description: str | None = None
    publish_ts: datetime | None = None
    duration_seconds: int | None = None
    is_charge_only: bool = False
    raw_json: str
