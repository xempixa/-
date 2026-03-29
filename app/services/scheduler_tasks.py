from __future__ import annotations

from loguru import logger


async def run_scheduler_tasks() -> None:
    """预留给调度系统调用的任务入口。"""
    logger.info("scheduler_tasks 任务入口预留，待后续编排具体任务")
