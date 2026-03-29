$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Test-Path ".\.venv")) {
    py -3.11 -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\playwright.exe install chromium

if (-not (Test-Path ".\.env")) {
    Copy-Item ".\.env.example" ".\.env"
}

.\.venv\Scripts\bili-archiver.exe init-db
Write-Host "初始化完成。请先执行 bili-archiver login 完成登录态。"
