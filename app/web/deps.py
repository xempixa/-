from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.web.services.dashboard_service import DashboardService
from app.web.services.download_admin_service import DownloadAdminService
from app.web.services.query_service import QueryService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


def get_dashboard_service() -> DashboardService:
    return DashboardService()


def get_download_admin_service() -> DownloadAdminService:
    return DownloadAdminService()


def get_query_service() -> QueryService:
    return QueryService()
