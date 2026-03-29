from __future__ import annotations

from typing import Any

import orjson
from loguru import logger

from app.clients.http import build_async_client
from app.clients.wbi import extract_key_from_url, sign_wbi_params
from app.config import settings
from app.utils.retry import http_retry
from app.utils.time import sleep_jitter


class BiliApiClient:
    def __init__(self) -> None:
        self._client = build_async_client()
        self._img_key: str | None = None
        self._sub_key: str | None = None

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

    async def _refresh_wbi_keys(self) -> tuple[str, str]:
        url = f"{settings.bili_api_base}/x/web-interface/nav"
        logger.info("刷新 WBI keys")
        data = await self.get_json(url)

        wbi_img = (data.get("data") or {}).get("wbi_img") or {}
        img_url = wbi_img.get("img_url")
        sub_url = wbi_img.get("sub_url")
        if not img_url or not sub_url:
            raise RuntimeError("nav 接口未返回 wbi_img.img_url / sub_url")

        self._img_key = extract_key_from_url(img_url)
        self._sub_key = extract_key_from_url(sub_url)
        return self._img_key, self._sub_key

    async def _get_wbi_keys(self) -> tuple[str, str]:
        if self._img_key and self._sub_key:
            return self._img_key, self._sub_key
        return await self._refresh_wbi_keys()

    async def get_json_wbi(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        img_key, sub_key = await self._get_wbi_keys()
        signed_params = sign_wbi_params(params=params, img_key=img_key, sub_key=sub_key)
        data = await self.get_json(url, signed_params)

        if isinstance(data, dict):
            payload = data.get("data") or {}
            voucher = payload.get("v_voucher")
            if voucher:
                logger.warning("WBI 签名疑似失效，尝试刷新 keys 后重试一次")
                img_key, sub_key = await self._refresh_wbi_keys()
                signed_params = sign_wbi_params(params=params, img_key=img_key, sub_key=sub_key)
                data = await self.get_json(url, signed_params)

        return data

    async def get_dynamic_list(self, host_uid: int, offset: str | None = None) -> dict[str, Any]:
        url = f"{settings.bili_api_base}/x/polymer/web-dynamic/v1/feed/space"
        params: dict[str, Any] = {
            "host_mid": host_uid,
            "timezone_offset": -480,
            "platform": "web",
            "features": (
                "itemOpusStyle,listOnlyfans,opusBigCover,onlyfansVote,"
                "forwardListHidden,decorationCard,commentsNewVersion,"
                "onlyfansAssetsV2,ugcDelete,onlyfansQaCard,avatarAutoTheme,"
                "sunflowerStyle,cardsEnhance,eva3CardOpus,eva3CardVideo,"
                "eva3CardComment,eva3CardUser"
            ),
            "web_location": "333.1387",
        }
        if offset is not None:
            params["offset"] = offset

        logger.info(f"请求动态列表 host_uid={host_uid}, offset={offset}")
        return await self.get_json_wbi(url, params)

    async def get_comment_main(
        self,
        comment_oid: str,
        comment_type: int,
        offset: str = "",
    ) -> dict[str, Any]:
        url = f"{settings.bili_api_base}/x/v2/reply/wbi/main"
        params: dict[str, Any] = {
            "oid": comment_oid,
            "type": comment_type,
            "mode": 3,
            "pagination_str": orjson.dumps({"offset": offset}).decode(),
            "plat": 1,
            "seek_rpid": "",
            "web_location": "1315875",
        }
        logger.info(
            f"请求一级评论 comment_oid={comment_oid}, comment_type={comment_type}, offset={offset}"
        )
        return await self.get_json_wbi(url, params)

    async def get_comment_replies(
        self,
        comment_oid: str,
        comment_type: int,
        root: str,
        pn: int = 1,
        ps: int = 10,
    ) -> dict[str, Any]:
        url = f"{settings.bili_api_base}/x/v2/reply/reply"
        params: dict[str, Any] = {
            "oid": comment_oid,
            "type": comment_type,
            "root": root,
            "ps": ps,
            "pn": pn,
            "web_location": "333.1387",
        }
        logger.info(
            f"请求二级评论 comment_oid={comment_oid}, comment_type={comment_type}, root={root}, pn={pn}, ps={ps}"
        )
        return await self.get_json(url, params)

    async def get_creator_videos(
        self,
        host_uid: int,
        page: int = 1,
        page_size: int = 42,
        charging_only: bool = False,
    ) -> dict[str, Any]:
        url = f"{settings.bili_api_base}/x/space/wbi/arc/search"
        params: dict[str, Any] = {
            "mid": host_uid,
            "pn": page,
            "ps": page_size,
            "tid": 0,
            "special_type": "charging" if charging_only else "",
            "order": "pubdate",
            "index": 0,
            "keyword": "",
            "order_avoided": "true",
            "platform": "web",
            "web_location": "333.1387",
        }
        logger.info(
            f"请求创作者视频列表 host_uid={host_uid}, page={page}, charging_only={charging_only}"
        )
        return await self.get_json_wbi(url, params)

    @staticmethod
    def dumps(data: dict[str, Any]) -> str:
        return orjson.dumps(data).decode("utf-8")
