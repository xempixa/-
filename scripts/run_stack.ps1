$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

New-Item -ItemType Directory -Path ".\data\run" -Force | Out-Null

$web = Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File .\scripts\run_web.ps1" -PassThru
$worker = Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File .\scripts\run_worker_loop.ps1" -PassThru
$scheduler = Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File .\scripts\run_scheduler_loop.ps1" -PassThru

Set-Content -Path ".\data\run\web.pid" -Value $web.Id -Encoding UTF8
Set-Content -Path ".\data\run\worker.pid" -Value $worker.Id -Encoding UTF8
Set-Content -Path ".\data\run\scheduler.pid" -Value $scheduler.Id -Encoding UTF8

Write-Host "stack started: web=$($web.Id) worker=$($worker.Id) scheduler=$($scheduler.Id)"
