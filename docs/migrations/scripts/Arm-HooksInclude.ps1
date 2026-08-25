# Arm-HooksInclude.ps1 - make core.hooksPath immune to Claude Code's worktree rewrite.
#
# Claude Code's worktree setup parses .git/config, resolves a RELATIVE core.hooksPath to an
# ABSOLUTE one, and writes it back with `git config` run inside the new worktree - which, for a
# linked worktree, writes the SHARED config. Every worktree then runs the MAIN checkout's hooks
# instead of its own. It only does this when it can SEE the key in .git/config.
#
# So the value stays local and relative, and moves into an INCLUDED file that git follows and a
# plain ini reader does not.
#
# Usage, from the lobby root:
#   powershell -File Arm-HooksInclude.ps1
#   powershell -File Arm-HooksInclude.ps1 -Repos '.','Projects\AGY_AVIATIONCHAT'
param(
    [string[]]$Repos
)

$ErrorActionPreference = 'Stop'

if (-not $Repos) {
    # every repo here that actually has a .githooks/ to point at
    $Repos = @('.')
    if (Test-Path 'Projects') {
        $Repos += (Get-ChildItem 'Projects' -Directory |
                   Where-Object { (Test-Path (Join-Path $_.FullName '.git')) -and
                                  (Test-Path (Join-Path $_.FullName '.githooks')) } |
                   ForEach-Object { $_.FullName })
    }
}

# ASCII only, and written without a BOM - Windows PowerShell 5.1's `Set-Content -Encoding utf8`
# emits a BOM, and a BOM at the head of an included git config file is not worth the gamble.
$body = @(
    '# Loaded by .git/config via include.path.',
    '#',
    '# core.hooksPath MUST stay RELATIVE so the main checkout and every worktree each read',
    '# their OWN .githooks/. It lives HERE, not in .git/config, because Claude Code''s worktree',
    '# setup parses .git/config directly, resolves a relative hooksPath to an ABSOLUTE one and',
    '# writes it back to the SHARED config. It only does that when it can SEE the key.',
    '[core]',
    "`thooksPath = .githooks"
) -join "`n"

$failed = $false
foreach ($r in $Repos) {
    if (-not (Test-Path (Join-Path $r '.git')))      { Write-Host "SKIP  $r  (not a git repo)";          continue }
    if (-not (Test-Path (Join-Path $r '.githooks'))) { Write-Host "SKIP  $r  (no .githooks/ to point at)"; continue }

    # a submodule's .git is a FILE, and so is a worktree's - ask git where the real dir is
    $gitDir = (& git -C $r rev-parse --path-format=absolute --git-common-dir).Trim()
    $config = Join-Path $gitDir 'config'
    $conf   = Join-Path $gitDir 'hooks.conf'

    [System.IO.File]::WriteAllText($conf, $body + "`n", (New-Object System.Text.UTF8Encoding($false)))

    # this key IS the trigger - it must not remain in .git/config
    & git -C $r config --local --unset-all core.hooksPath 2>$null | Out-Null

    if (-not (Select-String -Path $config -Pattern 'hooks\.conf' -Quiet)) {
        Add-Content -Path $config -Value "[include]" -Encoding ascii
        Add-Content -Path $config -Value "`tpath = hooks.conf" -Encoding ascii
    }

    # verify by asking GIT, not by trusting the write
    $effective = (& git -C $r config --get core.hooksPath)
    if ($null -eq $effective) { $effective = '' }
    $effective = $effective.Trim()
    $visible   = Select-String -Path $config -Pattern 'hooksPath' -Quiet
    $ok        = ($effective -eq '.githooks') -and (-not $visible)
    if (-not $ok) { $failed = $true }
    Write-Host ("{0} {1}  effective={2}  visible-in-.git/config={3}" -f
                $(if ($ok) { 'OK   ' } else { 'FAIL ' }), $r, $(if ($effective) { $effective } else { '(unset)' }), [bool]$visible)
}

if ($failed) { exit 1 } else { exit 0 }
