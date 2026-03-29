from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Dynamic, DynamicComment, SyncCheckpoint, Video


class DynamicRepo:
    @staticmethod
    async def get_by_dynamic_id(session: AsyncSession, dynamic_id: str) -> Dynamic | None:
        return await session.scalar(select(Dynamic).where(Dynamic.dynamic_id == dynamic_id))

    @staticmethod
    async def upsert(session: AsyncSession, payload: dict) -> Dynamic:
        existing = await DynamicRepo.get_by_dynamic_id(session, payload["dynamic_id"])
        if existing:
            existing.uid = payload.get("uid")
            existing.dynamic_type = payload.get("dynamic_type")
            existing.content_text = payload.get("content_text")
            existing.raw_json = payload.get("raw_json")
            existing.last_seen_at = datetime.utcnow()
            return existing

        obj = Dynamic(**payload)
        session.add(obj)
        return obj


class CommentRepo:
    @staticmethod
    async def get_by_comment_id(session: AsyncSession, comment_id: str) -> DynamicComment | None:
        return await session.scalar(
            select(DynamicComment).where(DynamicComment.comment_id == comment_id)
        )

    @staticmethod
    async def upsert(session: AsyncSession, payload: dict) -> DynamicComment:
        existing = await CommentRepo.get_by_comment_id(session, payload["comment_id"])
        if existing:
            existing.content = payload.get("content")
            existing.like_count = payload.get("like_count", 0)
            existing.raw_json = payload.get("raw_json")
            return existing

        obj = DynamicComment(**payload)
        session.add(obj)
        return obj


class VideoRepo:
    @staticmethod
    async def get_by_bvid(session: AsyncSession, bvid: str) -> Video | None:
        return await session.scalar(select(Video).where(Video.bvid == bvid))

    @staticmethod
    async def upsert(session: AsyncSession, payload: dict) -> Video:
        existing = await VideoRepo.get_by_bvid(session, payload["bvid"])
        if existing:
            for key, value in payload.items():
                setattr(existing, key, value)
            return existing

        obj = Video(**payload)
        session.add(obj)
        return obj


class CheckpointRepo:
    @staticmethod
    async def get(session: AsyncSession, scope: str) -> SyncCheckpoint | None:
        return await session.scalar(select(SyncCheckpoint).where(SyncCheckpoint.scope == scope))

    @staticmethod
    async def save(
        session: AsyncSession,
        scope: str,
        cursor: str | None = None,
        last_item_id: str | None = None,
    ) -> SyncCheckpoint:
        obj = await CheckpointRepo.get(session, scope)
        if obj:
            obj.cursor = cursor
            obj.last_item_id = last_item_id
            obj.updated_at = datetime.utcnow()
            return obj

        obj = SyncCheckpoint(
            scope=scope,
            cursor=cursor,
            last_item_id=last_item_id,
        )
        session.add(obj)
        return obj
