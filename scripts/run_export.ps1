$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

.venv\Scripts\bili-archiver.exe export-reports --report-dir .\reports
