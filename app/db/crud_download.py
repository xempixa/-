from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DownloadTask
from app.utils.backoff import compute_next_retry_at


async def create_download_task(
    session: AsyncSession,
    bvid: str,
    url: str,
    priority: int = 100,
    source_uid: int | None = None,
    note: str | None = None,
) -> DownloadTask:
    obj = DownloadTask(
        bvid=bvid,
        url=url,
        priority=priority,
        source_uid=source_uid,
        note=note,
        status="pending",
    )
    session.add(obj)
    return obj


async def get_runnable_tasks(session: AsyncSession, limit: int = 5) -> list[DownloadTask]:
    now = datetime.utcnow()
    result = await session.scalars(
        select(DownloadTask)
        .where(
            or_(
                DownloadTask.status == "pending",
                and_(
                    DownloadTask.status == "retry_wait",
                    DownloadTask.next_retry_at.is_not(None),
                    DownloadTask.next_retry_at <= now,
                ),
            ),
            or_(
                DownloadTask.lock_expire_at.is_(None),
                DownloadTask.lock_expire_at <= now,
            ),
        )
        .order_by(DownloadTask.priority.asc(), DownloadTask.created_at.asc())
        .limit(limit)
    )
    return list(result.all())


async def try_claim_task(
    session: AsyncSession,
    task_id: int,
    worker_id: str,
    lock_ttl_seconds: int = 600,
) -> bool:
    now = datetime.utcnow()
    lock_expire_at = now + timedelta(seconds=lock_ttl_seconds)
    result = await session.execute(
        update(DownloadTask)
        .where(
            DownloadTask.id == task_id,
            or_(
                DownloadTask.status == "pending",
                and_(
                    DownloadTask.status == "retry_wait",
                    DownloadTask.next_retry_at.is_not(None),
                    DownloadTask.next_retry_at <= now,
                ),
            ),
            or_(
                DownloadTask.lock_expire_at.is_(None),
                DownloadTask.lock_expire_at <= now,
            ),
        )
        .values(
            status="running",
            last_run_at=now,
            updated_at=now,
            locked_by=worker_id,
            lock_expire_at=lock_expire_at,
        )
    )
    return result.rowcount == 1


async def mark_task_running(
    session: AsyncSession,
    task: DownloadTask,
    worker_id: str | None = None,
    lock_ttl_seconds: int = 600,
) -> None:
    task.status = "running"
    task.last_run_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    task.locked_by = worker_id
    task.lock_expire_at = datetime.utcnow() + timedelta(seconds=lock_ttl_seconds)


async def mark_task_success(
    session: AsyncSession,
    task: DownloadTask,
    file_path: str | None = None,
) -> None:
    task.status = "success"
    task.file_path = file_path
    task.finished_at = datetime.utcnow()
    task.updated_at = datetime.utcnow()
    task.error_message = None
    task.next_retry_at = None
    task.locked_by = None
    task.lock_expire_at = None


async def mark_task_retry(
    session: AsyncSession,
    task: DownloadTask,
    error_message: str,
    base_delay_seconds: int = 300,
    max_delay_seconds: int = 86400,
    jitter_seconds: int = 60,
) -> None:
    task.retry_count += 1
    task.updated_at = datetime.utcnow()
    task.error_message = error_message
    task.locked_by = None
    task.lock_expire_at = None

    if task.retry_count >= task.max_retries:
        task.status = "failed"
        task.finished_at = datetime.utcnow()
        task.next_retry_at = None
    else:
        task.status = "retry_wait"
        task.next_retry_at = compute_next_retry_at(
            retry_count=task.retry_count,
            base_delay_seconds=base_delay_seconds,
            max_delay_seconds=max_delay_seconds,
            jitter_seconds=jitter_seconds,
        )
