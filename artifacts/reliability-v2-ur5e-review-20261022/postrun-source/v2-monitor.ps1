$ErrorActionPreference='Stop'
$v2Folder='C:\Proj\robotics\introtorobotics\rosa-evaluation\artifacts\reliability-v2-20261022\operator'
New-Item -ItemType Directory -Path $v2Folder -Force | Out-Null
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class ReliabilityV2Power {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
$v2Held=[ReliabilityV2Power]::SetThreadExecutionState([uint32]2147483649)
if ($v2Held -eq 0) { throw 'Could not acquire temporary system sleep hold.' }
@{started_utc=[DateTime]::UtcNow.ToString('o');persistent_power_plan_changed=$false;display_required=$false} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $v2Folder 'power-hold.json') -Encoding UTF8
$v2Deadline=[DateTime]::UtcNow.AddHours(8)
try {
    while (!(Test-Path -LiteralPath (Join-Path $v2Folder 'monitor.stop')) -and [DateTime]::UtcNow -lt $v2Deadline) {
        try {
            $v2Gpu=(& nvidia-smi --query-gpu=memory.used,utilization.gpu,temperature.gpu --format=csv,noheader,nounits | Select-Object -First 1) -split ','
            $v2Os=Get-CimInstance Win32_OperatingSystem
            [pscustomobject]@{observed_utc=[DateTime]::UtcNow.ToString('o');gpu_memory_mib=$v2Gpu[0].Trim();gpu_utilization=$v2Gpu[1].Trim();gpu_temp_c=$v2Gpu[2].Trim();free_ram_mib=[math]::Round($v2Os.FreePhysicalMemory/1024)} | Export-Csv -LiteralPath (Join-Path $v2Folder 'resources.csv') -Append -NoTypeInformation -Encoding UTF8
        } catch {
            $_.Exception.Message | Add-Content -LiteralPath (Join-Path $v2Folder 'monitor-errors.log')
        }
        Start-Sleep -Seconds 10
    }
} finally {
    [ReliabilityV2Power]::SetThreadExecutionState([uint32]2147483648) | Out-Null
    @{released_utc=[DateTime]::UtcNow.ToString('o');released=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $v2Folder 'power-release.json') -Encoding UTF8
}
