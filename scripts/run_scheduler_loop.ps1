$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$lockPath = ".\data\locks\scheduler.lock"
$stopPath = ".\data\locks\scheduler.stop"
$maxConsecutiveFailures = 10
$consecutiveFailures = 0

New-Item -ItemType Directory -Path ".\data\locks" -Force | Out-Null

if (Test-Path $stopPath) { Remove-Item $stopPath -Force }
if (Test-Path $lockPath) {
    $lastPid = Get-Content $lockPath -ErrorAction SilentlyContinue
    if ($lastPid -and (Get-Process -Id $lastPid -ErrorAction SilentlyContinue)) {
        Write-Host "scheduler loop 已在运行，锁文件存在: $lockPath pid=$lastPid"
        exit 1
    }
    Remove-Item $lockPath -Force
}

Set-Content -Path $lockPath -Value $PID -Encoding UTF8
try {
    while (-not (Test-Path $stopPath)) {
        try {
            .venv\Scripts\bili-archiver.exe run-scheduler-once
            if ($LASTEXITCODE -ne 0) {
                throw "run-scheduler-once exit code=$LASTEXITCODE"
            }
            $consecutiveFailures = 0
            Start-Sleep -Seconds 300
        }
        catch {
            $consecutiveFailures += 1
            Write-Warning "scheduler loop 执行失败($consecutiveFailures/$maxConsecutiveFailures): $($_.Exception.Message)"
            if ($consecutiveFailures -ge $maxConsecutiveFailures) {
                Write-Error "scheduler loop 连续失败次数过多，主动退出避免失控循环"
                break
            }
            Start-Sleep -Seconds 120
        }
    }
}
finally {
    if (Test-Path $lockPath) { Remove-Item $lockPath -Force }
    if (Test-Path $stopPath) { Remove-Item $stopPath -Force }
}
