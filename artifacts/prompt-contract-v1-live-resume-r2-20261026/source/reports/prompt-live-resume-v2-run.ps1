$ErrorActionPreference = 'Stop'
$repairResumeCampaign = 'C:\Proj\robotics\introtorobotics\rosa-evaluation\artifacts\prompt-contract-v1-live-resume-r2-20261026'
$repairResumeOperator = Join-Path $repairResumeCampaign 'operator'
if (Test-Path -LiteralPath (Join-Path $repairResumeOperator 'supervisor.json')) { throw 'Continuation already attempted.' }
New-Item -ItemType Directory -Path $repairResumeOperator -Force | Out-Null
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class RepairResume2Power {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
if ([RepairResume2Power]::SetThreadExecutionState([uint32]2147483649) -eq 0) { throw 'Sleep hold unavailable.' }
@{status='RUNNING';pid=$PID;started_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $repairResumeOperator 'supervisor.json') -Encoding UTF8
try {
    & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.prompt_live_resume_v2.runner --execute *> (Join-Path $repairResumeOperator 'live.log')
    if ($LASTEXITCODE -ne 0) { throw 'Continuation stopped; no retry loop. Evidence retained.' }
    @{status='COMPLETE';at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $repairResumeOperator 'supervisor.json') -Encoding UTF8
} catch {
    @{status='STOPPED';at_utc=[DateTime]::UtcNow.ToString('o');error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $repairResumeOperator 'supervisor.json') -Encoding UTF8
} finally {
    [RepairResume2Power]::SetThreadExecutionState([uint32]2147483648) | Out-Null
    @{released=$true;at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $repairResumeOperator 'power-release.json') -Encoding UTF8
    & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.prompt_live_resume_v2.analysis *> (Join-Path $repairResumeOperator 'analysis.log')
}


