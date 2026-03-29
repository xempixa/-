from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.web.routers.api_dashboard import router as api_dashboard_router
from app.web.routers.api_downloads import router as api_downloads_router
from app.web.routers.api_health import router as api_health_router
from app.web.routers.api_reports import router as api_reports_router
from app.web.routers.api_sync import router as api_sync_router
from app.web.routers.page_creators import router as page_creators_router
from app.web.routers.page_dashboard import router as page_dashboard_router
from app.web.routers.page_downloads import router as page_downloads_router
from app.web.routers.page_dynamics import router as page_dynamics_router
from app.web.routers.page_videos import router as page_videos_router


def create_web_app() -> FastAPI:
    app = FastAPI(title="Bili Charge Archiver Panel", version="0.1.0")

    app.state.templates = Jinja2Templates(directory="app/web/templates")
    app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

    app.include_router(page_dashboard_router)
    app.include_router(page_creators_router)
    app.include_router(page_dynamics_router)
    app.include_router(page_videos_router)
    app.include_router(page_downloads_router)

    app.include_router(api_health_router, prefix="/api")
    app.include_router(api_dashboard_router, prefix="/api")
    app.include_router(api_downloads_router, prefix="/api")
    app.include_router(api_sync_router, prefix="/api")
    app.include_router(api_reports_router, prefix="/api")

    return app
