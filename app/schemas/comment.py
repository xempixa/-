from datetime import datetime

from pydantic import BaseModel


class CommentItem(BaseModel):
    comment_id: str
    dynamic_id: str
    root_comment_id: str | None = None
    parent_id: str | None = None
    user_name: str | None = None
    content: str | None = None
    like_count: int = 0
    publish_ts: datetime | None = None
    raw_json: str
