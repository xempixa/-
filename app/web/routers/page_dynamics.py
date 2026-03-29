from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.deps import get_db_session, get_query_service, get_templates
from app.web.services.query_service import QueryService

router = APIRouter()


@router.get("/dynamics", response_class=HTMLResponse)
async def dynamics_page(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    uid: int | None = Query(None),
    keyword: str | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    service: QueryService = Depends(get_query_service),
) -> HTMLResponse:
    templates = get_templates(request)
    items, total = await service.list_dynamics(session=session, page=page, page_size=page_size, uid=uid, keyword=keyword)
    meta = service.make_meta(page, page_size, total)
    return templates.TemplateResponse(
        request=request,
        name="dynamics.html",
        context={
            "request": request,
            "page_title": "动态",
            "items": items,
            "meta": meta,
            "filters": {"uid": uid, "keyword": keyword},
        },
    )
