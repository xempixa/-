from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RunLog


async def create_run_log(
    session: AsyncSession,
    run_type: str,
    scope: str | None = None,
    status: str = "running",
) -> RunLog:
    obj = RunLog(
        run_type=run_type,
        scope=scope,
        status=status,
    )
    session.add(obj)
    await session.flush()
    return obj


async def finish_run_log(
    session: AsyncSession,
    run_log: RunLog,
    status: str,
    item_count: int = 0,
    success_count: int = 0,
    failed_count: int = 0,
    message: str | None = None,
) -> None:
    run_log.status = status
    run_log.finished_at = datetime.utcnow()
    run_log.item_count = item_count
    run_log.success_count = success_count
    run_log.failed_count = failed_count
    run_log.message = message
