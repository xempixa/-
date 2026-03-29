from __future__ import annotations

from pathlib import Path

import yaml
from loguru import logger

from app.db.crud_runlog import create_run_log, finish_run_log
from app.db.session import AsyncSessionLocal
from app.schemas.app_config import AppConfigFile, CreatorsFile
from app.services.sync_creator_feed import sync_creator_feed
from app.services.sync_creator_videos import sync_creator_videos
from app.utils.filelock import SingleInstanceLock


def load_creators_config(path: str = "config/creators.yaml") -> CreatorsFile:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return CreatorsFile.model_validate(data)


def load_app_config(path: str = "config/app.yaml") -> AppConfigFile:
    cfg_path = Path(path)
    if not cfg_path.exists():
        return AppConfigFile()
    with open(cfg_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return AppConfigFile.model_validate(data)


async def run_batch_sync() -> None:
    creators_cfg = load_creators_config()
    app_cfg = load_app_config()

    lock = SingleInstanceLock("./data/locks/batch_sync.lock")
    if app_cfg.runtime.single_instance_lock and not lock.acquire():
        logger.warning("batch-sync 已在运行，跳过本次执行")
        return

    try:
        async with AsyncSessionLocal() as session:
            run_log = await create_run_log(session, run_type="batch_sync", scope="creators.yaml")
            await session.commit()

            success_count = 0
            failed_count = 0
            item_count = 0

            for creator in creators_cfg.creators:
                if not creator.enabled:
                    continue

                item_count += 1
                try:
                    logger.info(f"开始处理 creator uid={creator.uid}, name={creator.name}")

                    if creator.sync_dynamics:
                        await sync_creator_feed(
                            host_uid=creator.uid,
                            limit_pages=creator.dynamic_pages,
                        )

                    if creator.sync_videos:
                        await sync_creator_videos(
                            host_uid=creator.uid,
                            limit_pages=creator.video_pages,
                        )

                    success_count += 1
                except Exception as exc:
                    failed_count += 1
                    logger.exception(f"creator uid={creator.uid} 批量同步失败: {exc}")

            await finish_run_log(
                session,
                run_log,
                status="success" if failed_count == 0 else "partial_success",
                item_count=item_count,
                success_count=success_count,
                failed_count=failed_count,
            )
            await session.commit()
    finally:
        if app_cfg.runtime.single_instance_lock:
            lock.release()
