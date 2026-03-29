# DEPLOY_LOCAL

## 部署目标

在 Windows 11 本地运行 Web + Scheduler + Worker，后续用于 OpenClaw 联调。

## 部署步骤

1. **克隆并进入仓库**
2. **执行初始化脚本**
   ```powershell
   powershell -File .\scripts\init_local.ps1
   ```
3. **补充 .env 配置**（如 UA、路径）
4. **登录并生成 storage_state**
   ```powershell
   .\.venv\Scripts\bili-archiver.exe login
   ```
5. **启动整套服务**
   ```powershell
   powershell -File .\scripts\run_stack.ps1
   ```
6. **执行健康检查**
   ```powershell
   powershell -File .\scripts\healthcheck.ps1
   ```

## OpenClaw 前置条件

- Python 3.11 可用
- PowerShell 可执行本仓库 `scripts/*.ps1`
- 本地可写目录：`data/`, `reports/`
- 已通过 `login` 获得有效登录态
- 对私有接口参数的 TODO 已按人工抓包补齐（若要真实同步）

## 回滚方案

### 代码回滚

```powershell
git checkout main
git branch -D deployment-prep
```

### 运行态回滚

```powershell
powershell -File .\scripts\stop_stack.ps1
```

### 数据回滚（本地）

- 停止进程后备份/替换 `data/app.db`
- 如需重建：
  ```powershell
  Remove-Item .\data\app.db -Force
  .\.venv\Scripts\bili-archiver.exe init-db
  ```

## 验收建议

- `scripts/acceptance_smoke.ps1` 可执行
- Web `/api/health` 正常返回
- 入队任务状态从 `pending` -> `running/success/retry_wait`
- 导出报表命令可执行
