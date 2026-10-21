param([string]$OutputDirectory = 'C:\Proj\robotics\introtorobotics\rosa-evaluation\artifacts\stage4-batching-completion-20261021')
$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class Stage4Power {
  [DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint flags);
}
'@
$marker = Join-Path $OutputDirectory 'monitor.stop'
$held = [Stage4Power]::SetThreadExecutionState([uint32]2147483649)
@{ held = ($held -ne 0); started_utc = [DateTime]::UtcNow.ToString('o'); pid = $PID } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDirectory 'power-hold.json') -Encoding UTF8
try {
  while (-not (Test-Path -LiteralPath $marker)) {
    $memory = Get-CimInstance Win32_OperatingSystem
    [pscustomobject]@{ utc = [DateTime]::UtcNow.ToString('o'); free_ram_kib = $memory.FreePhysicalMemory; free_virtual_kib = $memory.FreeVirtualMemory } | Export-Csv -LiteralPath (Join-Path $OutputDirectory 'resource-samples.csv') -NoTypeInformation -Append
    Start-Sleep -Seconds 10
  }
} finally {
  [void][Stage4Power]::SetThreadExecutionState([uint32]2147483648)
  @{ released_utc = [DateTime]::UtcNow.ToString('o') } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDirectory 'power-release.json') -Encoding UTF8
}
