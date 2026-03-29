from __future__ import annotations

from loguru import logger

from app.services.batch_sync import run_batch_sync


async def run_scheduler_tasks() -> None:
    """调度入口：当前执行一次批量同步。"""
    logger.info("scheduler tick: run batch-sync")
    await run_batch_sync()
