$ErrorActionPreference='Stop'
$v2Workspace='C:\Proj\robotics\introtorobotics'
$v2Campaign=Join-Path $v2Workspace 'rosa-evaluation\artifacts\reliability-v2-20261022'
$v2Utf8=New-Object System.Text.UTF8Encoding($false)
function Write-V2Json([string]$Path,$Value) {
    [IO.File]::WriteAllText($Path+'.tmp',($Value | ConvertTo-Json -Depth 14),$v2Utf8)
    Move-Item -LiteralPath ($Path+'.tmp') -Destination $Path -Force
}
function Wait-V2Phase([string]$Phase,[string]$Backend) {
    $v2Deadline=[DateTime]::UtcNow.AddHours(3)
    $v2StatusPath=Join-Path $v2Campaign "$Phase\$Backend\result.json"
    while ([DateTime]::UtcNow -lt $v2Deadline) {
        if (Test-Path -LiteralPath $v2StatusPath) {
            $v2Status=Get-Content -LiteralPath $v2StatusPath -Raw | ConvertFrom-Json
            if ($v2Status.status -eq 'COMPLETE') { return $v2Status }
            if ($v2Status.status -eq 'FAILED' -or $v2Status.status -like 'STOPPED*') { throw "$Backend/$Phase stopped: $($v2Status.error)" }
        }
        if ($Backend -eq 'siwc' -and (Test-Path -LiteralPath (Join-Path $v2Campaign 'session-siwc-pipeline.json'))) {
            throw "Hosted session ended before $Phase completed."
        }
        Start-Sleep -Seconds 5
    }
    throw "$Backend/$Phase exceeded the three-hour wait."
}
function Run-V2Local([string]$Phase) {
    $v2Log=Join-Path $v2Campaign "operator\local-$Phase.log"
    & wsl.exe -d Ubuntu-24.04 --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.reliability_v2.runner --backend ollama --phase $Phase *> $v2Log
    if ($LASTEXITCODE -ne 0) { throw "Qwen $Phase process failed; inspect $v2Log" }
}
function Audit-V2([string]$Phase) {
    & wsl.exe -d Ubuntu-24.04 --cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation --exec /home/martin/.local/share/rosa-envs/phoenix/bin/python -B -m experiments.reliability_v2.phoenix_audit --phase $Phase *> (Join-Path $v2Campaign "operator\phoenix-$Phase.log")
    if ($LASTEXITCODE -ne 0) { throw "Phoenix $Phase full audit failed." }
}
function Unload-V2Qwen {
    $v2Unload=Invoke-RestMethod -Uri 'http://172.31.0.1:11434/api/generate' -Method Post -ContentType 'application/json' -Body '{"model":"qwen3.5:9b","keep_alive":0}' -TimeoutSec 45
    Write-V2Json (Join-Path $v2Campaign 'operator\last-qwen-unload.json') @{done=$v2Unload.done;observed_utc=[DateTime]::UtcNow.ToString('o')}
}
$v2Completed=$false
try {
    Wait-V2Phase 'validation' 'siwc' | Out-Null
    Run-V2Local 'validation'
    Audit-V2 'validation'
    Unload-V2Qwen
    Write-V2Json (Join-Path $v2Campaign 'validation-gate.json') @{pass=$true;both_backends_completed=$true;phoenix_full_audit=$true;offline_tests=60;scripted_controls=40;at_utc=[DateTime]::UtcNow.ToString('o')}
    Wait-V2Phase 'mock' 'siwc' | Out-Null
    Run-V2Local 'mock'
    Audit-V2 'mock'
    Unload-V2Qwen
    & wsl.exe -d Ubuntu-24.04 -u root --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-install-arm.sh *> (Join-Path $v2Campaign 'operator\arm-install.log')
    if ($LASTEXITCODE -ne 0) { throw 'UR5e dependencies did not install.' }
    & wsl.exe -d Ubuntu-24.04 --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-arm-control.sh *> (Join-Path $v2Campaign 'operator\arm-control.log')
    if ($LASTEXITCODE -ne 0) { throw 'UR5e deterministic controls failed.' }
    $v2Controls=Get-Content (Join-Path $v2Campaign 'deterministic-arm\result.json') -Raw | ConvertFrom-Json
    if ($v2Controls.status -ne 'COMPLETE' -or $v2Controls.rows.Count -ne 4) { throw 'Incomplete deterministic controls.' }
    Write-V2Json (Join-Path $v2Campaign 'arm-gate.json') @{pass=$true;mock_completed_both=$true;mock_full_phoenix_audit=$true;deterministic_arm_controls=4;at_utc=[DateTime]::UtcNow.ToString('o')}
    Wait-V2Phase 'gazebo' 'siwc' | Out-Null
    Run-V2Local 'gazebo'
    Audit-V2 'gazebo'
    Unload-V2Qwen
    $v2Completed=$true
} catch {
    $v2Message=$_.Exception.Message
    foreach ($v2GateName in @('validation-gate.json','arm-gate.json')) {
        $v2GatePath=Join-Path $v2Campaign $v2GateName
        if (!(Test-Path -LiteralPath $v2GatePath)) { Write-V2Json $v2GatePath @{pass=$false;reason=$v2Message} }
    }
    Write-V2Json (Join-Path $v2Workspace 'reports\RELIABILITY_V2_ORCHESTRATOR.json') @{status='FAILED';error=$v2Message;at_utc=[DateTime]::UtcNow.ToString('o')}
    throw
} finally {
    [IO.File]::WriteAllText((Join-Path $v2Campaign 'operator\monitor.stop'),'stop',$v2Utf8)
    if ($v2Completed) {
        Write-V2Json (Join-Path $v2Workspace 'reports\RELIABILITY_V2_ORCHESTRATOR.json') @{status='LIVE_PHASES_COMPLETE';at_utc=[DateTime]::UtcNow.ToString('o')}
    }
}
