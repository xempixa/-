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
        "--print",
        "after_move:filepath",
        "--newline",
        "--no-progress",
        url,
    ]

    if cookies_file and cookies_file.exists():
        cmd.extend(["--cookies", str(cookies_file)])
    else:
        cmd.extend(["--cookies-from-browser", "chrome"])

    safe_cmd = [x if x not in {str(cookies_file)} else '<cookies-file>' for x in cmd]
    logger.info(f"执行下载命令: {' '.join(safe_cmd)}")
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()
    code = process.returncode

    if code != 0:
        logger.error(f"yt-dlp 下载失败，退出码={code} stderr={stderr.decode('utf-8', errors='ignore')}")

    file_path: str | None = None
    if stdout:
        lines = [line.strip() for line in stdout.decode("utf-8", errors="ignore").splitlines() if line.strip()]
        if lines:
            file_path = lines[-1]

    return code, file_path
