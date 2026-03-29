from __future__ import annotations

from typing import Any

import orjson
from loguru import logger

from app.clients.http import build_async_client
from app.config import settings
from app.utils.retry import http_retry
from app.utils.time import sleep_jitter


class BiliApiClient:
    def __init__(self) -> None:
        self._client = build_async_client()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _sleep_jitter(self) -> None:
        await sleep_jitter(settings.request_min_interval_ms, settings.request_max_interval_ms)

    @http_retry()
    async def get_json(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        await self._sleep_jitter()
        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_dynamic_list(self, host_uid: int, offset: str | None = None) -> dict[str, Any]:
        """
        TODO: 根据你自己的抓包结果替换 endpoint/query 参数/鉴权检查。
        """
        url = f"{settings.bili_api_base}/x/placeholder/dynamic/list"
        params = {
            "host_uid": host_uid,
            "offset": offset,
        }
        logger.info(f"请求动态列表 host_uid={host_uid}, offset={offset}")
        return await self.get_json(url, params=params)

    async def get_dynamic_comments(
        self,
        dynamic_id: str,
        page: int = 1,
        page_size: int = 20,
        root: str | None = None,
    ) -> dict[str, Any]:
        """
        TODO: 根据你自己的抓包结果替换 endpoint/query 参数/鉴权检查。
        """
        url = f"{settings.bili_api_base}/x/placeholder/comment/list"
        params = {
            "dynamic_id": dynamic_id,
            "page": page,
            "page_size": page_size,
            "root": root,
        }
        logger.info(f"请求评论 dynamic_id={dynamic_id}, page={page}, root={root}")
        return await self.get_json(url, params=params)



    async def get_creator_videos(self, host_uid: int, page: int = 1, page_size: int = 30) -> dict[str, Any]:
        """
        TODO: 根据你自己的抓包结果替换 endpoint/query 参数/鉴权检查。
        """
        url = f"{settings.bili_api_base}/x/placeholder/video/list"
        params = {"host_uid": host_uid, "page": page, "page_size": page_size}
        logger.info(f"请求创作者视频列表 host_uid={host_uid}, page={page}")
        return await self.get_json(url, params=params)

    async def get_video_detail(self, bvid: str) -> dict[str, Any]:
        """
        TODO: 根据你自己的抓包结果替换 endpoint/query 参数/鉴权检查。
        """
        url = f"{settings.bili_api_base}/x/placeholder/video/detail"
        params = {"bvid": bvid}
        logger.info(f"请求视频详情 bvid={bvid}")
        return await self.get_json(url, params=params)

    @staticmethod
    def dumps(data: dict[str, Any]) -> str:
        return orjson.dumps(data).decode("utf-8")
