from __future__ import annotations

from loguru import logger
from sqlalchemy import select

from app.clients.bili_api import BiliApiClient
from app.db.models import Video
from app.db.session import AsyncSessionLocal


async def sync_video(bvid: str) -> None:
    client = BiliApiClient()

    try:
        data = await client.get_video_detail(bvid)
        payload = data.get("data", data)

        async with AsyncSessionLocal() as session:
            existing = await session.scalar(select(Video).where(Video.bvid == bvid))

            title = payload.get("title")
            description = payload.get("desc") or payload.get("description")
            aid = payload.get("aid")
            cid = payload.get("cid")
            duration = payload.get("duration")
            uid = ((payload.get("owner") or {}).get("mid")) or payload.get("uid")
            is_charge_only = bool(payload.get("is_charge_only") or False)

            if existing:
                existing.title = title
                existing.description = description
                existing.aid = aid
                existing.cid = cid
                existing.uid = uid
                existing.duration_seconds = duration
                existing.is_charge_only = is_charge_only
                existing.raw_json = client.dumps(payload)
            else:
                session.add(
                    Video(
                        bvid=bvid,
                        aid=aid,
                        cid=cid,
                        uid=uid,
                        title=title,
                        description=description,
                        duration_seconds=duration,
                        is_charge_only=is_charge_only,
                        raw_json=client.dumps(payload),
                    )
                )

            await session.commit()
    except Exception as exc:
        logger.exception(f"同步视频失败: {exc}")
        raise
    finally:
        await client.aclose()
