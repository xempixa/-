from pathlib import Path

from loguru import logger
from playwright.async_api import async_playwright

from app.config import settings


async def interactive_login(storage_state_path: Path | None = None) -> Path:
    """手动扫码登录一次，保存登录态到 storage_state.json。"""
    target = storage_state_path or settings.storage_state_path

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(user_agent=settings.user_agent)
            page = await context.new_page()

            logger.info("打开 B 站首页，请手动扫码登录。")
            await page.goto(settings.bili_base_url, wait_until="domcontentloaded")

            input("完成登录后，按回车继续保存登录态...")

            await context.storage_state(path=str(target), indexed_db=True)
            await browser.close()

        logger.info(f"登录态已保存: {target}")
        return target
    except Exception as exc:
        logger.exception(f"登录过程失败: {exc}")
        raise
