from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud_download import create_download_task
from app.db.download_status import DOWNLOAD_STATUS_ACTIVE_DEDUP, DOWNLOAD_STATUS_RETRYABLE
from app.db.models import DownloadTask
from app.utils.bvid import is_valid_bvid, normalize_bvid


class DownloadAdminService:
    async def enqueue(
        self,
        session: AsyncSession,
        bvid: str,
        priority: int = 100,
        source_uid: int | None = None,
        note: str | None = None,
    ) -> tuple[bool, str]:
        bvid = normalize_bvid(bvid)
        if not is_valid_bvid(bvid):
            return False, "invalid bvid"

        existing = await session.scalar(
            select(DownloadTask).where(
                DownloadTask.bvid == bvid,
                DownloadTask.status.in_(sorted(DOWNLOAD_STATUS_ACTIVE_DEDUP)),
            )
        )
        if existing:
            return False, "task already exists"

        await create_download_task(
            session=session,
            bvid=bvid,
            url=f"https://www.bilibili.com/video/{bvid}",
            priority=priority,
            source_uid=source_uid,
            note=note,
        )
        await session.commit()
        return True, "enqueued"

    async def retry_task(
        self,
        session: AsyncSession,
        task_id: int,
        reset_retry_count: bool = False,
    ) -> tuple[bool, str]:
        task = await session.get(DownloadTask, task_id)
        if not task:
            return False, "task not found"
        if task.status not in DOWNLOAD_STATUS_RETRYABLE:
            return False, f"status {task.status} not retryable"

        task.status = "pending"
        task.error_message = None
        task.next_retry_at = None
        task.finished_at = None
        task.updated_at = datetime.utcnow()
        task.cancel_requested = False
        task.manual_retry_count = (task.manual_retry_count or 0) + 1
        task.locked_by = None
        task.lock_expire_at = None
        if reset_retry_count:
            task.retry_count = 0

        await session.commit()
        return True, "task reset to pending"

    async def cancel_task(self, session: AsyncSession, task_id: int, reason: str | None = None) -> tuple[bool, str]:
        task = await session.get(DownloadTask, task_id)
        if not task:
            return False, "task not found"

        task.cancel_requested = True
        if task.status in {"pending", "retry_wait"}:
            task.status = "cancelled"
            task.finished_at = datetime.utcnow()
            task.locked_by = None
            task.lock_expire_at = None
        if reason:
            task.error_message = reason

        task.updated_at = datetime.utcnow()
        await session.commit()
        return True, "task cancelled"
