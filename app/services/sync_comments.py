from __future__ import annotations

from loguru import logger
from sqlalchemy import select

from app.clients.bili_api import BiliApiClient
from app.db.models import DynamicComment
from app.db.session import AsyncSessionLocal


async def sync_comments(dynamic_id: str, max_pages: int = 3) -> None:
    client = BiliApiClient()

    try:
        async with AsyncSessionLocal() as session:
            for page in range(1, max_pages + 1):
                data = await client.get_dynamic_comments(dynamic_id=dynamic_id, page=page)
                replies = data.get("replies", [])
                logger.info(f"dynamic_id={dynamic_id} 第 {page} 页一级评论数: {len(replies)}")

                for reply in replies:
                    comment_id = str(reply.get("rpid") or reply.get("comment_id") or "")
                    if not comment_id:
                        continue

                    existing = await session.scalar(
                        select(DynamicComment).where(DynamicComment.comment_id == comment_id)
                    )

                    payload = {
                        "comment_id": comment_id,
                        "dynamic_id": dynamic_id,
                        "root_comment_id": str(reply.get("root") or "") or None,
                        "parent_id": str(reply.get("parent") or "") or None,
                        "user_name": ((reply.get("member") or {}).get("uname")),
                        "content": ((reply.get("content") or {}).get("message")) or reply.get("message"),
                        "like_count": int(reply.get("like") or 0),
                        "raw_json": client.dumps(reply),
                    }

                    if existing:
                        existing.content = payload["content"]
                        existing.like_count = payload["like_count"]
                        existing.raw_json = payload["raw_json"]
                    else:
                        session.add(DynamicComment(**payload))

                await session.commit()

                if not replies:
                    break
    except Exception as exc:
        logger.exception(f"同步评论失败: {exc}")
        raise
    finally:
        await client.aclose()
