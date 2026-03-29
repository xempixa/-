from sqlalchemy import text

from app.db import models  # noqa: F401
from app.db.base import Base
from app.db.session import engine


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA journal_mode=WAL;"))
        await conn.run_sync(Base.metadata.create_all)
