from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.db.models import DownloadTask, Dynamic, DynamicComment, Video
from app.db.session import AsyncSessionLocal
from app.utils.csv_export import export_csv
from app.utils.json_export import export_json


async def export_all_reports(report_dir: str = "./reports") -> dict[str, str]:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    async with AsyncSessionLocal() as session:
        dynamics = list((await session.scalars(select(Dynamic))).all())
        comments = list((await session.scalars(select(DynamicComment))).all())
        videos = list((await session.scalars(select(Video))).all())
        tasks = list((await session.scalars(select(DownloadTask))).all())

    dynamic_rows = [
        {
            "dynamic_id": x.dynamic_id,
            "uid": x.uid,
            "dynamic_type": x.dynamic_type,
            "content_text": x.content_text,
            "last_seen_at": x.last_seen_at.isoformat() if x.last_seen_at else None,
        }
        for x in dynamics
    ]

    comment_rows = [
        {
            "comment_id": x.comment_id,
            "dynamic_id": x.dynamic_id,
            "root_comment_id": x.root_comment_id,
            "parent_id": x.parent_id,
            "user_name": x.user_name,
            "content": x.content,
            "like_count": x.like_count,
            "publish_ts": x.publish_ts.isoformat() if x.publish_ts else None,
        }
        for x in comments
    ]

    video_rows = [
        {
            "bvid": x.bvid,
            "aid": x.aid,
            "cid": x.cid,
            "uid": x.uid,
            "title": x.title,
            "duration_seconds": x.duration_seconds,
            "is_charge_only": x.is_charge_only,
            "publish_ts": x.publish_ts.isoformat() if x.publish_ts else None,
        }
        for x in videos
    ]

    task_rows = [
        {
            "bvid": x.bvid,
            "status": x.status,
            "retry_count": x.retry_count,
            "file_path": x.file_path,
            "error_message": x.error_message,
            "next_retry_at": x.next_retry_at.isoformat() if x.next_retry_at else None,
            "source_uid": x.source_uid,
            "created_at": x.created_at.isoformat() if x.created_at else None,
            "finished_at": x.finished_at.isoformat() if x.finished_at else None,
        }
        for x in tasks
    ]

    outputs = {
        "dynamics_csv": str(export_csv(dynamic_rows, f"{report_dir}/dynamics_{ts}.csv")),
        "comments_csv": str(export_csv(comment_rows, f"{report_dir}/comments_{ts}.csv")),
        "videos_csv": str(export_csv(video_rows, f"{report_dir}/videos_{ts}.csv")),
        "tasks_csv": str(export_csv(task_rows, f"{report_dir}/download_tasks_{ts}.csv")),
        "videos_json": str(export_json(video_rows, f"{report_dir}/videos_{ts}.json")),
    }

    return outputs
