from __future__ import annotations

from loguru import logger

from app.clients.bili_api import BiliApiClient
from app.db.repo import CommentRepo
from app.db.session import AsyncSessionLocal


async def sync_comment_replies(
    dynamic_id: str,
    root_comment_id: str,
    max_pages: int = 10,
) -> None:
    client = BiliApiClient()

    try:
        async with AsyncSessionLocal() as session:
            for page in range(1, max_pages + 1):
                data = await client.get_dynamic_comments(
                    dynamic_id=dynamic_id,
                    page=page,
                    page_size=20,
                    root=root_comment_id,
                )

                replies = data.get("replies", [])
                logger.info(
                    f"dynamic_id={dynamic_id} root={root_comment_id} 第{page}页二级回复数={len(replies)}"
                )

                if not replies:
                    break

                for reply in replies:
                    comment_id = str(reply.get("rpid") or reply.get("comment_id") or "")
                    if not comment_id:
                        continue

                    payload = {
                        "comment_id": comment_id,
                        "dynamic_id": dynamic_id,
                        "root_comment_id": str(reply.get("root") or root_comment_id),
                        "parent_id": str(reply.get("parent") or "") or None,
                        "user_name": ((reply.get("member") or {}).get("uname")),
                        "content": ((reply.get("content") or {}).get("message"))
                        or reply.get("message"),
                        "like_count": int(reply.get("like") or 0),
                        "raw_json": client.dumps(reply),
                    }
                    await CommentRepo.upsert(session, payload)

                await session.commit()

    finally:
        await client.aclose()
