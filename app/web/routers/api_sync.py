from __future__ import annotations

from fastapi import APIRouter

from app.web.schemas.api_common import ApiResponse

router = APIRouter()


@router.post("/sync/batch", response_model=ApiResponse)
async def sync_batch_api() -> ApiResponse:
    return ApiResponse(success=True, message="accepted", data={"mode": "defer_to_worker"})


@router.post("/sync/creator/{uid}", response_model=ApiResponse)
async def sync_creator_api(uid: int) -> ApiResponse:
    return ApiResponse(success=True, message="accepted", data={"uid": uid, "mode": "defer_to_worker"})
