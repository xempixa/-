from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.deps import get_dashboard_service, get_db_session
from app.web.schemas.api_common import ApiResponse
from app.web.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/dashboard/summary", response_model=ApiResponse)
async def dashboard_summary_api(
    session: AsyncSession = Depends(get_db_session),
    service: DashboardService = Depends(get_dashboard_service),
) -> ApiResponse:
    data = await service.get_summary(session)
    return ApiResponse(data=data)
