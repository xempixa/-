# bili-charge-archiver

个人授权内容归档工具骨架，面向 **Windows 11 + Python 3.11+**。

- Playwright 登录并保存 storage_state（含 IndexedDB）
- HTTPX AsyncClient 访问接口
- SQLAlchemy + SQLite（WAL）持久化
- Typer CLI 管理流程
- yt-dlp 下载视频（预留 cookie 接入位）

## 1. 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -e .
playwright install chromium
```

## 2. 配置

复制并编辑环境变量：

```bash
copy .env.example .env
```

关键项：
- `USER_AGENT`：建议保持浏览器 UA
- `STORAGE_STATE_PATH`：Playwright 登录态输出
- `SQLITE_PATH`：SQLite 数据库路径

## 3. CLI 使用

```bash
bili-archiver --help
bili-archiver init-db
bili-archiver check-auth
bili-archiver login
```

可选同步命令：

```bash
bili-archiver sync-dynamics --host-uid 123456 --limit-pages 1
bili-archiver sync-comments --dynamic-id 10001 --max-pages 3
bili-archiver sync-video --bvid BV1xx411c7mD
bili-archiver download-video --bvid BV1xx411c7mD
```

## 4. 重要说明（需要你后续补充）

`app/clients/bili_api.py` 当前是 **可替换适配器**，故意保留 placeholder endpoint：
- `/x/placeholder/dynamic/list`
- `/x/placeholder/comment/list`
- `/x/placeholder/video/detail`

请基于你自己的账号权限和抓包结果，在 `TODO` 注释处补齐 endpoint 和参数，避免写入伪造私有参数。

## 5. 项目结构

```text
app/
  auth/        # Playwright 登录与登录态读取
  clients/     # HTTP/B站 API/yt-dlp 客户端
  db/          # SQLAlchemy 模型与会话
  schemas/     # Pydantic schema
  services/    # 业务编排（同步/下载）
  utils/       # 重试、路径、时间工具
```
