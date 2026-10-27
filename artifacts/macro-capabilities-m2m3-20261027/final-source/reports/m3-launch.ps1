param([ValidateSet('ollama','siwc')][string]$Backend)
$ErrorActionPreference = 'Stop'
$workspace = Split-Path $PSScriptRoot -Parent
$destination = Join-Path $workspace 'rosa-evaluation/artifacts/macro-capabilities-m2m3-20261027'
$operator = Join-Path $destination "operator-$Backend"
if (Test-Path -LiteralPath $operator) { throw 'Existing operator directory; refuse duplicate launch' }
New-Item -ItemType Directory -Path $operator | Out-Null
$arguments = @('-d','Ubuntu-24.04','-u','martin','--exec','bash','/mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh','experiments.macro_capabilities_v2.m3','--backend',$Backend)
if ($Backend -eq 'ollama') {
    $preflight = Get-Content -Raw -Encoding UTF8 (Join-Path $destination 'ollama-preflight.json') | ConvertFrom-Json
    $arguments += @('--ollama-url',$preflight.endpoint)
}
$child = Start-Process -FilePath wsl.exe -ArgumentList $arguments -WorkingDirectory $workspace -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $operator 'stdout.log') -RedirectStandardError (Join-Path $operator 'stderr.log')
@{pid=$child.Id;backend=$Backend;launched=(Get-Date).ToString('o');request_cap=24} | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $operator 'launch.json')
Write-Output "M3 $Backend worker started, PID $($child.Id)"
