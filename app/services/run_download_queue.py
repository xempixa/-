from app.workers.download_worker import run_download_worker


async def run_download_queue(batch_size: int = 3) -> None:
    await run_download_worker(batch_size=batch_size)
