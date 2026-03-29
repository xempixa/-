import sys
from pathlib import Path

from loguru import logger

from app.config import settings


def setup_logging() -> None:
    log_dir = Path(settings.data_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | {message}",
    )

    logger.add(
        log_dir / "app.log",
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        encoding="utf-8",
    )

    logger.add(
        log_dir / "error.log",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        backtrace=True,
        diagnose=False,
    )
