from __future__ import annotations

from loguru import logger

from app.clients.bili_api import BiliApiClient
from app.db.repo import CheckpointRepo, DynamicRepo
from app.db.session import AsyncSessionLocal


async def sync_creator_feed(host_uid: int, limit_pages: int = 3) -> None:
    scope = f"dynamic_feed:{host_uid}"
    client = BiliApiClient()

    try:
        async with AsyncSessionLocal() as session:
            checkpoint = await CheckpointRepo.get(session, scope)
            offset = checkpoint.cursor if checkpoint else None
            newest_dynamic_id: str | None = None

            for page_no in range(1, limit_pages + 1):
                # TODO: 如果抓包后确认实际参数名有差异，请按真实接口调整。
                data = await client.get_dynamic_list(host_uid=host_uid, offset=offset)
                items = data.get("items", [])

                logger.info(f"host_uid={host_uid} 第{page_no}页动态数={len(items)}")

                if not items:
                    break

                for idx, item in enumerate(items):
                    dynamic_id = str(item.get("id") or item.get("dynamic_id") or "")
                    if not dynamic_id:
                        continue

                    if page_no == 1 and idx == 0:
                        newest_dynamic_id = dynamic_id

                    payload = {
                        "dynamic_id": dynamic_id,
                        "uid": item.get("uid"),
                        "dynamic_type": str(item.get("type") or ""),
                        "content_text": item.get("text") or item.get("content") or "",
                        "raw_json": client.dumps(item),
                    }
                    await DynamicRepo.upsert(session, payload)

                offset = data.get("next_offset")
                await session.commit()

                if not offset:
                    break

            await CheckpointRepo.save(
                session,
                scope=scope,
                cursor=offset,
                last_item_id=newest_dynamic_id,
            )
            await session.commit()

    finally:
        await client.aclose()
