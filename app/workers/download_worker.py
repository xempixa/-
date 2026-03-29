from __future__ import annotations

import socket

from loguru import logger

from app.auth.export_cookies import export_netscape_cookies
from app.clients.ytdlp_client import download_video
from app.db.crud_download import (
    get_runnable_tasks,
    mark_task_retry,
    mark_task_success,
    try_claim_task,
)
from app.db.crud_runlog import create_run_log, finish_run_log
from app.db.session import AsyncSessionLocal
from app.services.batch_sync import load_app_config


def get_worker_id() -> str:
    return f"{socket.gethostname()}-download-worker"


async def run_download_worker(batch_size: int = 3) -> None:
    worker_id = get_worker_id()
    app_cfg = load_app_config()
    cookies_file = export_netscape_cookies()

    async with AsyncSessionLocal() as session:
        run_log = await create_run_log(
            session,
            run_type="download_queue",
            scope=worker_id,
        )
        await session.commit()

        success_count = 0
        failed_count = 0
        tasks = await get_runnable_tasks(session, limit=batch_size)

        if not tasks:
            await finish_run_log(
                session,
                run_log,
                status="success",
                message="no runnable download tasks",
            )
            await session.commit()
            logger.info("没有可运行下载任务")
            return

        for task in tasks:
            try:
                claimed = await try_claim_task(session, task.id, worker_id=worker_id)
                await session.commit()
                if not claimed:
                    logger.info(f"[{worker_id}] 任务已被其他 worker 领取，跳过 task_id={task.id}")
                    continue

                await session.refresh(task)
                logger.info(f"[{worker_id}] 开始下载 bvid={task.bvid}")
                code, file_path = await download_video(task.url, cookies_file=cookies_file)

                if code == 0:
                    await mark_task_success(session, task, file_path=file_path)
                    success_count += 1
                else:
                    await mark_task_retry(
                        session,
                        task,
                        error_message=f"yt-dlp exit code={code}",
                        base_delay_seconds=app_cfg.retry.base_delay_seconds,
                        max_delay_seconds=app_cfg.retry.max_delay_seconds,
                        jitter_seconds=app_cfg.retry.jitter_seconds,
                    )
                    failed_count += 1

                await session.commit()

            except Exception as exc:
                await mark_task_retry(
                    session,
                    task,
                    error_message=str(exc),
                    base_delay_seconds=app_cfg.retry.base_delay_seconds,
                    max_delay_seconds=app_cfg.retry.max_delay_seconds,
                    jitter_seconds=app_cfg.retry.jitter_seconds,
                )
                failed_count += 1
                await session.commit()
                logger.exception(f"下载异常 bvid={task.bvid}: {exc}")

        await finish_run_log(
            session,
            run_log,
            status="success" if failed_count == 0 else "partial_success",
            item_count=len(tasks),
            success_count=success_count,
            failed_count=failed_count,
        )
        await session.commit()
