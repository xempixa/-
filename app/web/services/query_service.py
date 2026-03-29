from __future__ import annotations

from math import ceil

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Creator, DownloadTask, Dynamic, Video


class QueryService:
    async def list_creators(self, session: AsyncSession) -> list[Creator]:
        result = await session.scalars(select(Creator).order_by(Creator.uid.asc()))
        return list(result.all())

    async def list_dynamics(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        uid: int | None = None,
        keyword: str | None = None,
    ) -> tuple[list[Dynamic], int]:
        stmt = select(Dynamic)
        if uid is not None:
            stmt = stmt.where(Dynamic.uid == uid)
        if keyword:
            stmt = stmt.where(Dynamic.content_text.ilike(f"%{keyword}%"))

        total = await session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = stmt.order_by(Dynamic.id.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list((await session.scalars(stmt)).all())
        return items, total

    async def list_videos(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        uid: int | None = None,
        keyword: str | None = None,
        charge_only: bool | None = None,
    ) -> tuple[list[Video], int]:
        stmt = select(Video)
        if uid is not None:
            stmt = stmt.where(Video.uid == uid)
        if keyword:
            stmt = stmt.where(or_(Video.title.ilike(f"%{keyword}%"), Video.description.ilike(f"%{keyword}%")))
        if charge_only is not None:
            stmt = stmt.where(Video.is_charge_only == charge_only)

        total = await session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = stmt.order_by(Video.id.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list((await session.scalars(stmt)).all())
        return items, total

    async def list_download_tasks(
        self,
        session: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        bvid: str | None = None,
        uid: int | None = None,
    ) -> tuple[list[DownloadTask], int]:
        stmt = select(DownloadTask)
        if status:
            stmt = stmt.where(DownloadTask.status == status)
        if bvid:
            stmt = stmt.where(DownloadTask.bvid.ilike(f"%{bvid}%"))
        if uid is not None:
            stmt = stmt.where(DownloadTask.source_uid == uid)

        total = await session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = stmt.order_by(DownloadTask.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list((await session.scalars(stmt)).all())
        return items, total

    @staticmethod
    def make_meta(page: int, page_size: int, total: int) -> dict:
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if page_size > 0 else 0,
        }
