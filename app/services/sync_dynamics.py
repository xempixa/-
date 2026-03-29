from __future__ import annotations

from loguru import logger
from sqlalchemy import select

from app.clients.bili_api import BiliApiClient
from app.db.models import Dynamic
from app.db.session import AsyncSessionLocal


async def sync_dynamics(host_uid: int, limit_pages: int = 1) -> None:
    client = BiliApiClient()
    offset = None

    try:
        async with AsyncSessionLocal() as session:
            for page_no in range(1, limit_pages + 1):
                data = await client.get_dynamic_list(host_uid=host_uid, offset=offset)

                items = data.get("items", [])
                logger.info(f"第 {page_no} 页动态数量: {len(items)}")

                for item in items:
                    dynamic_id = str(item.get("id") or item.get("dynamic_id") or "")
                    if not dynamic_id:
                        continue

                    existing = await session.scalar(select(Dynamic).where(Dynamic.dynamic_id == dynamic_id))

                    content_text = item.get("text") or item.get("content") or ""

                    if existing:
                        existing.raw_json = client.dumps(item)
                        existing.content_text = content_text
                    else:
                        session.add(
                            Dynamic(
                                dynamic_id=dynamic_id,
                                uid=item.get("uid"),
                                dynamic_type=str(item.get("type") or ""),
                                content_text=content_text,
                                raw_json=client.dumps(item),
                            )
                        )

                await session.commit()
                offset = data.get("next_offset")
                if not offset:
                    break
    except Exception as exc:
        logger.exception(f"同步动态失败: {exc}")
        raise
    finally:
        await client.aclose()
