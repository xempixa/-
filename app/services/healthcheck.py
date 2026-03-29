from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from app.auth.export_cookies import export_netscape_cookies
from app.auth.state import storage_state_exists
from app.config import settings
from app.db.session import AsyncSessionLocal


async def run_healthcheck() -> dict[str, bool]:
    report_dir = Path("./reports")
    result: dict[str, bool] = {
        "storage_state_exists": storage_state_exists(),
        "db_exists": Path(settings.sqlite_path).exists(),
        "report_dir_writable": False,
        "cookies_export_ok": False,
        "db_connect_ok": False,
    }

    report_dir.mkdir(parents=True, exist_ok=True)
    try:
        probe = report_dir / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        result["report_dir_writable"] = True
    except Exception:
        result["report_dir_writable"] = False

    try:
        export_netscape_cookies()
        result["cookies_export_ok"] = True
    except Exception:
        result["cookies_export_ok"] = False

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        result["db_connect_ok"] = True
    except Exception:
        result["db_connect_ok"] = False

    return result
