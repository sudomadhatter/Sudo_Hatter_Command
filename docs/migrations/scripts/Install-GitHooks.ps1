# Install-GitHooks.ps1 — Arm and verify Git hooks across all repositories (SCC-115).
#
# Configures core.hooksPath .githooks for the lobby and all project repos.
#
# Run from the lobby root:
#   powershell -File docs\migrations\scripts\Install-GitHooks.ps1
# or verify only:
#   powershell -File docs\migrations\scripts\Install-GitHooks.ps1 -VerifyOnly

param(
    [string]$Root = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent),
    [string]$Repo = '',
    [switch]$VerifyOnly,
    [switch]$Json,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

# Locate python binary
$py = Get-Command python, py, python3 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $py) {
    Write-Error "Python 3 is required to run install_git_hooks.py but was not found on PATH."
    exit 1
}

$scriptPath = Join-Path $PSScriptRoot "install_git_hooks.py"
if (-not (Test-Path $scriptPath)) {
    Write-Error "Installer script not found: $scriptPath"
    exit 1
}

$argsList = @($scriptPath, "--root", $Root)
if ($Repo) { $argsList += @("--repo", $Repo) }
if ($VerifyOnly) { $argsList += "--verify-only" }
if ($Json) { $argsList += "--json" }
if ($Quiet) { $argsList += "--quiet" }

& $py.Source $argsList
exit $LASTEXITCODE
