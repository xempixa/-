from __future__ import annotations

from typing import Any

from loguru import logger
from sqlalchemy import select

from app.clients.bili_api import BiliApiClient
from app.db.models import Dynamic
from app.db.session import AsyncSessionLocal


def _extract_page_data(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], str | None, bool]:
    data = payload.get("data")
    if not isinstance(data, dict):
        return [], None, False

    items = data.get("items")
    page_items = items if isinstance(items, list) else []

    next_offset = data.get("offset")
    page_offset = str(next_offset) if next_offset is not None else None

    has_more = bool(data.get("has_more"))
    return page_items, page_offset, has_more


async def sync_dynamics(host_uid: int, limit_pages: int = 1) -> None:
    client = BiliApiClient()
    offset: str | None = ""

    try:
        async with AsyncSessionLocal() as session:
            for page_no in range(1, limit_pages + 1):
                data = await client.get_dynamic_list(host_uid=host_uid, offset=offset)
                items, next_offset, has_more = _extract_page_data(data)
                logger.info(
                    f"第 {page_no} 页动态数量: {len(items)}, has_more={has_more}, next_offset={next_offset}"
                )

                for item in items:
                    dynamic_id = str(item.get("id_str") or "")
                    if not dynamic_id:
                        logger.warning("跳过动态：缺少 item.id_str")
                        continue

                    basic = item.get("basic") or {}
                    comment_oid = str(basic.get("comment_id_str") or "") or None
                    raw_comment_type = basic.get("comment_type")

                    comment_type: int | None = None
                    if raw_comment_type is not None:
                        try:
                            comment_type = int(raw_comment_type)
                        except (TypeError, ValueError):
                            logger.warning(
                                f"dynamic_id={dynamic_id} comment_type 非法: {raw_comment_type}, 将置空继续"
                            )

                    if not comment_oid:
                        logger.warning(f"dynamic_id={dynamic_id} 缺少 basic.comment_id_str，评论同步链路将跳过")
                    if comment_type is None:
                        logger.warning(f"dynamic_id={dynamic_id} 缺少/非法 basic.comment_type，评论同步链路将跳过")

                    existing = await session.scalar(select(Dynamic).where(Dynamic.dynamic_id == dynamic_id))

                    modules = item.get("modules") or {}
                    module_dynamic = modules.get("module_dynamic") or {}
                    major = module_dynamic.get("major") or {}
                    desc = module_dynamic.get("desc") or {}
                    content_text = (
                        desc.get("text")
                        or module_dynamic.get("text")
                        or major.get("desc")
                        or item.get("text")
                        or item.get("content")
                        or ""
                    )

                    if existing:
                        existing.uid = item.get("uid")
                        existing.dynamic_type = str(item.get("type") or item.get("type_name") or "") or None
                        existing.content_text = content_text
                        existing.comment_oid = comment_oid
                        existing.comment_type = comment_type
                        existing.raw_json = client.dumps(item)
                    else:
                        session.add(
                            Dynamic(
                                dynamic_id=dynamic_id,
                                uid=item.get("uid"),
                                dynamic_type=str(item.get("type") or item.get("type_name") or "") or None,
                                content_text=content_text,
                                comment_oid=comment_oid,
                                comment_type=comment_type,
                                raw_json=client.dumps(item),
                            )
                        )

                await session.commit()
                if not has_more:
                    break
                if not next_offset:
                    logger.warning("has_more=true 但 data.offset 为空，提前结束以避免重复翻页")
                    break
                offset = next_offset
    except Exception as exc:
        logger.exception(f"同步动态失败: {exc}")
        raise
    finally:
        await client.aclose()
