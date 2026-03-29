from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.deps import get_db_session, get_query_service, get_templates
from app.web.services.query_service import QueryService

router = APIRouter()


@router.get("/creators", response_class=HTMLResponse)
async def creators_page(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    service: QueryService = Depends(get_query_service),
) -> HTMLResponse:
    templates = get_templates(request)
    creators = await service.list_creators(session)
    return templates.TemplateResponse(
        request=request,
        name="creators.html",
        context={"request": request, "page_title": "创作者", "creators": creators},
    )
