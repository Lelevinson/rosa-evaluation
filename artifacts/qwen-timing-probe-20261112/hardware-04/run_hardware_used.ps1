param([ValidatePattern('^hardware-[0-9]{2}$')][string]$Attempt = 'hardware-02', [switch]$Corrected)
$ErrorActionPreference = 'Stop'
$probeDir = $PSScriptRoot
$workspaceDir = (Resolve-Path (Join-Path $probeDir '..\..\..')).Path
$runDir = Join-Path $probeDir $Attempt
if ($Corrected) {
    $authorization = Get-Content -LiteralPath (Join-Path $probeDir 'corrected-check-authorization.json') -Raw | ConvertFrom-Json
    if ($authorization.status -ne 'APPROVED_BY_USER' -or $authorization.attempt -ne $Attempt -or
        $authorization.max_additional_inference_requests -ne 1 -or $authorization.stage1_authorized) {
        throw 'Explicit one-request correction authorization absent or wrong scope'
    }
    if (Test-Path -LiteralPath (Join-Path $probeDir 'corrected-hardware-dispatch-reservation.json')) { throw 'Additional corrected request already reserved; refusing replay' }
} elseif (Test-Path -LiteralPath (Join-Path $probeDir 'hardware-dispatch-reservation.json')) {
    throw 'Original one-request allowance already reserved; refusing replay'
}
if (Test-Path -LiteralPath $runDir) { throw 'Hardware attempt directory already exists; refusing automatic replay' }
New-Item -ItemType Directory -Path $runDir | Out-Null
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $runDir 'run_hardware_used.ps1')
$serverProcess = $null
$clientProcess = $null
$probeWatch = [Diagnostics.Stopwatch]::StartNew()
$outcome = @{ status='PREPARING'; inference_requests_reserved=0; tools_dispatched=0 }
function Save-ProbeJson($Name, $Value) {
    $encoded = $Value | ConvertTo-Json -Depth 30
    [IO.File]::WriteAllText((Join-Path $runDir $Name), $encoded, [Text.UTF8Encoding]::new($false))
}
try {
    $editors = @(Get-Process -Name Unity,'gz*','ollama*' -ErrorAction SilentlyContinue)
    if ($editors.Count) { throw 'Competing editor/simulator/Ollama process present' }
    $beforeGpu = (& nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu --format=csv | Out-String)
    $beforeApps = (& nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader | Out-String)
    Save-ProbeJson 'gpu-before.json' @{ gpu=$beforeGpu; processes=$beforeApps; captured_at=(Get-Date).ToString('o') }
    $gatewayText = (& wsl.exe --distribution Ubuntu-24.04 --user martin --exec /usr/sbin/ip -4 route show default | Out-String)
    if ($gatewayText -notmatch 'default via ([0-9.]+)') { throw 'No WSL gateway' }
    $probeAddress = $Matches[1]
    $port = 11436
    $endpoint = "http://${probeAddress}:$port"
    try {
        $existing = Invoke-RestMethod "$endpoint/api/version" -TimeoutSec 2
        throw 'Probe port already serving; refusing to reuse or stop an unowned service'
    } catch {
        if ($_.Exception.Message -like 'Probe port already*') { throw }
    }
    $binary = Join-Path $workspaceDir '.local\ollama-0.40.6\ollama.exe'
    if (!(Test-Path -LiteralPath $binary)) { throw 'Pinned binary absent' }
    # Process-local settings only; restore the caller's values immediately.
    $settings = @{
        OLLAMA_HOST="${probeAddress}:$port"; OLLAMA_MODELS=(Join-Path $env:USERPROFILE '.ollama\models');
        OLLAMA_NO_CLOUD='1'; OLLAMA_NOPRUNE='1'; OLLAMA_NUM_PARALLEL='1'; OLLAMA_MAX_LOADED_MODELS='1';
        OLLAMA_CONTEXT_LENGTH='4096'; OLLAMA_FLASH_ATTENTION=$null; OLLAMA_KV_CACHE_TYPE=$null;
        OLLAMA_KEEP_ALIVE='2m'; HTTP_PROXY=''; HTTPS_PROXY=''; ALL_PROXY='';
        OLLAMA_DEBUG_LOG_REQUESTS='false'
    }
    $previous = @{}
    try {
        foreach ($key in $settings.Keys) {
            $previous[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
            [Environment]::SetEnvironmentVariable($key, $settings[$key], 'Process')
        }
        $serverProcess = Start-Process -FilePath $binary -ArgumentList 'serve' -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput (Join-Path $runDir 'server-stdout.log') `
            -RedirectStandardError (Join-Path $runDir 'server-stderr.log')
    } finally {
        foreach ($key in $previous.Keys) { [Environment]::SetEnvironmentVariable($key, $previous[$key], 'Process') }
    }
    Save-ProbeJson 'server-process.json' @{ process_id=$serverProcess.Id; executable=$binary; endpoint=$endpoint; settings=$settings }
    $version = $null
    for ($startupPoll=0; $startupPoll -lt 40; $startupPoll++) {
        if ($serverProcess.HasExited) { throw 'Pinned server exited during startup' }
        try { $version = Invoke-RestMethod "$endpoint/api/version" -TimeoutSec 2; break } catch { Start-Sleep -Milliseconds 250 }
    }
    if (!$version -or $version.version -ne '0.40.6') { throw 'Pinned server version check failed' }
    $tags = Invoke-RestMethod "$endpoint/api/tags" -TimeoutSec 10
    $models = @($tags.models | Where-Object name -eq 'qwen3.5:9b')
    if ($models.Count -ne 1 -or $models[0].digest -ne '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90') {
        throw 'Pinned digest mismatch; no download or inference'
    }
    Save-ProbeJson 'verified-server-model.json' @{ version=$version; model=$models[0] }
    $show = Invoke-RestMethod "$endpoint/api/show" -Method Post -ContentType 'application/json' `
        -Body '{"model":"qwen3.5:9b"}' -TimeoutSec 15
    Save-ProbeJson 'model-show.json' $show
    $linuxScript = '/mnt/c/Proj/robotics/introtorobotics/rosa-evaluation/artifacts/qwen-timing-probe-20261112/hardware_call.py'
    $arguments = @('--distribution','Ubuntu-24.04','--user','martin','--exec',
        '/home/martin/.local/share/rosa-envs/research/bin/python','-B',$linuxScript,$endpoint,$Attempt)
    if ($Corrected) { $arguments += 'corrected' }
    $clientProcess = Start-Process -FilePath 'wsl.exe' -ArgumentList $arguments -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $runDir 'client-stdout.log') `
        -RedirectStandardError (Join-Path $runDir 'client-stderr.log')
    while (!$clientProcess.WaitForExit(1000)) {
        if ($probeWatch.Elapsed.TotalSeconds -gt 420) { throw 'External hardware-check deadline exceeded' }
        if (Get-Process -Name Unity,'gz*' -ErrorAction SilentlyContinue) { throw 'GPU workload appeared during request; stop without retry' }
    }
    Save-ProbeJson 'client-exit.json' @{ exit_code=$clientProcess.ExitCode }
    $resultPath = Join-Path $runDir 'result.json'
    if (!(Test-Path -LiteralPath $resultPath)) { throw 'Hardware client produced no result; no automatic retry' }
    $clientResult = Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
    if ($clientResult.status -ne 'RETURNED') { throw 'Hardware client failed; no automatic retry' }
    $loaded = Invoke-RestMethod "$endpoint/api/ps" -TimeoutSec 10
    Save-ProbeJson 'loaded-model.json' $loaded
    $afterGpu = (& nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu --format=csv | Out-String)
    $afterApps = (& nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader | Out-String)
    Save-ProbeJson 'gpu-loaded.json' @{ gpu=$afterGpu; processes=$afterApps; captured_at=(Get-Date).ToString('o') }
    $savedHost = [Environment]::GetEnvironmentVariable('OLLAMA_HOST','Process')
    try {
        [Environment]::SetEnvironmentVariable('OLLAMA_HOST',"${probeAddress}:$port",'Process')
        $processor = (& $binary ps | Out-String)
        [IO.File]::WriteAllText((Join-Path $runDir 'ollama-ps.txt'),$processor,[Text.UTF8Encoding]::new($false))
    } finally { [Environment]::SetEnvironmentVariable('OLLAMA_HOST',$savedHost,'Process') }
    $runtimeLog = Get-Content -LiteralPath (Join-Path $runDir 'server-stderr.log') -Raw
    if ($runtimeLog -match 'Flash Attention enabled' -and $runtimeLog -match '--flash-attn auto') {
        $outcome.status = 'COMPLETE'
        $outcome.effective_flash_attention_verified=$true
    } else {
        $outcome.status = 'RETURNED_CONFIGURATION_MISMATCH'
        $outcome.effective_flash_attention_verified=$false
    }
} catch {
    $outcome.status = 'STOPPED_NO_AUTOMATIC_RETRY'
    $outcome.error = $_.Exception.Message
} finally {
    if (Test-Path -LiteralPath (Join-Path $runDir 'dispatch-reservation.json')) { $outcome.inference_requests_reserved=1 }
    if ($clientProcess -and !$clientProcess.HasExited) { Stop-Process -Id $clientProcess.Id -ErrorAction SilentlyContinue }
    if ($serverProcess -and !$serverProcess.HasExited) {
        # Bound to an owned server only. Empty chat+keep_alive=0 is unload, no generation.
        try { Invoke-RestMethod "$endpoint/api/chat" -Method Post -ContentType 'application/json' `
            -Body '{"model":"qwen3.5:9b","messages":[],"keep_alive":0,"stream":false}' -TimeoutSec 10 | Out-Null } catch {}
        # Stop only this owned process tree (server and its child runner).
        # Unload can make a child exit before taskkill enumerates it. Record the
        # native exit without allowing its stderr to erase the attempt status.
        $priorErrorAction = $ErrorActionPreference
        try {
            $ErrorActionPreference = 'Continue'
            $killOutput = (& taskkill.exe /PID $serverProcess.Id /T /F 2>&1 | Out-String)
            Save-ProbeJson 'cleanup-command.json' @{ exit_code=$LASTEXITCODE; output=$killOutput }
        } finally { $ErrorActionPreference = $priorErrorAction }
    }
    $outcome.elapsed_seconds=$probeWatch.Elapsed.TotalSeconds
    Save-ProbeJson 'attempt-status.json' $outcome
    Write-Output ($outcome | ConvertTo-Json -Compress)
}
