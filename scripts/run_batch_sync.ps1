$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

.venv\Scripts\bili-archiver.exe healthcheck
.venv\Scripts\bili-archiver.exe batch-sync
.venv\Scripts\bili-archiver.exe run-download-queue --batch-size 3
