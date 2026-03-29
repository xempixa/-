import asyncio

import typer
from rich import print

from app.auth.export_cookies import export_netscape_cookies
from app.auth.login import interactive_login
from app.auth.state import storage_state_exists
from app.db.init_db import init_db
from app.logging import setup_logging
from app.services.download_videos import download_video_by_bvid
from app.services.enqueue_video_download import enqueue_video_download
from app.services.run_download_queue import run_download_queue
from app.services.sync_comment_replies import sync_comment_replies
from app.services.sync_comments import sync_comments
from app.services.sync_creator_feed import sync_creator_feed
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
    fetch_replies: bool = typer.Option(True, help="是否自动抓取二级回复"),
) -> None:
    asyncio.run(sync_comments(dynamic_id=dynamic_id, max_pages=max_pages, fetch_replies=fetch_replies))
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


@app.command("sync-creator-feed")
def cli_sync_creator_feed(
    host_uid: int = typer.Option(..., help="目标 UP 主 UID"),
    limit_pages: int = typer.Option(3, help="拉取页数"),
) -> None:
    asyncio.run(sync_creator_feed(host_uid=host_uid, limit_pages=limit_pages))
    print("[green]创作者动态增量同步完成[/green]")


@app.command("sync-comment-replies")
def cli_sync_comment_replies(
    dynamic_id: str = typer.Option(..., help="动态 ID"),
    root_comment_id: str = typer.Option(..., help="一级评论 ID"),
    max_pages: int = typer.Option(10, help="最大页数"),
) -> None:
    asyncio.run(
        sync_comment_replies(
            dynamic_id=dynamic_id,
            root_comment_id=root_comment_id,
            max_pages=max_pages,
        )
    )
    print("[green]二级评论同步完成[/green]")


@app.command("enqueue-download")
def cli_enqueue_download(
    bvid: str = typer.Option(..., help="视频 BVID"),
    priority: int = typer.Option(100, help="优先级，越小越高"),
) -> None:
    ok = asyncio.run(enqueue_video_download(bvid=bvid, priority=priority))
    if ok:
        print("[green]下载任务已入队[/green]")
    else:
        print("[yellow]任务已存在，跳过入队[/yellow]")


@app.command("run-download-queue")
def cli_run_download_queue(
    batch_size: int = typer.Option(3, help="每次处理任务数"),
) -> None:
    asyncio.run(run_download_queue(batch_size=batch_size))
    print("[green]下载队列执行完成[/green]")


@app.command("export-cookies")
def cli_export_cookies() -> None:
    path = export_netscape_cookies()
    print(f"[green]cookies 已导出: {path}[/green]")


if __name__ == "__main__":
    app()
