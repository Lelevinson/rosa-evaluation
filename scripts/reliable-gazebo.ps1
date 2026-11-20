param(
    [ValidateSet('deterministic', 'ollama', 'siwc')][string]$Backend = 'deterministic',
    [ValidateSet('A', 'B', 'C', 'D')][string]$Configuration = 'A',
    [ValidateRange(-0.6, 0.6)][double]$Target = 0.2,
    [string]$Distro = 'Ubuntu-24.04'
)
$ErrorActionPreference = 'Stop'
$reliabilityEvaluation = Split-Path $PSScriptRoot -Parent
$reliabilityWorkspace = Split-Path $reliabilityEvaluation -Parent
if ($Backend -eq 'ollama') {
    & (Join-Path $reliabilityWorkspace 'rosa-research\scripts\start-research.ps1') -Distro $Distro
}
$reliabilityLinuxPath = (& wsl.exe -d $Distro --exec wslpath -u $reliabilityEvaluation.Replace('\', '/') | Out-String).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Could not resolve the evaluation checkout in WSL.' }
& wsl.exe -d $Distro --cd $reliabilityLinuxPath --exec bash scripts/phoenix-service.sh start
if ($LASTEXITCODE -ne 0) { throw 'Phoenix startup failed.' }
$reliabilityTargetText = $Target.ToString([System.Globalization.CultureInfo]::InvariantCulture)
& wsl.exe -d $Distro --cd $reliabilityLinuxPath --exec bash scripts/reliable-gazebo.sh --backend $Backend --configuration $Configuration --target $reliabilityTargetText
if ($LASTEXITCODE -ne 0) { throw 'The Gazebo demonstration did not complete; inspect its saved evidence.' }
