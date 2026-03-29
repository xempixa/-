from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.deps import get_db_session, get_download_admin_service, get_query_service
from app.web.schemas.api_common import ApiResponse, PaginatedResponse, PaginationMeta
from app.web.schemas.api_download import CancelDownloadRequest, EnqueueDownloadRequest, RetryDownloadRequest
from app.web.services.download_admin_service import DownloadAdminService
from app.web.services.query_service import QueryService

router = APIRouter()


@router.get("/downloads", response_model=PaginatedResponse)
async def list_downloads_api(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Literal["pending", "running", "retry_wait", "success", "failed", "cancelled", "skipped"] | None = Query(None),
    bvid: str | None = Query(None),
    uid: int | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    service: QueryService = Depends(get_query_service),
) -> PaginatedResponse:
    items, total = await service.list_download_tasks(
        session=session,
        page=page,
        page_size=page_size,
        status=status,
        bvid=bvid,
        uid=uid,
    )
    rows = [
        {
            "id": item.id,
            "bvid": item.bvid,
            "status": item.status,
            "priority": item.priority,
            "retry_count": item.retry_count,
            "file_path": item.file_path,
            "error_message": item.error_message,
            "source_uid": item.source_uid,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "next_retry_at": item.next_retry_at.isoformat() if item.next_retry_at else None,
        }
        for item in items
    ]
    meta = PaginationMeta(**service.make_meta(page, page_size, total))
    return PaginatedResponse(data=rows, meta=meta)


@router.post("/downloads/enqueue", response_model=ApiResponse)
async def enqueue_download_api(
    payload: EnqueueDownloadRequest,
    session: AsyncSession = Depends(get_db_session),
    service: DownloadAdminService = Depends(get_download_admin_service),
) -> ApiResponse:
    ok, msg = await service.enqueue(
        session=session,
        bvid=payload.bvid,
        priority=payload.priority,
        source_uid=payload.source_uid,
        note=payload.note,
    )
    return ApiResponse(success=ok, message=msg)


@router.post("/downloads/{task_id}/retry", response_model=ApiResponse)
async def retry_download_api(
    payload: RetryDownloadRequest,
    task_id: int = Path(..., ge=1),
    session: AsyncSession = Depends(get_db_session),
    service: DownloadAdminService = Depends(get_download_admin_service),
) -> ApiResponse:
    ok, msg = await service.retry_task(session=session, task_id=task_id, reset_retry_count=payload.reset_retry_count)
    return ApiResponse(success=ok, message=msg)


@router.post("/downloads/{task_id}/cancel", response_model=ApiResponse)
async def cancel_download_api(
    payload: CancelDownloadRequest,
    task_id: int = Path(..., ge=1),
    session: AsyncSession = Depends(get_db_session),
    service: DownloadAdminService = Depends(get_download_admin_service),
) -> ApiResponse:
    ok, msg = await service.cancel_task(session=session, task_id=task_id, reason=payload.reason)
    return ApiResponse(success=ok, message=msg)
