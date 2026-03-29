from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.deps import get_db_session, get_query_service, get_templates
from app.web.services.query_service import QueryService

router = APIRouter()


@router.get("/downloads", response_class=HTMLResponse)
async def downloads_page(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    bvid: str | None = Query(None),
    uid: int | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    service: QueryService = Depends(get_query_service),
) -> HTMLResponse:
    templates = get_templates(request)
    items, total = await service.list_download_tasks(
        session=session,
        page=page,
        page_size=page_size,
        status=status,
        bvid=bvid,
        uid=uid,
    )
    meta = service.make_meta(page, page_size, total)
    return templates.TemplateResponse(
        request=request,
        name="downloads.html",
        context={
            "request": request,
            "page_title": "下载任务",
            "items": items,
            "meta": meta,
            "filters": {"status": status, "bvid": bvid, "uid": uid},
        },
    )
