import asyncio

import typer
from rich import print

from app.auth.login import interactive_login
from app.auth.state import storage_state_exists
from app.db.init_db import init_db
from app.logging import setup_logging
from app.services.download_videos import download_video_by_bvid
from app.services.sync_comments import sync_comments
from app.services.sync_dynamics import sync_dynamics
from app.services.sync_videos import sync_video
from app.utils.paths import ensure_dirs

app = typer.Typer(help="Bilibili personal charge content archiver")


@app.callback()
def main() -> None:
    setup_logging()
    ensure_dirs()


@app.command("init-db")
def cli_init_db() -> None:
    asyncio.run(init_db())
    print("[green]数据库初始化完成[/green]")


@app.command("login")
def cli_login() -> None:
    asyncio.run(interactive_login())
    print("[green]登录态保存完成[/green]")


@app.command("check-auth")
def cli_check_auth() -> None:
    ok = storage_state_exists()
    if ok:
        print("[green]storage_state 已存在[/green]")
    else:
        print("[red]storage_state 不存在，请先运行 login[/red]")


@app.command("sync-dynamics")
def cli_sync_dynamics(
    host_uid: int = typer.Option(..., help="目标 UP 主 UID"),
    limit_pages: int = typer.Option(1, help="拉取页数"),
) -> None:
    asyncio.run(sync_dynamics(host_uid=host_uid, limit_pages=limit_pages))
    print("[green]动态同步完成[/green]")


@app.command("sync-comments")
def cli_sync_comments(
    dynamic_id: str = typer.Option(..., help="动态 ID"),
    max_pages: int = typer.Option(3, help="评论最大页数"),
) -> None:
    asyncio.run(sync_comments(dynamic_id=dynamic_id, max_pages=max_pages))
    print("[green]评论同步完成[/green]")


@app.command("sync-video")
def cli_sync_video(
    bvid: str = typer.Option(..., help="视频 BVID"),
) -> None:
    asyncio.run(sync_video(bvid=bvid))
    print("[green]视频元数据同步完成[/green]")


@app.command("download-video")
def cli_download_video(
    bvid: str = typer.Option(..., help="视频 BVID"),
) -> None:
    code = asyncio.run(download_video_by_bvid(bvid))
    if code == 0:
        print("[green]视频下载完成[/green]")
    else:
        print(f"[red]视频下载失败，退出码: {code}[/red]")


if __name__ == "__main__":
    app()
