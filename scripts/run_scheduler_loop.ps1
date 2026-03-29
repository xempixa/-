$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$lockPath = ".\data\locks\scheduler.lock"
$stopPath = ".\data\locks\scheduler.stop"
New-Item -ItemType Directory -Path ".\data\locks" -Force | Out-Null

if (Test-Path $stopPath) { Remove-Item $stopPath -Force }
if (Test-Path $lockPath) {
    Write-Host "scheduler loop 已在运行，锁文件存在: $lockPath"
    exit 1
}

Set-Content -Path $lockPath -Value $PID -Encoding UTF8
try {
    while (-not (Test-Path $stopPath)) {
        .venv\Scripts\bili-archiver.exe run-scheduler-once
        Start-Sleep -Seconds 300
    }
}
finally {
    if (Test-Path $lockPath) { Remove-Item $lockPath -Force }
    if (Test-Path $stopPath) { Remove-Item $stopPath -Force }
}
