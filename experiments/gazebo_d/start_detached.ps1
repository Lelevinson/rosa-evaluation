# Start a Gazebo D job fully detached from VS Code (and from this terminal).
# The wsl.exe process is created through WMI (Win32_Process.Create), so its parent is the WMI provider host,
# not VS Code: closing or restarting VS Code cannot kill it. The job writes all logs/state to disk (job.sh).
# It does NOT protect against sleep, shutdown, reboot or `wsl --shutdown`.
#
# Usage (from any PowerShell):
#   powershell -NoProfile -File <repo>\experiments\gazebo_d\start_detached.ps1 -RepoRoot C:\Proj\...\<worktree> -Stage dev -Models artifacts\gazebo-d-20261121\models.json
# Check progress: <RepoRoot>\artifacts\gazebo-d-20261121\jobs\<stage>-*\job.json, runner.log, and runs\<stage>\status.json
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][ValidateSet('controls', 'dev', 'heldout')][string]$Stage,
    [string]$Models = '',
    [string]$Distro = 'Ubuntu-24.04',
    [string]$User = 'martin'
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $RepoRoot).Path
if (-not (Test-Path -LiteralPath (Join-Path $root 'experiments\gazebo_d\job.sh'))) { throw "job.sh not found under $root" }
if ($Stage -ne 'controls' -and -not $Models) { throw 'Models (path relative to RepoRoot) is required for dev/heldout' }
function ConvertTo-WslPath([string]$p) {
    $full = [IO.Path]::GetFullPath($p)
    '/mnt/' + $full.Substring(0, 1).ToLower() + ($full.Substring(2) -replace '\\', '/')
}
$wslRoot = ConvertTo-WslPath $root
$command = "wsl.exe -d $Distro -u $User --exec bash $wslRoot/experiments/gazebo_d/job.sh $wslRoot $Stage $Models"
$result = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $command; CurrentDirectory = $root }
if ($result.ReturnValue -ne 0) { throw "Win32_Process.Create failed: $($result.ReturnValue)" }
$launch = [ordered]@{ stage = $Stage; windows_pid = $result.ProcessId; command = $command; launched = (Get-Date).ToString('o') }
$dir = Join-Path $root 'artifacts\gazebo-d-20261121\jobs'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$utf8 = New-Object Text.UTF8Encoding($false)
[IO.File]::AppendAllText((Join-Path $dir 'LAUNCHES.jsonl'), (($launch | ConvertTo-Json -Compress) + "`n"), $utf8)
Write-Output "Started detached: windows pid $($result.ProcessId). Logs: $dir\$Stage-<timestamp>\"
