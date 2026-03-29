$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

.\.venv\Scripts\bili-archiver.exe healthcheck
.\.venv\Scripts\bili-archiver.exe run-scheduler-once
.\.venv\Scripts\bili-archiver.exe enqueue-download --bvid BV1xx411c7mD
.\.venv\Scripts\bili-archiver.exe run-download-queue --batch-size 1
.\.venv\Scripts\bili-archiver.exe export-reports --report-dir .\reports
