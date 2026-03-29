$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot\..

Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File .\scripts\run_web.ps1"
Start-Process powershell -ArgumentList "-Command .\.venv\Scripts\bili-archiver.exe run-download-queue --batch-size 2"
Start-Process powershell -ArgumentList "-Command .\.venv\Scripts\bili-archiver.exe batch-sync"
