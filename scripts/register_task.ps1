$taskName = "BiliChargeArchiverSync"
$scriptPath = (Resolve-Path ".\scripts\run_sync_all.ps1").Path

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""

$trigger = New-ScheduledTaskTrigger -Daily -At 9:00AM

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Description "Run Bili Charge Archiver daily sync" `
    -Force
