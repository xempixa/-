$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$lockPath = ".\data\locks\download_worker.lock"
$stopPath = ".\data\locks\download_worker.stop"
New-Item -ItemType Directory -Path ".\data\locks" -Force | Out-Null

if (Test-Path $stopPath) { Remove-Item $stopPath -Force }
if (Test-Path $lockPath) {
    $lastPid = Get-Content $lockPath -ErrorAction SilentlyContinue
    if ($lastPid -and (Get-Process -Id $lastPid -ErrorAction SilentlyContinue)) {
        Write-Host "download worker loop 已在运行，锁文件存在: $lockPath pid=$lastPid"
        exit 1
    }
    Remove-Item $lockPath -Force
}

Set-Content -Path $lockPath -Value $PID -Encoding UTF8
try {
    while (-not (Test-Path $stopPath)) {
        .venv\Scripts\bili-archiver.exe run-download-queue --batch-size 2
        Start-Sleep -Seconds 30
    }
}
finally {
    if (Test-Path $lockPath) { Remove-Item $lockPath -Force }
    if (Test-Path $stopPath) { Remove-Item $stopPath -Force }
}
