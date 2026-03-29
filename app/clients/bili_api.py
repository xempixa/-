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
            if voucher and not payload.get("replies"):
                logger.warning("WBI 签名疑似失效，尝试刷新 keys 后重试一次")
                img_key, sub_key = await self._refresh_wbi_keys()
                signed_params = sign_wbi_params(params=params, img_key=img_key, sub_key=sub_key)
                data = await self.get_json(url, signed_params)

        return data

    async def get_dynamic_list(self, host_uid: int, offset: str | None = None) -> dict[str, Any]:
        url = f"{settings.bili_api_base}/x/polymer/web-dynamic/v1/feed/space"
        params = {
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
        if offset:
            params["offset"] = offset

        logger.info(f"请求动态列表 host_uid={host_uid}, offset={offset}")
        return await self.get_json_wbi(url, params)

    async def get_comment_main(
        self,
        oid: str,
        reply_type: int = 11,
        offset: str = "",
    ) -> dict[str, Any]:
        url = f"{settings.bili_api_base}/x/v2/reply/wbi/main"
        params = {
            "oid": oid,
            "type": reply_type,
            "mode": 3,
            "pagination_str": orjson.dumps({"offset": offset}).decode(),
            "plat": 1,
            "seek_rpid": "",
            "web_location": "1315875",
        }
        logger.info(f"请求一级评论 oid={oid}, type={reply_type}, offset={offset}")
        return await self.get_json_wbi(url, params)

    async def get_comment_replies(
        self,
        oid: str,
        root: str,
        reply_type: int = 11,
        pn: int = 1,
        ps: int = 10,
    ) -> dict[str, Any]:
        url = f"{settings.bili_api_base}/x/v2/reply/reply"
        params = {
            "oid": oid,
            "type": reply_type,
            "root": root,
            "ps": ps,
            "pn": pn,
            "web_location": "333.1387",
        }
        logger.info(f"请求二级评论 oid={oid}, root={root}, pn={pn}, ps={ps}")
        return await self.get_json(url, params)

    async def get_dynamic_comments(
        self,
        dynamic_id: str,
        page: int = 1,
        page_size: int = 20,
        root: str | None = None,
    ) -> dict[str, Any]:
        """
        TODO: 动态 dynamic_id 到评论 oid/type 的映射关系需结合真实抓包确认。
        当前先沿用 dynamic_id 直传为 oid，避免伪造映射规则。
        """
        if root:
            return await self.get_comment_replies(
                oid=dynamic_id,
                root=root,
                reply_type=11,
                pn=page,
                ps=page_size,
            )

        if page > 1:
            logger.warning("一级评论接口使用 offset 游标分页，page>1 需要调用方传入真实 offset")

        return await self.get_comment_main(
            oid=dynamic_id,
            reply_type=11,
            offset="",
        )

    async def get_creator_videos(
        self,
        host_uid: int,
        page: int = 1,
        page_size: int = 42,
        charging_only: bool = False,
    ) -> dict[str, Any]:
        url = f"{settings.bili_api_base}/x/space/wbi/arc/search"
        params = {
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

    async def get_video_detail(self, bvid: str) -> dict[str, Any]:
        url = f"{settings.bili_api_base}/x/web-interface/view"
        params = {"bvid": bvid}
        logger.info(f"请求视频详情 bvid={bvid}")
        return await self.get_json(url, params)

    @staticmethod
    def dumps(data: dict[str, Any]) -> str:
        return orjson.dumps(data).decode("utf-8")
