from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DownloadTask


async def create_download_task(
    session: AsyncSession,
    bvid: str,
    url: str,
    priority: int = 100,
) -> DownloadTask:
    obj = DownloadTask(
        bvid=bvid,
        url=url,
        priority=priority,
        status="pending",
    )
    session.add(obj)
    return obj


async def get_pending_tasks(session: AsyncSession, limit: int = 5) -> list[DownloadTask]:
    result = await session.scalars(
        select(DownloadTask)
        .where(DownloadTask.status.in_(["pending", "retry_wait"]))
        .order_by(DownloadTask.priority.asc(), DownloadTask.created_at.asc())
        .limit(limit)
    )
    return list(result.all())


async def mark_task_running(session: AsyncSession, task: DownloadTask) -> None:
    task.status = "running"
    task.last_run_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()


async def mark_task_success(
    session: AsyncSession, task: DownloadTask, file_path: str | None = None
) -> None:
    task.status = "success"
    task.file_path = file_path
    task.finished_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    task.error_message = None


async def mark_task_retry(session: AsyncSession, task: DownloadTask, error_message: str) -> None:
    task.retry_count += 1
    task.updated_at = datetime.utcnow()
    task.error_message = error_message

    if task.retry_count >= task.max_retries:
        task.status = "failed"
        task.finished_at = datetime.utcnow()
    else:
        task.status = "retry_wait"
