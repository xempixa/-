from typing import Any

import httpx
from loguru import logger

from app.auth.state import load_storage_state
from app.config import settings


def _cookies_from_storage_state() -> dict[str, str]:
    try:
        state: dict[str, Any] = load_storage_state()
    except FileNotFoundError:
        logger.warning("未发现 storage_state.json，将以无 cookie 状态请求。")
        return {}

    cookies: dict[str, str] = {}
    for item in state.get("cookies", []):
        name = item.get("name")
        value = item.get("value")
        if name and value is not None:
            cookies[name] = value
    return cookies


def build_async_client() -> httpx.AsyncClient:
    cookies = _cookies_from_storage_state()
    limits = httpx.Limits(
        max_connections=settings.http_max_connections,
        max_keepalive_connections=settings.http_max_keepalive,
    )
    timeout = httpx.Timeout(settings.http_timeout)

    headers = {
        "User-Agent": settings.user_agent,
        "Referer": settings.bili_base_url,
    }

    return httpx.AsyncClient(
        headers=headers,
        cookies=cookies,
        timeout=timeout,
        limits=limits,
        http2=True,
        follow_redirects=True,
    )
