from __future__ import annotations

from datetime import datetime

from loguru import logger

from app.clients.bili_api import BiliApiClient
from app.db.repo import CheckpointRepo, VideoRepo
from app.db.session import AsyncSessionLocal


async def sync_creator_videos(host_uid: int, limit_pages: int = 3) -> tuple[int, int]:
    scope = f"creator_videos:{host_uid}"
    client = BiliApiClient()
    upsert_count = 0
    page_count = 0

    try:
        async with AsyncSessionLocal() as session:
            checkpoint = await CheckpointRepo.get(session, scope)
            start_page = int(checkpoint.cursor) if checkpoint and checkpoint.cursor and checkpoint.cursor.isdigit() else 1
            newest_bvid: str | None = None

            for page in range(start_page, start_page + max(0, limit_pages)):
                # TODO: 若真实接口的分页字段不是 page/page_size，请按抓包结果调整。
                data = await client.get_creator_videos(host_uid=host_uid, page=page)
                payload = data.get("data", data)
                items = payload.get("items") or payload.get("list") or []
                logger.info(f"host_uid={host_uid} 第{page}页视频数={len(items)}")

                if not items:
                    break

                page_count += 1

                for idx, item in enumerate(items):
                    bvid = str(item.get("bvid") or "")
                    if not bvid:
                        continue

                    if newest_bvid is None and idx == 0:
                        newest_bvid = bvid

                    await VideoRepo.upsert(
                        session,
                        {
                            "bvid": bvid,
                            "aid": item.get("aid"),
                            "cid": item.get("cid"),
                            "uid": host_uid,
                            "title": item.get("title"),
                            "description": item.get("description") or item.get("desc"),
                            "duration_seconds": item.get("duration"),
                            "publish_ts": datetime.utcfromtimestamp(item["publish_ts"])
                            if item.get("publish_ts")
                            else None,
                            "is_charge_only": bool(item.get("is_charge_only") or False),
                            "raw_json": client.dumps(item),
                        },
                    )
                    upsert_count += 1

                await session.commit()

            await CheckpointRepo.save(
                session,
                scope=scope,
                cursor=str(start_page + page_count) if page_count > 0 else str(start_page),
                last_item_id=newest_bvid,
            )
            await session.commit()

    finally:
        await client.aclose()

    return upsert_count, page_count
