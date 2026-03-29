import asyncio
import random


async def sleep_jitter(min_interval_ms: int, max_interval_ms: int) -> None:
    await asyncio.sleep(random.randint(min_interval_ms, max_interval_ms) / 1000)
