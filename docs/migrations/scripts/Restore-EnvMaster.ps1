# Restore-EnvMaster.ps1 — split docs\migrations\auth_keys\_secrets\master.env back
# into the individual .env / credential files it was exported from, at their
# original relative paths.
#
# Run from the lobby root of the NEW machine after cloning the repos:
#   powershell -File docs\migrations\scripts\Restore-EnvMaster.ps1
# or point at a master file sitting anywhere (e.g. straight off the USB stick):
#   powershell -File docs\migrations\scripts\Restore-EnvMaster.ps1 -MasterPath D:\master.env
#
# Behavior:
#   - Creates missing directories (e.g. auth_keys/) as needed.
#   - If a target file already exists with DIFFERENT content, the old copy is
#     saved next to it as <name>.pre-restore.bak before overwriting.
#   - Writes UTF-8 without BOM (safe for python-dotenv, Next.js, docker, etc.).
#   - Refuses absolute paths or paths containing ".." inside the master file.

param(
    # $Root must be the LOBBY ROOT — manifest paths are relative to it. This script
    # lives three levels down (docs/migrations/scripts/), so walk up three times.
    [string]$Root = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent),
    [string]$MasterPath = ''
)

$ErrorActionPreference = 'Stop'
if (-not $MasterPath) { $MasterPath = Join-Path $Root 'docs\migrations\auth_keys\_secrets\master.env' }
if (-not (Test-Path $MasterPath)) { throw "Master file not found: $MasterPath" }

$lines = [System.IO.File]::ReadAllLines($MasterPath)
$utf8 = New-Object System.Text.UTF8Encoding $false
$current = $null
$buffer = New-Object System.Collections.Generic.List[string]
$written = 0

function Write-Target([string]$relPath, [string[]]$contentLines) {
    if ([System.IO.Path]::IsPathRooted($relPath) -or $relPath -match '\.\.') {
        throw "Unsafe path in master file: $relPath"
    }
    $dest = Join-Path $Root ($relPath.Replace('/', '\'))
    $destDir = Split-Path $dest -Parent
    if ($destDir -and -not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
    }
    $newContent = ($contentLines -join "`n") + "`n"
    if (Test-Path $dest) {
        $old = [System.IO.File]::ReadAllText($dest)
        if ($old -eq $newContent) { Write-Host "  unchanged  $relPath"; return }
        Copy-Item $dest "$dest.pre-restore.bak" -Force
        Write-Host "  backed up  $relPath -> $relPath.pre-restore.bak"
    }
    [System.IO.File]::WriteAllText($dest, $newContent, $utf8)
    Write-Host "  restored   $relPath"
    $script:written++
}

foreach ($line in $lines) {
    if ($line -match '^# >>> FILE: (.+)$') {
        if ($null -ne $current) { throw "Marker mismatch: new FILE started before END of $current" }
        $current = $Matches[1].Trim()
        $buffer.Clear()
    }
    elseif ($line -match '^# <<< END FILE:') {
        if ($null -eq $current) { throw 'Marker mismatch: END without a matching FILE marker' }
        Write-Target $current $buffer.ToArray()
        $current = $null
    }
    elseif ($null -ne $current) {
        [void]$buffer.Add($line)
    }
}
if ($null -ne $current) { throw "Master file ended mid-block: $current never closed" }

Write-Host ''
# NOTE: keep this string pure ASCII. This file is UTF-8 WITHOUT a BOM, and Windows
# PowerShell 5.1 parses a no-BOM script as the ANSI codepage — so a non-ASCII char
# here prints mangled at runtime (a section sign came out as "A§"). Verified 2026-08-03.
Write-Host "Done. $written file(s) written/updated. Now run the verification checklist in docs/migrations/install_guides/new_machine-migration-guide.md (section 4)."
