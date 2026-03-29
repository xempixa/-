$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot\..

.venv\Scripts\bili-archiver.exe init-db
.venv\Scripts\bili-archiver.exe sync-creator-feed --host-uid 123456 --limit-pages 2
.venv\Scripts\bili-archiver.exe run-download-queue --batch-size 2
