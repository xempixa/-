$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

.\.venv\Scripts\bili-archiver.exe healthcheck
try {
    .\.venv\Scripts\python.exe -c "import urllib.request;print(urllib.request.urlopen('http://127.0.0.1:8000/api/health').read().decode())"
}
catch {
    Write-Host "web health endpoint 未就绪: $($_.Exception.Message)"
}
