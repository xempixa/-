from datetime import datetime

from pydantic import BaseModel


class DynamicItem(BaseModel):
    dynamic_id: str
    uid: int | None = None
    dynamic_type: str | None = None
    publish_ts: datetime | None = None
    content_text: str | None = None
    raw_json: str
