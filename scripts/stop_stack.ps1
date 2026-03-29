$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot\..

@(".\data\locks\download_worker.stop", ".\data\locks\scheduler.stop") | ForEach-Object {
    New-Item -Path $_ -ItemType File -Force | Out-Null
}

@("web", "worker", "scheduler") | ForEach-Object {
    $pidFile = ".\data\run\$_.pid"
    if (Test-Path $pidFile) {
        $rawPid = (Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
        $pidValue = 0
        if ([int]::TryParse($rawPid, [ref]$pidValue) -and $pidValue -gt 0) {
            Stop-Process -Id $pidValue -Force -ErrorAction SilentlyContinue
        }
        else {
            Write-Warning "pid 文件内容无效，跳过停止: $pidFile"
        }
        Remove-Item $pidFile -Force
    }
}

Write-Host "stack stop requested"
