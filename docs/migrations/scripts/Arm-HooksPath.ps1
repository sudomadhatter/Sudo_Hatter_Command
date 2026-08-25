<#
.SYNOPSIS
    Immunise core.hooksPath against the worktree rewrite (SCC-323). Windows twin of arm_hooks_path.py.

.DESCRIPTION
    Claude Code's worktree setup parses the main repo's .git/config with a plain ini reader,
    resolves a RELATIVE core.hooksPath to an ABSOLUTE one, and runs `git config core.hooksPath
    <abs>` with cwd set to the new worktree. `git config` in a linked worktree writes the SHARED
    config, so every worktree - and the main checkout - ends up running the MAIN checkout's hooks
    instead of its own. A lane's gates are then not the gates being enforced on it.

    The remedy keeps the value LOCAL and RELATIVE, but moves it out of .git/config into an
    included file:

        .git/config      gains  [include] path = hooks.conf   (no hooksPath key remains here)
        .git/hooks.conf  holds  [core] hooksPath = .githooks

    git follows include.path; the plain ini reader in the worktree setup does not, so it reads no
    key and never fires.

    Idempotent: running it twice changes nothing the second time. Repos with no .githooks/ are
    skipped. A submodule's or worktree's real git dir is resolved via `rev-parse --git-common-dir`,
    never by assuming `.git` is a directory.

.EXAMPLE
    powershell -File docs/migrations/scripts/Arm-HooksPath.ps1
.EXAMPLE
    powershell -File docs/migrations/scripts/Arm-HooksPath.ps1 -VerifyOnly
.EXAMPLE
    powershell -File docs/migrations/scripts/Arm-HooksPath.ps1 -Repo Projects/AGY_AVIATIONCHAT
#>
[CmdletBinding()]
param(
    [string]   $Root,
    [string[]] $Repo = @(),
    [switch]   $VerifyOnly
)

$ErrorActionPreference = 'Stop'

$HooksDirName = '.githooks'
$ConfName     = 'hooks.conf'
# git writes tabs in section bodies; match it exactly so the idempotence check does not rewrite.
$ConfBody     = "[core]`n`thooksPath = .githooks`n"

if (-not $Root) {
    # docs/migrations/scripts/ -> 3 levels up
    $Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
}
$Root = (Resolve-Path $Root).Path

function Invoke-Git {
    param([string]$RepoPath, [string[]]$GitArgs)
    # -C keeps cwd out of it: nothing here may depend on where the shell happens to be.
    $out = & git -C $RepoPath @GitArgs 2>$null
    return [pscustomobject]@{
        Code   = $LASTEXITCODE
        Output = if ($null -eq $out) { '' } else { ($out -join "`n").Trim() }
    }
}

function Get-GitCommonDir {
    param([string]$RepoPath)
    $r = Invoke-Git $RepoPath @('rev-parse', '--git-common-dir')
    if ($r.Code -ne 0 -or -not $r.Output) { return $null }
    $p = $r.Output
    if ([System.IO.Path]::IsPathRooted($p)) { return (Resolve-Path $p).Path }
    return (Resolve-Path (Join-Path $RepoPath $p)).Path
}

function Get-DiscoveredRepos {
    param([string]$RootPath)
    $found = @($RootPath)
    $projects = Join-Path $RootPath 'Projects'
    if (Test-Path $projects -PathType Container) {
        Get-ChildItem $projects -Directory | Sort-Object Name | ForEach-Object {
            if (Test-Path (Join-Path $_.FullName '.git')) { $found += $_.FullName }
        }
    }
    return $found
}

function Get-LocalHooksPathLineCount {
    param([string]$ConfigPath)
    if (-not (Test-Path $ConfigPath -PathType Leaf)) { return 0 }
    # Match the config KEY, not the substring: a section header such as
    # [branch "chore/SCC-323-hookspath-immunisation"] contains the word and is not the key.
    $text  = [System.IO.File]::ReadAllText($ConfigPath)
    $lines = @($text -split "`r?`n" | Where-Object { $_ -match '(?i)^\s*hooksPath\s*=' })
    return $lines.Count
}

function Test-HasInclude {
    param([string]$RepoPath)
    $r = Invoke-Git $RepoPath @('config', '--local', '--get-all', 'include.path')
    if ($r.Code -ne 0) { return $false }
    foreach ($line in ($r.Output -split "`n")) {
        if ($line.Trim() -eq $ConfName) { return $true }
    }
    return $false
}

