param([ValidateSet('ollama','siwc')][string]$Backend)
$ErrorActionPreference = 'Stop'
$promptLiveRoot = 'C:\Proj\robotics\introtorobotics'
$promptLiveCampaign = Join-Path $promptLiveRoot 'rosa-evaluation\artifacts\prompt-contract-v1-live-20261026'
$promptLiveOperator = Join-Path $promptLiveCampaign ('operator-' + $Backend)
New-Item -ItemType Directory -Path $promptLiveOperator -Force | Out-Null
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class PromptLivePower {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
if ([PromptLivePower]::SetThreadExecutionState([uint32]2147483649) -eq 0) { throw 'Sleep hold unavailable.' }
@{status='RUNNING';pid=$PID;backend=$Backend;started_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $promptLiveOperator 'supervisor.json') -Encoding UTF8
try {
    & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.prompt_live_v1.runner --backend $Backend *> (Join-Path $promptLiveOperator 'live.log')
    if ($LASTEXITCODE -ne 0) { throw 'Live validation stopped; saved evidence retained.' }
    @{status='COMPLETE';at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $promptLiveOperator 'supervisor.json') -Encoding UTF8
} catch {
    @{status='STOPPED';at_utc=[DateTime]::UtcNow.ToString('o');error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $promptLiveOperator 'supervisor.json') -Encoding UTF8
} finally {
    [PromptLivePower]::SetThreadExecutionState([uint32]2147483648) | Out-Null
    @{released=$true;at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $promptLiveOperator 'power-release.json') -Encoding UTF8
}
