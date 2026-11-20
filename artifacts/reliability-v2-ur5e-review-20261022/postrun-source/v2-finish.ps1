$ErrorActionPreference='Stop'
$v2Workspace='C:\Proj\robotics\introtorobotics'
$v2Campaign=Join-Path $v2Workspace 'rosa-evaluation\artifacts\reliability-v2-20261022'
$v2ReceiptPath=Join-Path $v2Workspace 'reports\RELIABILITY_V2_ORCHESTRATOR.json'
$v2Deadline=[DateTime]::UtcNow.AddHours(8)
try {
    while ([DateTime]::UtcNow -lt $v2Deadline) {
        if (Test-Path $v2ReceiptPath) {
            $v2Receipt=Get-Content $v2ReceiptPath -Raw | ConvertFrom-Json
            if ($v2Receipt.status -eq 'FAILED') { throw $v2Receipt.error }
            if ($v2Receipt.status -eq 'LIVE_PHASES_COMPLETE') { break }
        }
        Start-Sleep -Seconds 10
    }
    if ([DateTime]::UtcNow -ge $v2Deadline) { throw 'Finalizer wait limit reached.' }
    $v2CleanupDeadline=[DateTime]::UtcNow.AddMinutes(3)
    do {
        $v2AuthReady=Test-Path (Join-Path $v2Campaign 'session-siwc-pipeline.json')
        $v2Hold=Get-Content (Join-Path $v2Campaign 'operator\power-hold.json') -Raw | ConvertFrom-Json
        $v2Released=$false
        if (Test-Path (Join-Path $v2Campaign 'operator\power-release.json')) {
            $v2Release=Get-Content (Join-Path $v2Campaign 'operator\power-release.json') -Raw | ConvertFrom-Json
            $v2Released=([DateTime]$v2Release.released_utc -ge [DateTime]$v2Hold.started_utc)
        }
        if ($v2AuthReady -and $v2Released) { break }
        Start-Sleep -Seconds 3
    } while ([DateTime]::UtcNow -lt $v2CleanupDeadline)
    if (!$v2AuthReady -or !$v2Released) { throw 'Session or temporary-power cleanup was not confirmed.' }
    $v2PostSource=Join-Path $v2Campaign 'postrun-source\operator'
    New-Item -ItemType Directory -Path $v2PostSource -Force | Out-Null
    Get-ChildItem (Join-Path $v2Workspace 'reports') -Filter 'v2-*' -File | Where-Object { $_.Extension -in @('.ps1','.sh','.py') } | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $v2PostSource }
    & wsl.exe -d Ubuntu-24.04 --exec /home/martin/.local/share/rosa-envs/research/bin/python -B /mnt/c/Proj/robotics/introtorobotics/reports/v2-review.py *> (Join-Path $v2Workspace 'reports\v2-final-review.log')
    if ($LASTEXITCODE -ne 0) { throw 'Independent final review failed; evidence preserved without sealing.' }
    @{status='COMPLETE';at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content (Join-Path $v2Workspace 'reports\RELIABILITY_V2_FINISHER.json') -Encoding UTF8
} catch {
    @{status='FAILED';error=$_.Exception.Message;at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content (Join-Path $v2Workspace 'reports\RELIABILITY_V2_FINISHER.json') -Encoding UTF8
    throw
}
