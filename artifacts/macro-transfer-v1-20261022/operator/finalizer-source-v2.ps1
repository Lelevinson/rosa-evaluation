$ErrorActionPreference = 'Stop'
$macroRoot = 'C:\Proj\robotics\introtorobotics'
$macroCampaign = Join-Path $macroRoot 'rosa-evaluation\artifacts\macro-transfer-v1-20261022'
$macroOperator = Join-Path $macroCampaign 'operator'
$macroStatus = Join-Path $macroOperator 'finalizer-status.json'
$macroDeadline = [DateTime]::UtcNow.AddHours(4)
@{status='WAITING_FOR_BACKENDS';at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $macroStatus -Encoding UTF8
try {
    while ($true) {
        if ([DateTime]::UtcNow -gt $macroDeadline) { throw 'Finalizer wait deadline exceeded; evidence retained.' }
        $macroReady = $true
        $macroComplete = $true
        foreach ($macroBackend in @('ollama','siwc')) {
            $macroSupervisor = Join-Path $macroOperator ($macroBackend+'-supervisor.json')
            $macroRelease = Join-Path $macroOperator ($macroBackend+'-power-release.json')
            if (!(Test-Path -LiteralPath $macroSupervisor) -or !(Test-Path -LiteralPath $macroRelease)) {
                $macroReady = $false
                continue
            }
            try { $macroState = Get-Content -LiteralPath $macroSupervisor -Raw | ConvertFrom-Json } catch { $macroReady = $false; continue }
            if ($macroState.status -notin @('COMPLETE','STOPPED')) { $macroReady = $false }
            if ($macroState.status -ne 'COMPLETE') { $macroComplete = $false }
        }
        # Status and sleep-release receipts precede each supervisor's last analysis.
        # Wait for the actual supervisors to exit so archived logs cannot change.
        foreach ($macroLaunch in (Get-Content -LiteralPath (Join-Path $macroOperator 'launches.json') -Raw | ConvertFrom-Json)) {
            $macroParent = Get-Process -Id $macroLaunch.pid -ErrorAction SilentlyContinue
            if ($macroParent -and $macroParent.ProcessName -eq 'powershell' -and
                [math]::Abs(($macroParent.StartTime.ToUniversalTime()-[DateTime]::Parse($macroLaunch.started_utc).ToUniversalTime()).TotalSeconds) -lt 10) {
                $macroReady = $false
            }
        }
        if ($macroReady) { break }
        Start-Sleep -Seconds 10
    }
    & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/v2-command.sh experiments.macro_transfer_v1.analyze *> (Join-Path $macroOperator 'final-analysis.log')
    if ($LASTEXITCODE -ne 0) { throw 'Analysis failed; evidence retained.' }
    if (!$macroComplete) { throw 'A backend stopped: partial report saved; no complete archive claimed.' }
    & wsl.exe -d Ubuntu-24.04 -u martin --exec bash /mnt/c/Proj/robotics/introtorobotics/reports/macro-transfer-v1-postprocess.sh *> (Join-Path $macroOperator 'final-evidence-audit.log')
    if ($LASTEXITCODE -ne 0) { throw 'Evidence finalization failed; raw data and report retained.' }
    @{status='COMPLETE';at_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $macroStatus -Encoding UTF8
} catch {
    @{status='STOPPED';at_utc=[DateTime]::UtcNow.ToString('o');error=$_.Exception.Message} | ConvertTo-Json | Set-Content -LiteralPath $macroStatus -Encoding UTF8
}
