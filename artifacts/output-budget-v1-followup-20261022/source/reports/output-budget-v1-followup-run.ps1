$ErrorActionPreference='Stop'
$outputRoot='C:\Proj\robotics\introtorobotics'
$outputCampaign=Join-Path $outputRoot 'rosa-evaluation\artifacts\output-budget-v1-followup-20261022'
$outputSuccess=$false
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class OutputBudgetPower {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
$outputHeld=[OutputBudgetPower]::SetThreadExecutionState([uint32]2147483649)
if ($outputHeld -eq 0) { throw 'Could not acquire temporary sleep hold.' }
@{started_utc=[DateTime]::UtcNow.ToString('o');persistent_power_plan_changed=$false} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputCampaign 'operator\power-hold.json') -Encoding UTF8
try {
    & wsl.exe -d Ubuntu-24.04 --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.output_budget_v1_followup.runner *> (Join-Path $outputCampaign 'operator\live.log')
    if ($LASTEXITCODE -ne 0) { throw 'Output diagnostic stopped; inspect preserved checkpoint and live.log.' }
    & wsl.exe -d Ubuntu-24.04 --cd /mnt/c/Proj/robotics/introtorobotics/rosa-evaluation --exec /home/martin/.local/share/rosa-envs/phoenix/bin/python -B -m experiments.output_budget_v1_followup.combined_audit *> (Join-Path $outputCampaign 'operator\phoenix.log')
    if ($LASTEXITCODE -ne 0) { throw 'Independent persisted Phoenix audit failed.' }
    $outputSuccess=$true
} catch {
    @{status='FAILED';error=$_.Exception.Message;at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputRoot 'reports\OUTPUT_BUDGET_V1_FOLLOWUP_SUPERVISOR.json') -Encoding UTF8
    throw
} finally {
    try {
        Invoke-RestMethod -Uri 'http://172.31.0.1:11434/api/generate' -Method Post -ContentType 'application/json' -Body '{"model":"qwen3.5:9b","keep_alive":0}' -TimeoutSec 45 | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $outputCampaign 'operator\model-unload.json') -Encoding UTF8
    } finally {
        [OutputBudgetPower]::SetThreadExecutionState([uint32]2147483648) | Out-Null
        @{released_utc=[DateTime]::UtcNow.ToString('o');released=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputCampaign 'operator\power-release.json') -Encoding UTF8
    }
}
if ($outputSuccess) {
    & wsl.exe -d Ubuntu-24.04 --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.output_budget_v1_followup.analyze *> (Join-Path $outputRoot 'reports\output-budget-v1-followup-analysis.log')
    if ($LASTEXITCODE -ne 0) { throw 'Post-run analysis failed; raw data are preserved.' }
    @{status='COMPLETE';at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $outputRoot 'reports\OUTPUT_BUDGET_V1_FOLLOWUP_SUPERVISOR.json') -Encoding UTF8
}

