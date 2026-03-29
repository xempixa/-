from __future__ import annotations

import asyncio
from pathlib import Path

from loguru import logger

from app.config import settings
from app.constants import DEFAULT_DOWNLOAD_TEMPLATE


async def download_video(url: str, output_dir: Path | None = None) -> int:
    out_dir = output_dir or settings.download_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        settings.yt_dlp_bin,
        "--cookies-from-browser",
        "chrome",
        # TODO: 后续可替换为 --cookies <cookie_file> 以接入 Playwright 导出的 cookie。
        "-o",
        str(out_dir / DEFAULT_DOWNLOAD_TEMPLATE),
        url,
    ]
    logger.info(f"执行下载命令: {' '.join(cmd)}")

    process = await asyncio.create_subprocess_exec(*cmd)
    return_code = await process.wait()
    if return_code != 0:
        logger.error(f"yt-dlp 下载失败，退出码={return_code}")
    return return_code
