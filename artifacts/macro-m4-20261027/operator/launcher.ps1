$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path $PSScriptRoot -Parent
$base = Join-Path $workspaceRoot 'rosa-evaluation/artifacts/macro-m4-20261027'
$controls = Get-Content -Raw -Encoding UTF8 (Join-Path $base 'controls/checkpoint.json') | ConvertFrom-Json
if ($controls.status -ne 'COMPLETE' -or $controls.primary_correct -ne 20 -or $controls.simulator_cleanup.returncode -ne 0 -or $controls.cleanup_errors.Count -ne 0) { throw 'M4 controls have not passed' }
$operator = Join-Path $base 'operator'
if (Test-Path -LiteralPath $operator) { throw 'Refusing duplicate M4 operator launch' }
New-Item -ItemType Directory -Path $operator | Out-Null
$utf8 = New-Object Text.UTF8Encoding($false)
$record = @{phase='STARTING';started=(Get-Date).ToString('o');backends=@();manual_review_pending=$true}
function Save-Status {
    $statusPath = Join-Path $operator 'status.json'
    $temporary = Join-Path $operator 'status.tmp'
    [IO.File]::WriteAllText($temporary, ($record | ConvertTo-Json -Depth 8), $utf8)
    Move-Item -LiteralPath $temporary -Destination $statusPath -Force
}
Save-Status
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'm4-run.ps1') -Destination (Join-Path $operator 'launcher.ps1')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'm4-archive.py') -Destination (Join-Path $operator 'archive.py')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'm4-offline-checks.py') -Destination (Join-Path $operator 'offline-checks.py')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'm4-development') -Destination (Join-Path $base 'development-checks') -Recurse
$preflight = Get-Content -Raw -Encoding UTF8 (Join-Path $base 'source/reports/m4-service-preflight.json') | ConvertFrom-Json
foreach ($backend in @('siwc','ollama')) {
    $record.phase = "RUNNING_$backend"
    Save-Status
    $arguments = @('-d','Ubuntu-24.04','-u','martin','--exec','bash','/mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh','experiments.macro_m4.runner','live','--backend',$backend)
    if ($backend -eq 'ollama') { $arguments += @('--endpoint', $preflight.endpoint) }
    $process = Start-Process -FilePath wsl.exe -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $operator "$backend-stdout.log") -RedirectStandardError (Join-Path $operator "$backend-stderr.log")
    $item = @{backend=$backend;pid=$process.Id;started=(Get-Date).ToString('o');exit_code=$null}
    $record.backends += $item
    Save-Status
    $process.WaitForExit()
    $item.exit_code = $process.ExitCode
    $item.finished = (Get-Date).ToString('o')
    Save-Status
}
$record.phase = 'SUMMARIZING'
Save-Status
$summaryArgs = @('-d','Ubuntu-24.04','-u','martin','--exec','bash','/mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh','experiments.macro_m4.report')
$summary = Start-Process -FilePath wsl.exe -ArgumentList $summaryArgs -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput (Join-Path $operator 'analysis-stdout.log') -RedirectStandardError (Join-Path $operator 'analysis-stderr.log')
$record.analysis_exit_code = $summary.ExitCode
$record.phase = 'EXECUTION_FINISHED_REVIEW_REQUIRED'
$record.finished = (Get-Date).ToString('o')
Save-Status
$archiveArgs = @('-d','Ubuntu-24.04','-u','martin','--exec','bash','/mnt/c/Proj/robotics/introtorobotics/reports/m1-command.sh','reports/m4-archive.py')
$archive = Start-Process -FilePath wsl.exe -ArgumentList $archiveArgs -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput (Join-Path $PSScriptRoot 'm4-archive-stdout.log') -RedirectStandardError (Join-Path $PSScriptRoot 'm4-archive-stderr.log')
Write-Output "M4 worker execution finished; archive exit $($archive.ExitCode). Transcript review remains required."
