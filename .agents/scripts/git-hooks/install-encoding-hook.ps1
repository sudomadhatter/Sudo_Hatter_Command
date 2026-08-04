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

  if (Test-Path $hook) {
    $existing = Get-Content $hook -Raw
    if ($existing -notmatch $MARKER) {
      Write-Host "  REFUSED $root - a different pre-commit hook is already installed:"
      Write-Host ($existing -split "`n" | Select-Object -First 5 | ForEach-Object { "      $_" })
      Write-Host "      chain it by hand if you want both."
      return
    }
  }

  $body = @"
#!/bin/sh
# $MARKER (installed by .agents/scripts/git-hooks/install-encoding-hook.ps1)
exec "`$(git rev-parse --show-toplevel)/.agents/scripts/git-hooks/pre-commit-encoding.sh" "`$@"
"@
  # LF only: git runs this through sh, and CRLF here is a "bad interpreter" error.
  [System.IO.File]::WriteAllText($hook, ($body -replace "`r`n", "`n"), `
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
