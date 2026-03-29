# bili-charge-archiver

个人授权内容归档工具骨架：

- Playwright 登录
- HTTPX 异步请求
- SQLite 落库
- Typer CLI
- 预留 yt-dlp 视频下载

## 1. 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -e .
playwright install chromium
