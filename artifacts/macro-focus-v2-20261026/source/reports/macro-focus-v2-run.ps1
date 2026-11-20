param([ValidateSet('ollama','siwc')][string]$Backend)
$ErrorActionPreference = 'Stop'
$focusRoot = 'C:\Proj\robotics\introtorobotics'
$focusCampaign = Join-Path $focusRoot 'rosa-evaluation\artifacts\macro-focus-v2-20261026'
$focusOperator = Join-Path $focusCampaign ('operator-' + $Backend)
if (Test-Path -LiteralPath (Join-Path $focusOperator 'supervisor.json')) { throw 'Already attempted; preserve original logs and results.' }
New-Item -ItemType Directory -Path $focusOperator -Force | Out-Null
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class FocusPower {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
if ([FocusPower]::SetThreadExecutionState([uint32]2147483649) -eq 0) { throw 'Sleep hold unavailable.' }
@{status='RUNNING';pid=$PID;backend=$Backend;started_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $focusOperator 'supervisor.json') -Encoding UTF8
try {
    & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.macro_focus_v2.runner --backend $Backend *> (Join-Path $focusOperator 'live.log')
    if ($LASTEXITCODE -ne 0) { throw 'Fresh pilot stopped; saved evidence retained.' }
    @{status='COMPLETE';at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $focusOperator 'supervisor.json') -Encoding UTF8
} catch {
    @{status='STOPPED';at_utc=[DateTime]::UtcNow.ToString('o');error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $focusOperator 'supervisor.json') -Encoding UTF8
} finally {
    [FocusPower]::SetThreadExecutionState([uint32]2147483648) | Out-Null
    @{released=$true;at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $focusOperator 'power-release.json') -Encoding UTF8
    @{ready=$true;at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $focusCampaign ('analysis-ready-' + $Backend + '.json')) -Encoding UTF8
    if ((Test-Path -LiteralPath (Join-Path $focusCampaign 'analysis-ready-ollama.json')) -and (Test-Path -LiteralPath (Join-Path $focusCampaign 'analysis-ready-siwc.json'))) {
        & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.macro_focus_v2.analysis *> (Join-Path $focusOperator 'analysis.log')
    }
}
