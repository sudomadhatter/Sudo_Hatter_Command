#requires -Version 5
<#
  check-repo-map-drift.ps1 - detect-only repo-map drift nag (workspace-standard Part 3).
  MASTER copy in .agents/scripts/ ; vendored to each project as scripts/check-repo-map-drift.ps1
  (and wired into .claude/settings.json as a SessionStart hook). Edit the master; re-sync.

  Lists the project's real top-level folders, skips the ignore set (built-in defaults + the
  -IgnoreExtra names, which MUST match the generator's --ignore), and flags any folder on disk but
  NOT named in docs/repo-map.md. It NAGS only; it never edits anything and always exits 0 (a drift
  nag must not block a session). It cannot write the one-line purpose a curated header needs - that
  stays a human/agent job at end-of-task. Rebuild the map with:
      python scripts/generate_repo_map.py --ignore <same extras>

  ASCII-only on purpose: PowerShell 5.1 reads a BOM-less file as Windows-1252, so non-ASCII here
  would corrupt the parse.
#>
param(
    [string]$IgnoreExtra = '',              # comma-separated EXTRA folder names to skip (match the map's --ignore)
    [string]$Root = '',                     # override the auto-detected root (default: parent of scripts/)
    [string]$MapPath = 'docs/repo-map.md'   # repo-map path relative to root (lobby and project both use docs/)
)

$ErrorActionPreference = 'SilentlyContinue'

# Projects vendor this at <project>/scripts/ and auto-detect root; the home base calls the master copy
# in .agents/scripts/ directly and passes -Root/-MapPath (its map lives at docs/repo-map.md, same as a project).
if ($Root) { $root = $Root } else { $root = Split-Path -Parent $PSScriptRoot }   # <project>/scripts -> <project>
$map  = Join-Path $root $MapPath

if (-not (Test-Path $map)) {
    Write-Output '[repo-map] docs/repo-map.md not found - run: python scripts/generate_repo_map.py'
    exit 0
}

# Built-in skips mirror generate_repo_map.py DEFAULT_IGNORES (dot-folders are skipped automatically).
# NOTE: named $skip, NOT $ignore - PowerShell variable names are case-insensitive, so $ignore would
# collide with the $IgnoreExtra-style param and silently break the filter.
$skip = @(
    'node_modules','venv','env','__pycache__','auth_keys',
    '_artifacts','_claude_artifacts','_opencode_artifacts',
    '_test_scripts','_debug_audio','dist','build','__tests__',
    '_bmad','_my_resources'
)
foreach ($x in ($IgnoreExtra -split ',')) { $x = $x.Trim(); if ($x) { $skip += $x } }

$mapText = Get-Content -Raw -Encoding UTF8 $map
$dirs = Get-ChildItem -LiteralPath $root -Directory |
    Where-Object { $_.Name -notlike '.*' -and $skip -notcontains $_.Name }

$missing = @()
foreach ($d in $dirs) {
    if ($mapText -notmatch [regex]::Escape($d.Name + '/')) { $missing += $d.Name }
}

if ($missing.Count -gt 0) {
    Write-Output ''
    Write-Output '[repo-map drift] top-level folders on disk but NOT in docs/repo-map.md:'
    foreach ($m in $missing) { Write-Output ('  - ' + $m + '/') }
    Write-Output '  -> rebuild: python scripts/generate_repo_map.py   (then add a one-line purpose to the curated header)'
}

exit 0
