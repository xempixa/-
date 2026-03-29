from __future__ import annotations

from fastapi import APIRouter

from app.web.schemas.api_common import ApiResponse

router = APIRouter()


@router.get("/reports/export", response_model=ApiResponse)
async def export_reports_api() -> ApiResponse:
    return ApiResponse(success=True, message="use existing export-reports cli or wire service later")
