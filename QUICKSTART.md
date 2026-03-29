# QUICKSTART

## 1. 环境要求

- Windows 11
- Python 3.11.x
- PowerShell 5+/7+
- 可访问 B 站与依赖下载源

## 2. 首次初始化

```powershell
powershell -File .\scripts\init_local.ps1
```

该脚本会执行：
- 创建 `.venv`
- 安装 Python 依赖
- 安装 Playwright Chromium
- 创建 `.env`（若不存在）
- 初始化 SQLite

## 3. 登录并导出登录态（人工）

```powershell
.\.venv\Scripts\bili-archiver.exe login
.\.venv\Scripts\bili-archiver.exe check-auth
```

## 4. 启动服务

```powershell
powershell -File .\scripts\run_stack.ps1
```

默认：
- Web: `http://127.0.0.1:8000`
- Worker: 30 秒轮询下载队列
- Scheduler: 5 分钟触发一次调度

## 5. 健康检查

```powershell
powershell -File .\scripts\healthcheck.ps1
```

## 6. 最小验收命令

```powershell
powershell -File .\scripts\acceptance_smoke.ps1
```

> 若缺少真实 cookie / 私有接口参数 / 浏览器环境，下载与部分同步需人工补环境验证。

## 7. 停止服务

```powershell
powershell -File .\scripts\stop_stack.ps1
```
