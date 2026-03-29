from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Creator, DownloadTask, Dynamic, DynamicComment, RunLog, Video


class DashboardService:
    async def get_summary(self, session: AsyncSession) -> dict:
        creators = await session.scalar(select(func.count()).select_from(Creator)) or 0
        dynamics = await session.scalar(select(func.count()).select_from(Dynamic)) or 0
        comments = await session.scalar(select(func.count()).select_from(DynamicComment)) or 0
        videos = await session.scalar(select(func.count()).select_from(Video)) or 0

        pending = await session.scalar(
            select(func.count()).select_from(DownloadTask).where(DownloadTask.status == "pending")
        ) or 0
        running = await session.scalar(
            select(func.count()).select_from(DownloadTask).where(DownloadTask.status == "running")
        ) or 0
        failed = await session.scalar(
            select(func.count()).select_from(DownloadTask).where(DownloadTask.status == "failed")
        ) or 0
        success = await session.scalar(
            select(func.count()).select_from(DownloadTask).where(DownloadTask.status == "success")
        ) or 0

        latest_run = await session.scalar(select(RunLog).order_by(RunLog.started_at.desc()).limit(1))

        return {
            "creators": creators,
            "dynamics": dynamics,
            "comments": comments,
            "videos": videos,
            "download_pending": pending,
            "download_running": running,
            "download_failed": failed,
            "download_success": success,
            "latest_run": {
                "run_type": latest_run.run_type,
                "status": latest_run.status,
                "started_at": latest_run.started_at.isoformat() if latest_run.started_at else None,
                "finished_at": latest_run.finished_at.isoformat() if latest_run.finished_at else None,
            }
            if latest_run
            else None,
        }
