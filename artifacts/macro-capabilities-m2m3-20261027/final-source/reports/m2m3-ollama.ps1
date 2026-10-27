$ErrorActionPreference = 'Stop'
$workspace = Split-Path $PSScriptRoot -Parent
$route = (& wsl.exe -d Ubuntu-24.04 --exec ip -4 route show default | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $route -notmatch 'default via ([0-9.]+)') { throw 'WSL gateway unavailable' }
$hostAddress = $Matches[1]
$adapter = Get-NetIPAddress -AddressFamily IPv4 -IPAddress $hostAddress -ErrorAction Stop
if ($adapter.InterfaceAlias -notmatch 'WSL') { throw 'Refusing non-WSL Ollama binding' }
$endpoint = "http://${hostAddress}:11434"
try { $version = Invoke-RestMethod "$endpoint/api/version" -TimeoutSec 2 } catch { $version = $null }
if (!$version) {
    $binary = Join-Path $workspace '.local/ollama-0.40.6/ollama.exe'
    if (!(Test-Path -LiteralPath $binary)) { throw 'Pinned Ollama executable unavailable; no replacement downloaded' }
    $state = Join-Path $workspace 'rosa-evaluation/.local/ollama'
    New-Item -ItemType Directory -Path $state -Force | Out-Null
    $saved = @{}
    $settings = @{ OLLAMA_HOST="${hostAddress}:11434"; OLLAMA_NO_CLOUD='1'; OLLAMA_CONTEXT_LENGTH='4096'; OLLAMA_NUM_PARALLEL='1'; OLLAMA_MAX_LOADED_MODELS='1' }
    try {
        foreach ($key in $settings.Keys) {
            $saved[$key] = [Environment]::GetEnvironmentVariable($key, 'Process')
            [Environment]::SetEnvironmentVariable($key, $settings[$key], 'Process')
        }
        $child = Start-Process -FilePath $binary -ArgumentList 'serve' -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $state 'm3-stdout.log') -RedirectStandardError (Join-Path $state 'm3-stderr.log')
    } finally {
        foreach ($key in $saved.Keys) { [Environment]::SetEnvironmentVariable($key, $saved[$key], 'Process') }
    }
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try { $version = Invoke-RestMethod "$endpoint/api/version" -TimeoutSec 2; break } catch { Start-Sleep -Milliseconds 500 }
    }
}
if (!$version -or $version.version -ne '0.40.6') { throw 'Pinned Ollama version not available' }
$tags = Invoke-RestMethod "$endpoint/api/tags" -TimeoutSec 10
$model = @($tags.models | Where-Object name -eq 'qwen3.5:9b')
if ($model.Count -ne 1 -or $model[0].digest -ne '56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90') { throw 'Pinned model digest mismatch' }
$result = @{ endpoint=$endpoint; version=$version.version; model=$model[0].name; digest=$model[0].digest; details=$model[0].details; live_model_requests=0 }
$result | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $workspace 'rosa-evaluation/artifacts/macro-capabilities-m2m3-20261027/ollama-preflight.json')
Write-Output "Pinned Ollama ready: $endpoint"
