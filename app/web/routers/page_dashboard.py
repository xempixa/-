from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.deps import get_dashboard_service, get_db_session, get_templates
from app.web.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    service: DashboardService = Depends(get_dashboard_service),
) -> HTMLResponse:
    templates = get_templates(request)
    summary = await service.get_summary(session)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request, "page_title": "仪表盘", "summary": summary},
    )
