# Starts the weekend parity Ollama server (D16). Side by side with the M4 install:
# same pinned 0.40.6 binary (read-only use), own model dir, own state dir, own port 11440.
# Bound to the WSL virtual adapter only.
$ErrorActionPreference = 'Stop'
$root = 'C:\Proj\robotics\introtorobotics\.local'
$exe = Join-Path $root 'ollama-0.40.6\ollama.exe'
$state = Join-Path $root 'parity-ollama-state'
$models = Join-Path $root 'parity-ollama-models'
$route = (& wsl.exe -d Ubuntu-24.04 --exec ip -4 route show default | Out-String).Trim()
if ($route -notmatch 'default via ([0-9.]+)') { throw 'No WSL gateway' }
$hostAddress = $Matches[1]
$adapter = Get-NetIPAddress -AddressFamily IPv4 -IPAddress $hostAddress
if ($adapter.InterfaceAlias -notmatch 'WSL') { throw 'Not the WSL adapter' }
$base = "http://${hostAddress}:11440"
try { $v = Invoke-RestMethod "$base/api/version" -TimeoutSec 2 } catch { $v = $null }
if ($v) { Write-Host "already running $($v.version) $base"; exit 0 }
$vars = @{ OLLAMA_HOST = "${hostAddress}:11440"; OLLAMA_MODELS = $models; OLLAMA_NO_CLOUD = '1';
           OLLAMA_NUM_PARALLEL = '1'; OLLAMA_MAX_LOADED_MODELS = '1'; OLLAMA_NOPRUNE = '1';
           OLLAMA_CONTEXT_LENGTH = '8192'; OLLAMA_DEBUG = '1' }
foreach ($k in $vars.Keys) { [Environment]::SetEnvironmentVariable($k, $vars[$k], 'Process') }
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$p = Start-Process -FilePath $exe -ArgumentList 'serve' -WindowStyle Hidden -PassThru `
     -RedirectStandardOutput (Join-Path $state "stdout-$stamp.log") -RedirectStandardError (Join-Path $state "stderr-$stamp.log")
@{ pid = $p.Id; endpoint = $base; executable = $exe; models = $models; env = $vars; started = (Get-Date).ToString('o');
   stderr = "stderr-$stamp.log" } | ConvertTo-Json | Set-Content (Join-Path $state 'process.json')
for ($i = 0; $i -lt 40; $i++) { try { $v = Invoke-RestMethod "$base/api/version" -TimeoutSec 2; break } catch { Start-Sleep -Milliseconds 500 } }
if (!$v) { throw "did not start; see $state" }
Write-Host "Ollama $($v.version) $base pid $($p.Id)"
