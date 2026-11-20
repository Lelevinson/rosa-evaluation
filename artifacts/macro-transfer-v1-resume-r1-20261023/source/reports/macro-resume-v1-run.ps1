$ErrorActionPreference = 'Stop'
$resumeRoot = 'C:\Proj\robotics\introtorobotics'
$resumeCampaign = Join-Path $resumeRoot 'rosa-evaluation\artifacts\macro-transfer-v1-resume-r1-20261023'
$resumeOperator = Join-Path $resumeCampaign 'operator'
New-Item -ItemType Directory -Path $resumeOperator -Force | Out-Null
$resumeStatus = Join-Path $resumeOperator 'supervisor.json'
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class ResumePower {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
if ([ResumePower]::SetThreadExecutionState([uint32]2147483649) -eq 0) { throw 'Sleep hold unavailable.' }
@{status='RUNNING';pid=$PID;started_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $resumeStatus -Encoding UTF8
try {
    & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.macro_resume_v1.runner --execute *> (Join-Path $resumeOperator 'live.log')
    if ($LASTEXITCODE -ne 0) { throw 'Continuation stopped; saved evidence retained.' }
    @{status='COMPLETE';at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $resumeStatus -Encoding UTF8
} catch {
    @{status='STOPPED';at_utc=[DateTime]::UtcNow.ToString('o');error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath $resumeStatus -Encoding UTF8
} finally {
    [ResumePower]::SetThreadExecutionState([uint32]2147483648) | Out-Null
    @{released=$true;at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $resumeOperator 'power-release.json') -Encoding UTF8
    & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/macro-resume-v1-finalize.sh *> (Join-Path $resumeOperator 'finalization.log')
    if ($LASTEXITCODE -ne 0) {
        @{status='STOPPED';reason='Finalization failed; raw evidence preserved.'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $resumeOperator 'finalization-status.json') -Encoding UTF8
    }
}
