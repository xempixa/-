from __future__ import annotations

from fastapi import APIRouter

from app.web.schemas.api_common import ApiResponse

router = APIRouter()


@router.get("/health", response_model=ApiResponse)
async def health_api() -> ApiResponse:
    return ApiResponse(success=True, message="ok", data={"status": "healthy"})
