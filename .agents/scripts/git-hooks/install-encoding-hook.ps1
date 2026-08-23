<#
.SYNOPSIS
  Install the pre-commit encoding gate into THIS repo's .git/hooks (machine-local).

.DESCRIPTION
  .git/ never travels through GitHub, so every machine installs hooks once per clone.
  Run from a repo root, or pass -Repo. -All installs into the lobby and every maintained
  project in one go.

  REFUSES to clobber. If .git/hooks/pre-commit already exists and is not ours, it stops and
  prints the existing file — chaining someone else's hook is their call, not this script's.

.PARAMETER Repo   Repo root to install into. Default: the current repo.
.PARAMETER All    Install into the lobby + every name in .agents/maintained-projects.txt.
.PARAMETER Uninstall  Remove the hook (only if it is ours).
#>
param(
  [string]$Repo,
  [switch]$All,
  [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'
$MARKER = 'pre-commit-encoding'

function Install-One([string]$root) {
  $gitPath = Join-Path $root '.git'
  if (-not (Test-Path $gitPath)) { Write-Host "  SKIP $root (not a git repo)"; return }

  # core.hooksPath OVERRIDES .git/hooks entirely. Three of the four repos here set it to
  # .githooks, so an installer that assumes .git/hooks writes a file git never reads —
  # it reports success and installs nothing. A gate that silently does not run is worse
  # than no gate, so this is resolved, not assumed.
  $hooksPath = (git -C $root config --get core.hooksPath 2>$null)
  if ($hooksPath) {
    $hookDir = if ([System.IO.Path]::IsPathRooted($hooksPath)) { $hooksPath }
               else { Join-Path $root $hooksPath }
    Write-Host "  ($root -> core.hooksPath = $hooksPath)"
  } else {
    # A worktree's .git is a FILE pointing at the real gitdir.
    if (Test-Path $gitPath -PathType Leaf) {
      $line = (Get-Content $gitPath -TotalCount 1)
      $gitPath = $line -replace '^gitdir:\s*', ''
    }
    $hookDir = Join-Path $gitPath 'hooks'
  }
  if (-not (Test-Path $hookDir)) { New-Item -ItemType Directory -Path $hookDir -Force | Out-Null }
  $hook = Join-Path $hookDir 'pre-commit'

  if ($Uninstall) {
    if ((Test-Path $hook) -and ((Get-Content $hook -Raw) -match $MARKER)) {
      Remove-Item $hook -Force -Confirm:$false
      Write-Host "  removed  $hook"
    } else {
      Write-Host "  SKIP $root (no hook of ours)"
    }
    return
  }

  $body = @"
#!/bin/sh
# $MARKER (installed by .agents/scripts/git-hooks/install-encoding-hook.ps1)
exec "`$(git rev-parse --show-toplevel)/.agents/scripts/git-hooks/pre-commit-encoding.sh" "`$@"
"@
  $bodyLf = ($body -replace "`r`n", "`n")

  # ⛔ AUDIT FINDING F2 (SCC-290). THE MARKER TEST ALONE IS NOT AN OWNERSHIP TEST, and reading it
  # as one silently DISARMS a gate. `.githooks/pre-commit` is a tracked DISPATCHER that chains two
  # delegates — the maps refresh and this encoding gate — and it necessarily contains the string
  # `pre-commit-encoding`. So `-match $MARKER` was true, the installer called the file its own, and
  # overwrote it with the three-line body below: the maps delegate gone, `git status` showing a
  # modified `.githooks/pre-commit` the operator reads as "the installer touched its own file", and
  # the maps silently stale on that machine until a push is refused.
  #
  # So ownership is now byte equality, and the three outcomes are distinct:
  #   no marker         -> a FOREIGN hook. Refuse, print it, tell them to chain by hand.
  #   marker, different -> OURS BUT EXTENDED (the dispatcher). Refuse — same message, because the
  #                        answer is the same: chain it, do not clobber it.
  #   marker, identical -> ours and unchanged. Rewriting is a no-op; keep the existing behaviour.
  if (Test-Path $hook) {
    $existing = Get-Content $hook -Raw
    $existingLf = ($existing -replace "`r`n", "`n")
    # Three states, and the message must not conflate them: not ours · ours but DIFFERENT (chained
# by someone, or written by an older installer) · ours and byte-identical. Only the last is
# rewritten. Saying "it chains more than the encoding gate" about a merely stale own-hook sends
# the operator to look for a chain that is not there.
if (($existing -notmatch $MARKER) -or ($existingLf.TrimEnd() -ne $bodyLf.TrimEnd())) {
      $why = if ($existing -notmatch $MARKER) { "a different pre-commit hook is already installed" }
             else { "the pre-commit hook here is OURS but DIFFERENT - either it chains more than the encoding gate, or it was written by an older installer. Overwriting blind could drop a chain, so read the head below and decide" }
      Write-Host "  REFUSED $root - ${why}:"
      Write-Host ($existing -split "`n" | Select-Object -First 5 | ForEach-Object { "      $_" })
      Write-Host "      chain it by hand if you want both."
      return
    }
  }
  # LF only: git runs this through sh, and CRLF here is a "bad interpreter" error.
  [System.IO.File]::WriteAllText($hook, $bodyLf, `
    (New-Object System.Text.UTF8Encoding $false))
  Write-Host "  installed $hook"
}

if ($All) {
  $lobby = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent   # .agents/scripts/git-hooks -> lobby
  $lobby = Split-Path $lobby -Parent
  Write-Host "install-encoding-hook: lobby + maintained projects"
  Install-One $lobby
  $list = Join-Path $lobby '.agents\maintained-projects.txt'
  if (Test-Path $list) {
    Get-Content $list | Where-Object { $_ -match '\S' -and $_ -notmatch '^\s*#' } | ForEach-Object {
      Install-One (Join-Path $lobby "Projects\$($_.Trim())")
    }
  }
} else {
  if (-not $Repo) { $Repo = (git rev-parse --show-toplevel 2>$null) }
  if (-not $Repo) { throw "not in a git repo - pass -Repo <path> or use -All" }
  Install-One $Repo
}

Write-Host "done. Test it:  python .agents/scripts/workflow_lint.py --staged"
