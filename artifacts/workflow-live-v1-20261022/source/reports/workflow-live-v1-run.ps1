param([Parameter(Mandatory=$true)][ValidateSet('ollama','siwc')][string]$Backend)
$ErrorActionPreference='Stop'
$workflowRoot='C:\Proj\robotics\introtorobotics'
$workflowCampaign=Join-Path $workflowRoot 'rosa-evaluation\artifacts\workflow-live-v1-20261022'
$workflowOperator=Join-Path $workflowCampaign 'operator'
New-Item -ItemType Directory -Path $workflowOperator -Force | Out-Null
$workflowStatus=Join-Path $workflowOperator ($Backend+'-supervisor.json')
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class WorkflowPower {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
$workflowHeld=[WorkflowPower]::SetThreadExecutionState([uint32]2147483649)
if ($workflowHeld -eq 0) { throw 'Could not acquire temporary sleep hold.' }
@{status='RUNNING';backend=$Backend;started_utc=[DateTime]::UtcNow.ToString('o');pid=$PID} | ConvertTo-Json | Set-Content -LiteralPath $workflowStatus -Encoding UTF8
try {
    & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.workflow_live_v1.runner --backend $Backend *> (Join-Path $workflowOperator ($Backend+'-live.log'))
    if ($LASTEXITCODE -ne 0) { throw 'Workflow pilot stopped; checkpoint and evidence retained.' }
    @{status='COMPLETE';backend=$Backend;at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $workflowStatus -Encoding UTF8
} catch {
    @{status='STOPPED';backend=$Backend;at_utc=[DateTime]::UtcNow.ToString('o');error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath $workflowStatus -Encoding UTF8
} finally {
    [WorkflowPower]::SetThreadExecutionState([uint32]2147483648) | Out-Null
    @{released=$true;at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $workflowOperator ($Backend+'-power-release.json')) -Encoding UTF8
    & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.workflow_live_v1.analyze *> (Join-Path $workflowOperator ($Backend+'-analysis.log'))
}
