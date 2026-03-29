from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Creator(Base):
    __tablename__ = "creators"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    homepage_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Dynamic(Base):
    __tablename__ = "dynamics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dynamic_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    uid: Mapped[int | None] = mapped_column(ForeignKey("creators.uid"), nullable=True)
    dynamic_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    publish_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_json: Mapped[str] = mapped_column(Text)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    creator: Mapped["Creator | None"] = relationship()


class DynamicComment(Base):
    __tablename__ = "dynamic_comments"
    __table_args__ = (UniqueConstraint("comment_id", name="uq_dynamic_comment_comment_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    comment_id: Mapped[str] = mapped_column(String(64), index=True)
    dynamic_id: Mapped[str] = mapped_column(String(64), index=True)
    root_comment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    parent_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    publish_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    raw_json: Mapped[str] = mapped_column(Text)


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bvid: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    aid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uid: Mapped[int | None] = mapped_column(ForeignKey("creators.uid"), nullable=True)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    publish_ts: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_charge_only: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_json: Mapped[str] = mapped_column(Text)

    creator: Mapped["Creator | None"] = relationship()


class DownloadTask(Base):
    __tablename__ = "download_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bvid: Mapped[str] = mapped_column(String(32), index=True)
    url: Mapped[str] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    file_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SyncCheckpoint(Base):
    __tablename__ = "sync_checkpoints"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scope: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    cursor: Mapped[str | None] = mapped_column(String(512), nullable=True)
    last_item_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
