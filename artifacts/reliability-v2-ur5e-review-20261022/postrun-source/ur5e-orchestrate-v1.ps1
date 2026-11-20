$ErrorActionPreference='Stop'
$urRoot='C:\Proj\robotics\introtorobotics'
$urCampaign=Join-Path $urRoot 'rosa-evaluation\artifacts\ur5e-transfer-v1-20261022'
$urDeadline=[DateTime]::UtcNow.AddHours(3)
$urComplete=$false
try {
    do {
        $urStatusPath=Join-Path $urCampaign 'gazebo\siwc\result.json'
        if (Test-Path $urStatusPath) {
            $urStatus=Get-Content $urStatusPath -Raw | ConvertFrom-Json
            if ($urStatus.status -eq 'COMPLETE') { break }
            if ($urStatus.status -eq 'FAILED' -or $urStatus.status -like 'STOPPED*') { throw "Hosted arm batch stopped: $($urStatus.error)" }
        }
        if (Test-Path (Join-Path $urCampaign 'session-siwc-gazebo.json')) { throw 'Hosted session ended before completion.' }
        Start-Sleep -Seconds 5
    } while ([DateTime]::UtcNow -lt $urDeadline)
    if ([DateTime]::UtcNow -ge $urDeadline) { throw 'Hosted wait limit reached.' }
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $urRoot 'rosa-research\scripts\start-research.ps1') *> (Join-Path $urCampaign 'operator\services.log')
    if ($LASTEXITCODE -ne 0) { throw 'Local inference service startup failed.' }
    & wsl.exe -d Ubuntu-24.04 --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.ur5e_transfer_v1.runner --backend ollama --phase gazebo *> (Join-Path $urCampaign 'operator\local.log')
    if ($LASTEXITCODE -ne 0) { throw 'Local arm batch failed.' }
    & wsl.exe -d Ubuntu-24.04 --cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation --exec /home/martin/.local/share/rosa-envs/phoenix/bin/python -B -m experiments.ur5e_transfer_v1.phoenix_audit --phase gazebo *> (Join-Path $urCampaign 'operator\phoenix.log')
    if ($LASTEXITCODE -ne 0) { throw 'Independent persisted Phoenix audit failed.' }
    Invoke-RestMethod -Uri 'http://172.31.0.1:11434/api/generate' -Method Post -ContentType 'application/json' -Body '{"model":"qwen3.5:9b","keep_alive":0}' -TimeoutSec 45 | Out-Null
    $urComplete=$true
} catch {
    @{status='FAILED';error=$_.Exception.Message;at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content (Join-Path $urRoot 'reports\UR5E_TRANSFER_V1_ORCHESTRATOR.json') -Encoding UTF8
    throw
} finally {
    Set-Content -LiteralPath (Join-Path $urCampaign 'operator\monitor.stop') -Value 'stop'
}
if ($urComplete) {
    Start-Sleep -Seconds 12
    & wsl.exe -d Ubuntu-24.04 --exec /home/martin/.local/share/rosa-envs/research/bin/python -B /mnt/c/Proj/robotics/introtorobotics/reports/v2-review.py *> (Join-Path $urRoot 'reports\ur5e-combined-review.log')
    if ($LASTEXITCODE -ne 0) { throw 'Combined independent review failed; raw results are preserved.' }
    @{status='COMPLETE';at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content (Join-Path $urRoot 'reports\UR5E_TRANSFER_V1_ORCHESTRATOR.json') -Encoding UTF8
}
