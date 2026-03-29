# bili-charge-archiver

面向 **Windows 11 + Python 3.11** 的 B 站内容归档工具，提供：

- CLI 管理（初始化、登录、同步、下载、报表、健康检查）
- Web 面板（任务看板、下载队列、健康接口）
- Worker 下载执行
- Scheduler 周期同步

> 当前仓库保留了 B 站接口占位实现。涉及私有接口参数处请按抓包结果补齐，代码中已保留 TODO，不会伪造参数。

## 运行模式

1. **CLI 模式**：`bili-archiver ...`
2. **Web 面板模式**：`bili-archiver serve-web`
3. **下载 Worker**：`bili-archiver run-download-queue`
4. **同步 Worker**：`bili-archiver batch-sync`
5. **调度器**：`bili-archiver run-scheduler-once`（可配合脚本循环执行）

## 快速命令

```powershell
# 初始化
powershell -ExecutionPolicy Bypass -File .\scripts\init_local.ps1

# 登录（人工）
.\.venv\Scripts\bili-archiver.exe login

# 启动整套服务（Web + Worker + Scheduler）
powershell -ExecutionPolicy Bypass -File .\scripts\run_stack.ps1

# 健康检查
powershell -ExecutionPolicy Bypass -File .\scripts\healthcheck.ps1

# 停止整套服务
powershell -ExecutionPolicy Bypass -File .\scripts\stop_stack.ps1
```

## 目录说明

- `app/web`：HTTP 路由、页面模板、API schema
- `app/services`：业务编排（同步、下载、调度、报表）
- `app/db`：模型、会话、CRUD
- `app/workers`：下载 worker 执行逻辑
- `scripts`：Windows 本地部署与运维脚本
- `config`：应用配置

## 文档

- [QUICKSTART.md](QUICKSTART.md)：最小启动与验证
- [DEPLOY_LOCAL.md](DEPLOY_LOCAL.md)：本地部署/联调/回滚流程

## 安全默认值

- Web 默认监听 `127.0.0.1`
- 下载队列任务增加领取锁，避免多 worker 重复消费
- BVID 输入在 CLI 与 API 层进行格式校验