function Test-Armed {
    param([string]$RepoPath, [string]$ConfigPath)
    # Ask GIT what it resolves; read the config FILE for the key that must be gone.
    $r = Invoke-Git $RepoPath @('config', '--get', 'core.hooksPath')
    $residue = Get-LocalHooksPathLineCount $ConfigPath

    if ($r.Code -ne 0 -or $r.Output -ne $HooksDirName) {
        return @('FAILED', "git resolves core.hooksPath to '$($r.Output)' (want '$HooksDirName')")
    }
    if ($residue -ne 0) {
        return @('FAILED', "$residue hooksPath line(s) still in $ConfigPath")
    }
    return @('armed', "core.hooksPath=$($r.Output) - 0 lines in .git/config")
}

function Invoke-Arm {
    param([string]$RepoPath, [bool]$Check)

    if (-not (Test-Path (Join-Path $RepoPath $HooksDirName) -PathType Container)) {
        return @('skipped', "no $HooksDirName/")
    }

    $gitdir = Get-GitCommonDir $RepoPath
    if (-not $gitdir) { return @('FAILED', 'could not resolve --git-common-dir') }

    $config = Join-Path $gitdir 'config'
    $conf   = Join-Path $gitdir $ConfName

    if ($Check) { return (Test-Armed $RepoPath $config) }

    $changed = $false

    # 1. The included file carries the value. Write it FIRST so no window exists where the
    #    hooks are unarmed. LF endings and no BOM: git's parser wants a plain ini file.
    # Compare NORMALISED: an older run of the Python twin may have left CRLF here, and a bare
    # comparison would make the two twins rewrite each other's file on every run.
    $current = if (Test-Path $conf -PathType Leaf) {
        ([System.IO.File]::ReadAllText($conf)) -replace "`r`n", "`n"
    } else { $null }
    if ($current -ne $ConfBody) {
        [System.IO.File]::WriteAllText($conf, $ConfBody, (New-Object System.Text.UTF8Encoding $false))
        $changed = $true
    }

    # 2. .git/config includes it.
    if (-not (Test-HasInclude $RepoPath)) {
        $r = Invoke-Git $RepoPath @('config', '--local', '--add', 'include.path', $ConfName)
        if ($r.Code -ne 0) { return @('FAILED', "could not add include.path: $($r.Output)") }
        $changed = $true
    }

    # 3. Only NOW does the direct key leave .git/config. --local touches that file alone; the
    #    included file is untouched, so the value never disappears.
    if ((Get-LocalHooksPathLineCount $config) -gt 0) {
        $r = Invoke-Git $RepoPath @('config', '--local', '--unset-all', 'core.hooksPath')
        # 5 = key not present, which is the state we want anyway.
        if ($r.Code -ne 0 -and $r.Code -ne 5) {
            return @('FAILED', "could not unset core.hooksPath: $($r.Output)")
        }
        $changed = $true
    }

    $result = Test-Armed $RepoPath $config
    if ($result[0] -eq 'FAILED') { return $result }
    return @(($(if ($changed) { 'changed' } else { 'armed' })), $result[1])
}

# ---- main ----------------------------------------------------------------

if ($Repo.Count -gt 0) {
    $repos = $Repo | ForEach-Object {
        if ([System.IO.Path]::IsPathRooted($_)) { $_ } else { (Join-Path $Root $_) }
    }
} else {
    $repos = Get-DiscoveredRepos $Root
}

$mode = if ($VerifyOnly) { 'VERIFY-ONLY' } else { 'ARM' }
Write-Host "== Arm-HooksPath @ $Root =="
Write-Host "   mode: $mode - $($repos.Count) repo(s)`n"

$failures = 0
foreach ($r in $repos) {
    $res    = Invoke-Arm $r ([bool]$VerifyOnly)
    $status = $res[0]
    $detail = $res[1]
    if ($status -eq 'FAILED') { $failures++ }
    $name  = Split-Path $r -Leaf
    if ((Resolve-Path $r).Path -eq $Root) { $name = "$name (lobby)" }
    Write-Host ("[{0,-7}] {1}: {2}" -f $status.ToUpper(), $name, $detail)
}

Write-Host ''
if ($failures -gt 0) {
    Write-Host "-- $failures repo(s) FAILED --"
    exit 1
}
Write-Host '-- all repos armed --'
exit 0
