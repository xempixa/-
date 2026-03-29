from __future__ import annotations

from typing import Any

from loguru import logger
from sqlalchemy import select

from app.clients.bili_api import BiliApiClient
from app.db.models import Dynamic
from app.db.session import AsyncSessionLocal


def _extract_dynamic_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(payload.get("items"), list):
        return payload["items"]

    data = payload.get("data")
    if isinstance(data, dict) and isinstance(data.get("items"), list):
        return data["items"]

    return []


def _extract_next_offset(payload: dict[str, Any]) -> str | None:
    offset = payload.get("next_offset")
    if offset is not None:
        return str(offset)

    data = payload.get("data")
    if isinstance(data, dict) and data.get("offset") is not None:
        return str(data.get("offset"))

    return None


async def sync_dynamics(host_uid: int, limit_pages: int = 1) -> None:
    client = BiliApiClient()
    offset: str | None = None

    try:
        async with AsyncSessionLocal() as session:
            for page_no in range(1, limit_pages + 1):
                data = await client.get_dynamic_list(host_uid=host_uid, offset=offset)

                items = _extract_dynamic_items(data)
                logger.info(f"第 {page_no} 页动态数量: {len(items)}")

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
                offset = _extract_next_offset(data)
                if not offset:
                    break
    except Exception as exc:
        logger.exception(f"同步动态失败: {exc}")
        raise
    finally:
        await client.aclose()
