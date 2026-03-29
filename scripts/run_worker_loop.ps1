$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot\..

while ($true) {
    .venv\Scripts\bili-archiver.exe run-download-queue --batch-size 2
    Start-Sleep -Seconds 300
}
