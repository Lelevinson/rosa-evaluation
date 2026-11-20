param([string]$OutputFile, [switch]$DuringRequest, [int]$OwnedServerId=0)
$ErrorActionPreference='Stop'
$failures=@()
$processes=@(Get-Process -Name Unity,'gz*','ollama*','llama-server*' -ErrorAction SilentlyContinue | Select-Object ProcessName,Id)
foreach ($item in $processes) {
    if ($item.ProcessName -eq 'Unity' -or $item.ProcessName -like 'gz*') { $failures+='editor_or_simulator' }
    if ($OwnedServerId -eq 0 -and ($item.ProcessName -like '*ollama*' -or $item.ProcessName -like 'llama-server*')) { $failures+='unowned_model_worker' }
    if ($item.ProcessName -eq 'ollama' -and $OwnedServerId -ne 0 -and $item.Id -ne $OwnedServerId) { $failures+='unowned_model_server' }
}
$engineRows=@()
$counterRows=(Get-Counter '\GPU Engine(*)\Utilization Percentage' -SampleInterval 1 -MaxSamples 2).CounterSamples
foreach ($counter in $counterRows) {
    if ($counter.CookedValue -le 2) { continue }
    $taskPid=$null
    if ($counter.Path -match 'pid_(\d+)') { $taskPid=[int]$Matches[1] }
    $taskProcess=Get-Process -Id $taskPid -ErrorAction SilentlyContinue
    $engineKind=($counter.Path -replace '^.*engtype_','')
    $engineRows += @{name=$taskProcess.ProcessName;pid=$taskPid;percent=$counter.CookedValue;engine=$engineKind}
    $displayNames=@('dwm','Code','System','explorer','RuntimeBroker','ShellExperienceHost','SearchHost','TextInputHost')
    $browserUi=($taskProcess.ProcessName -eq 'chrome' -and $engineKind -like '3d*' -and $counter.CookedValue -le 5)
    $ownModel=($OwnedServerId -ne 0 -and $taskProcess.ProcessName -in @('ollama','llama-server'))
    if (!$ownModel -and ($engineKind -like '*videodecode*' -or ($taskProcess.ProcessName -notin $displayNames -and !$browserUi))) {
        $failures+='external_gpu_activity'
    }
}
$gpuRows=@()
$sampleCount=1
if (!$DuringRequest) { $sampleCount=3 }
for ($sample=0; $sample -lt $sampleCount; $sample++) {
    $raw=(& nvidia-smi --query-gpu=memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu,clocks.current.sm,power.draw --format=csv,noheader,nounits | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) { throw 'nvidia-smi query failed' }
    $parts=$raw -split ','
    $gpuRows+=@{reading=$raw;time=(Get-Date).ToString('o')}
    if (!$DuringRequest -and [double]$parts[3].Trim() -gt 10) { $failures+='gpu_not_quiet' }
    if ($sample -lt $sampleCount-1) { Start-Sleep -Milliseconds 500 }
}
$record=@{pass=($failures.Count -eq 0);failures=@($failures | Select-Object -Unique);during_request=[bool]$DuringRequest;engines=$engineRows;gpu=$gpuRows;processes=$processes;time=(Get-Date).ToString('o')}
[IO.File]::WriteAllText($OutputFile,($record | ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))
if ($failures.Count) { exit 2 }
