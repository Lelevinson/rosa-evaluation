param([ValidateSet('start','stop')][string]$Action)
$ErrorActionPreference = 'Stop'
$workspace = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$folder = Join-Path $workspace 'reports\phase4-v2'
New-Item -ItemType Directory -Path $folder -Force | Out-Null
$marker = Join-Path $folder 'monitor.stop'
if ($Action -eq 'start') {
    if (Test-Path -LiteralPath $marker) { throw 'This campaign monitor already stopped; preserve it and review before restarting.' }
    $script = Join-Path $PSScriptRoot 'phase4-monitor.ps1'
    $process = Start-Process -FilePath powershell.exe -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$script) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $folder 'monitor-output.log') -RedirectStandardError (Join-Path $folder 'monitor-errors.log')
    @{pid=$process.Id; started_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $folder 'monitor-process.json') -Encoding UTF8
    Write-Output 'Resource sampling and temporary system sleep hold started.'
} else {
    [System.IO.File]::WriteAllText($marker, 'Phase 4 live execution finished.')
    if (Test-Path -LiteralPath (Join-Path $folder 'monitor-process.json')) {
        $record = Get-Content -LiteralPath (Join-Path $folder 'monitor-process.json') -Raw | ConvertFrom-Json
        $running = Get-Process -Id $record.pid -ErrorAction SilentlyContinue
        if ($running) { Wait-Process -Id $running.Id -Timeout 30 }
    }
    Write-Output 'Resource sampler and temporary system sleep hold stopped.'
}
