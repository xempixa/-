$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot\..

@(".\data\locks\download_worker.stop", ".\data\locks\scheduler.stop") | ForEach-Object {
    New-Item -Path $_ -ItemType File -Force | Out-Null
}

@("web", "worker", "scheduler") | ForEach-Object {
    $pidFile = ".\data\run\$_.pid"
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile
        if ($pid) {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
        Remove-Item $pidFile -Force
    }
}

Write-Host "stack stop requested"
