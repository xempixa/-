from __future__ import annotations

from loguru import logger

from app.auth.export_cookies import export_netscape_cookies
from app.clients.ytdlp_client import download_video
from app.db.crud_download import (
    get_pending_tasks,
    mark_task_retry,
    mark_task_running,
    mark_task_success,
)
from app.db.session import AsyncSessionLocal


async def run_download_worker(batch_size: int = 3) -> None:
    cookies_file = export_netscape_cookies()

    async with AsyncSessionLocal() as session:
        tasks = await get_pending_tasks(session, limit=batch_size)
        if not tasks:
            logger.info("没有待处理下载任务")
            return

        for task in tasks:
            await mark_task_running(session, task)
            await session.commit()

            try:
                logger.info(f"开始下载 bvid={task.bvid}")
                code, file_path = await download_video(task.url, cookies_file=cookies_file)

                if code == 0:
                    await mark_task_success(session, task, file_path=file_path)
                    logger.info(f"下载成功 bvid={task.bvid}")
                else:
                    await mark_task_retry(session, task, error_message=f"yt-dlp exit code={code}")
                    logger.warning(f"下载失败 bvid={task.bvid}, exit code={code}")

            except Exception as exc:
                await mark_task_retry(session, task, error_message=str(exc))
                logger.exception(f"下载异常 bvid={task.bvid}: {exc}")

            await session.commit()
