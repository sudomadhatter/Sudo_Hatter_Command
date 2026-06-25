<#
.SYNOPSIS
  Push the master .agents toolkit into a target's tool dirs (the lobby, or a project).

.DESCRIPTION
  Single source of authorship = <home>\.agents. This copies commands / skills / opencode-agents into
  the target's .claude and .opencode dirs so Claude /commands + skills resolve there. For a PROJECT
  target (not the lobby root) it ALSO vendors the whole .agents into the project so the repo is
  clone-safe and opencode.json / rule-by-path references resolve standalone.

  Additive copy (robocopy /E) — it does NOT delete target-local files (e.g. a project's own commands).
  Always edit the master; never hand-edit the copies. Re-run this to propagate changes.

.PARAMETER Target
  Directory to sync into. Default: the home-base root (lobby).
#>
param([string]$Target)

$ErrorActionPreference = "Stop"
$Master   = Split-Path $PSScriptRoot -Parent     # ...\.agents
$HomeRoot = Split-Path $Master -Parent           # ...\Sudo_Hatter_Command
if (-not $Target) { $Target = $HomeRoot }
$Target   = (Resolve-Path $Target).Path
$IsLobby  = ($Target.TrimEnd('\') -ieq $HomeRoot.TrimEnd('\'))

function Sync-Dir($src, $dst) {
  if (-not (Test-Path $src)) { return }
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
  robocopy $src $dst /E /XD node_modules /NFL /NDL /NJH /NJS /NC /NS | Out-Null
  if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($src -> $dst), rc=$LASTEXITCODE" }
}

Write-Host "sync-agents: master=$Master"
Write-Host "sync-agents: target=$Target (lobby=$IsLobby)"

# Project target → vendor the whole master so the repo is self-contained.
if (-not $IsLobby) { Sync-Dir $Master (Join-Path $Target ".agents") }

# Source of truth for this target's tool dirs: master for the lobby, vendored copy for a project.
$src = if ($IsLobby) { $Master } else { Join-Path $Target ".agents" }

Sync-Dir (Join-Path $src "commands")        (Join-Path $Target ".claude\commands")
Sync-Dir (Join-Path $src "skills")          (Join-Path $Target ".claude\skills")
Sync-Dir (Join-Path $src "commands")        (Join-Path $Target ".opencode\commands")
Sync-Dir (Join-Path $src "opencode-agents") (Join-Path $Target ".opencode\agent")

Write-Host "sync-agents: done. (Edit the master .agents/ — never the copies — and re-run to propagate.)"
exit 0
