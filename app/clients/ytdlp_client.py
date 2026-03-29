from __future__ import annotations

import asyncio
from pathlib import Path

from loguru import logger

from app.config import settings
from app.constants import DEFAULT_DOWNLOAD_TEMPLATE


async def download_video(
    url: str,
    output_dir: Path | None = None,
    cookies_file: Path | None = None,
) -> tuple[int, str | None]:
    out_dir = output_dir or settings.download_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    output_tpl = str(out_dir / DEFAULT_DOWNLOAD_TEMPLATE)

    cmd = [
        settings.yt_dlp_bin,
        "-o",
        output_tpl,
        "--newline",
        "--no-progress",
        url,
    ]

    if cookies_file and cookies_file.exists():
        cmd.extend(["--cookies", str(cookies_file)])
    else:
        cmd.extend(["--cookies-from-browser", "chrome"])

    logger.info(f"执行下载命令: {' '.join(cmd)}")
    process = await asyncio.create_subprocess_exec(*cmd)
    code = await process.wait()

    if code != 0:
        logger.error(f"yt-dlp 下载失败，退出码={code}")

    # TODO: 第二轮可用 --print after_move:filepath 解析真实落盘路径。
    return code, None
