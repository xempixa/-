from app.clients.ytdlp_client import download_video


async def download_video_by_bvid(bvid: str) -> int:
    url = f"https://www.bilibili.com/video/{bvid}"
    code, _ = await download_video(url)
    return code
