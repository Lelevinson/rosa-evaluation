$ErrorActionPreference = 'Stop'
$workspace = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$folder = Join-Path $workspace 'reports\phase4-v2'
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class Phase4Power {
    [DllImport("kernel32.dll", SetLastError=true)]
    public static extern uint SetThreadExecutionState(uint flags);
}
'@
$held = [Phase4Power]::SetThreadExecutionState([uint32]2147483649)
if ($held -eq 0) { throw 'Could not acquire temporary system sleep hold.' }
@{started_utc=[DateTime]::UtcNow.ToString('o'); persistent_power_plan_changed=$false; display_required=$false} |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $folder 'power-hold.json') -Encoding UTF8
try {
    while (!(Test-Path -LiteralPath (Join-Path $folder 'monitor.stop'))) {
        $gpu = (& nvidia-smi --query-gpu=memory.used,utilization.gpu,power.draw,temperature.gpu --format=csv,noheader,nounits | Select-Object -First 1) -split ','
        $os = Get-CimInstance Win32_OperatingSystem
        [pscustomobject]@{observed_utc=[DateTime]::UtcNow.ToString('o'); gpu_memory_mib=$gpu[0].Trim(); gpu_utilization=$gpu[1].Trim(); gpu_power_w=$gpu[2].Trim(); gpu_temp_c=$gpu[3].Trim(); free_ram_mib=[math]::Round($os.FreePhysicalMemory/1024)} |
            Export-Csv -LiteralPath (Join-Path $folder 'resource-samples.csv') -Append -NoTypeInformation -Encoding UTF8
        Start-Sleep -Seconds 10
    }
} finally {
    [Phase4Power]::SetThreadExecutionState([uint32]2147483648) | Out-Null
    @{released_utc=[DateTime]::UtcNow.ToString('o'); released=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $folder 'power-release.json') -Encoding UTF8
}
