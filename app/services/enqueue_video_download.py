from __future__ import annotations

from sqlalchemy import select

from app.db.crud_download import create_download_task
from app.db.download_status import DOWNLOAD_STATUS_ACTIVE_DEDUP
from app.db.models import DownloadTask
from app.db.session import AsyncSessionLocal
from app.utils.bvid import is_valid_bvid, normalize_bvid


async def enqueue_video_download(bvid: str, priority: int = 100) -> bool:
    bvid = normalize_bvid(bvid)
    if not is_valid_bvid(bvid):
        return False

    url = f"https://www.bilibili.com/video/{bvid}"

    async with AsyncSessionLocal() as session:
        existing = await session.scalar(
            select(DownloadTask).where(
                DownloadTask.bvid == bvid,
                DownloadTask.status.in_(sorted(DOWNLOAD_STATUS_ACTIVE_DEDUP)),
            )
        )
        if existing:
            return False

        await create_download_task(session, bvid=bvid, url=url, priority=priority)
        await session.commit()
        return True
