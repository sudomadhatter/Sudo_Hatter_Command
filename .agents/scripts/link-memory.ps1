<#
.SYNOPSIS
  Make Claude Code's auto-memory store portable: junction it into the repo so it travels via git.

.DESCRIPTION
  Claude Code keeps auto-memory at  %USERPROFILE%\.claude\projects\<slug>\memory\  where <slug> is
  DERIVED FROM THE ABSOLUTE PATH of the workspace (':' '\' '/' '_' and '.' all become '-'). That makes
  the store fragile on three axes:

    1. MACHINE  - ~/.claude is not a repo and is not synced, so memory never leaves the box it was
                  written on.
    2. RENAME   - renaming the home base or a project changes the slug, silently orphaning everything
                  under the old one. (This already happened twice here: 13 files stranded under
                  c--AGY-Projects-aviationChat-AGY and 2 under
                  c--Sudo-Hatter-Command-Projects-aviationChat-AGY.)
    3. DRIVE CASE - 'c--...' and 'C--...' are DIFFERENT directories, so a session opened from a
                  differently-cased cwd starts with empty memory.

  The fix: the repo holds the canonical store at <root>\_artifacts\_memory\, and the slug directory
  becomes a JUNCTION pointing at it. Memory then commits and travels with every other tracked file, and
  a rename only needs the junction re-pointed - never a data rescue.

  macOS twin: link-memory.sh (symlink instead of junction). TWINS BY CONTRACT - if either changes,
  change both. Same rule the Restore-EnvMaster.ps1 / restore-env-master.sh pair lives under.

.PARAMETER Root
  Workspace root to link. Defaults to this script's repo (two levels up from .agents\scripts\).

.PARAMETER All
  Link the lobby AND every project in .agents\maintained-projects.txt (the single source of truth for
  which workspaces we keep in sync). Never hand-loops over Projects\*.

.PARAMETER Apply
  Actually write. WITHOUT THIS THE SCRIPT ONLY REPORTS - dry-run by default, same posture as
  rename-fix.ps1.

.PARAMETER Force
  Re-point a junction that already exists but targets somewhere other than canonical.

.EXAMPLE
  .\.agents\scripts\link-memory.ps1                 # dry run, this workspace
  .\.agents\scripts\link-memory.ps1 -All            # dry run, lobby + maintained projects
  .\.agents\scripts\link-memory.ps1 -All -Apply     # do it

.NOTES
  SAFETY. This script never deletes memory. If canonical already holds files AND the local slug dir
  holds its own, the local ones are moved ASIDE to memory.local-backup-<timestamp> and reported - never
  merged, never clobbered. That is the case when a second machine links to a store another machine
  already seeded, and the two sets disagree. A human resolves it; the script refuses to guess.
#>
[CmdletBinding()]
param(
  [string]$Root,
  [switch]$All,
  [switch]$Apply,
  [switch]$Force
)

$ErrorActionPreference = 'Stop'

# Repo root: this script lives at <root>\.agents\scripts\ (master + vendored alike).
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DefaultRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
if (-not $Root) { $Root = $DefaultRoot }
$Root = (Resolve-Path $Root).Path.TrimEnd('\')

$ProjectsStore = Join-Path $env:USERPROFILE '.claude\projects'

# --- the slug algorithm -------------------------------------------------------------------------
# Verified against every directory present under ~\.claude\projects on this machine: ':' '\' '/' '_'
# and '.' each become '-'. Nothing else is touched, and case is preserved exactly as the path supplies
# it.
#
# '.' IS IN THE SET, and leaving it out is not cosmetic - it silently retargets the whole script. Our
# home base lives under a DOTTED directory, '.gemini', so the true slug carries a DOUBLE dash there:
#
#     c:\Users\dlohn\.gemini\...  ->  c--Users-dlohn--gemini-...
#                     ^ '\' then '.'        ^^ both dashes
#
# A char class without '.' yields '-.gemini', which matches no existing directory. The script would
# then take itself down the "no local store" path, create a BRAND NEW empty slug dir, junction that,
# and leave every real memory stranded in the old one - the precise data-loss this tool exists to
# prevent, wearing a success message. Caught 2026-08-04 on the seeding run, 126 files at stake.
function Get-MemorySlug([string]$path) {
  return ($path.TrimEnd('\') -replace '[:\\/_.]', '-')
}

# Drive-letter case (axis 3) is NOT a fragmentation risk on Windows: NTFS is case-INSENSITIVE, so
# 'C--Foo' and 'c--Foo' resolve to one directory. Claude Code merely preserves whichever casing created
# it first, which is why the store shows a mix. Linking "both spellings" would therefore process the
# same directory twice and manufacture a false canonical-vs-local conflict on the second pass.
#
# So: compute ONE slug, then reuse any existing directory that matches case-insensitively rather than
# creating a second one. Correct on case-insensitive volumes (reuse) and case-sensitive ones (create).
#
# Resolve by ENUMERATION, never by Test-Path: Get-ChildItem reports each name as it is stored ON DISK,
# whereas Test-Path/Get-Item echo back whatever casing the caller supplied (NTFS happily resolves
# either). PowerShell's Resolve-Path uppercases the drive letter while the harness records the cwd's
# own casing - here lowercase - so the two spellings routinely disagree. Exact match wins first, so a
# genuinely case-sensitive volume still picks its exact directory; the case-insensitive pass is the
# reuse path. Reporting the on-disk spelling matters: an operator comparing this output against
# `ls ~/.claude/projects` must not see a name that looks like a second, freshly-created store.
function Resolve-SlugDir([string]$path) {
  $slug = Get-MemorySlug $path
  $all = @()
  if (Test-Path $ProjectsStore) {
    $all = @(Get-ChildItem $ProjectsStore -Directory -Force -ErrorAction SilentlyContinue)
  }
  $hit = $all | Where-Object { $_.Name -ceq $slug } | Select-Object -First 1
  if (-not $hit) { $hit = $all | Where-Object { $_.Name -ieq $slug } | Select-Object -First 1 }
  if ($hit) { return $hit.FullName }
  return (Join-Path $ProjectsStore $slug)
}

# Count MEMORIES only. README.md / .gitkeep are scaffolding committed so the empty store is visible in
# git; counting them would make a fresh canonical look "already populated" and send the first machine
# down the backup path instead of seeding. That would silently strand the very memories we are rescuing.
$MemoryScaffold = @('README.md', '.gitkeep')
function Get-MemoryFiles([string]$dir) {
  if (-not (Test-Path $dir)) { return @() }
  return @(Get-ChildItem $dir -File -Force -ErrorAction SilentlyContinue |
             Where-Object { $MemoryScaffold -notcontains $_.Name })
}

function Test-IsReparse([string]$p) {
  if (-not (Test-Path $p)) { return $false }
  $i = Get-Item $p -Force
  return [bool]($i.Attributes -band [IO.FileAttributes]::ReparsePoint)
}

function Get-ReparseTarget([string]$p) {
  $i = Get-Item $p -Force
  $t = $i.Target                       # PS 5.0+ populates this for junctions/symlinks
  if ($t -is [array]) { if ($t.Count -gt 0) { return [string]$t[0] } else { return $null } }
  return [string]$t
}

function Write-Act([string]$msg, [switch]$Change) {
  if ($Apply) { Write-Host "  $msg" }
  else        { Write-Host "  WHATIF: would $msg" }
}

# --- link one workspace -------------------------------------------------------------------------
function Link-Workspace([string]$wsRoot) {
  $name = Split-Path $wsRoot -Leaf
  Write-Host ""
  Write-Host ("=== {0}" -f $wsRoot)

  $canonical = Join-Path $wsRoot '_artifacts\_memory'
  $canonExists = Test-Path $canonical
  $canonCount = 0
  if ($canonExists) { $canonCount = (Get-MemoryFiles $canonical).Count }
  Write-Host ("  canonical : {0}  ({1})" -f $canonical, $(if ($canonExists) { "$canonCount file(s)" } else { 'does not exist yet' }))

  if (-not $canonExists) {
    Write-Act ("create canonical store '{0}'" -f $canonical)
    if ($Apply) { New-Item -ItemType Directory -Force -Path $canonical | Out-Null }
  }

  $slugDir = Resolve-SlugDir $wsRoot
  $link    = Join-Path $slugDir 'memory'
  $slug    = Split-Path $slugDir -Leaf
  $computed = Get-MemorySlug $wsRoot
  if ($slug -cne $computed) { Write-Host ("  slug      : {0}  (reusing existing dir; computed '{1}')" -f $slug, $computed) }
  else                      { Write-Host ("  slug      : {0}" -f $slug) }

  # Already a junction? Check where it points before touching anything.
  if (Test-IsReparse $link) {
    $tgt = Get-ReparseTarget $link
    if ($tgt -and ($tgt.TrimEnd('\') -ieq $canonical.TrimEnd('\'))) {
      Write-Host "    [ok] already junctioned to canonical - nothing to do"
      return
    }
    if (-not $Force) {
      Write-Warning ("    link exists but points at '{0}' - re-run with -Force to re-point" -f $tgt)
      return
    }
    Write-Act ("remove junction pointing at '{0}'" -f $tgt)
    if ($Apply) { [IO.Directory]::Delete($link, $false) }
  }
  elseif (Test-Path $link) {
      # A REAL directory with real files. Decide seed-vs-backup; never merge, never delete.
      $local = Get-MemoryFiles $link
      if ($local.Count -eq 0) {
        Write-Act ("remove empty local memory dir '{0}'" -f $link)
        if ($Apply) { Remove-Item $link -Recurse -Force }
      }
      elseif ($canonCount -eq 0) {
        # Canonical is empty -> this machine SEEDS it. Safe: nothing to overwrite.
        Write-Act ("SEED canonical with {0} local file(s) from '{1}'" -f $local.Count, $link)
        if ($Apply) {
          foreach ($f in $local) { Move-Item $f.FullName (Join-Path $canonical $f.Name) -Force }
          Remove-Item $link -Recurse -Force
        }
        $canonCount = $local.Count
      }
      else {
        # BOTH sides hold files and they may disagree. Back up, do not guess.
        $stamp  = Get-Date -Format 'yyyy-MM-dd_HHmmss'
        $backup = Join-Path $slugDir ("memory.local-backup-{0}" -f $stamp)
        Write-Warning ("    canonical has {0} file(s) AND local has {1} - NOT merging" -f $canonCount, $local.Count)
        Write-Act ("move local memory aside to '{0}' (nothing deleted; reconcile by hand)" -f $backup)
        if ($Apply) { Move-Item $link $backup -Force }
      }
    }

    if (-not (Test-Path $slugDir)) {
      Write-Act ("create slug dir '{0}'" -f $slugDir)
      if ($Apply) { New-Item -ItemType Directory -Force -Path $slugDir | Out-Null }
    }

  Write-Act ("junction '{0}' -> '{1}'" -f $link, $canonical)
  if ($Apply) {
    New-Item -ItemType Junction -Path $link -Target $canonical | Out-Null
    if (Test-IsReparse $link) { Write-Host "    [ok] junction verified" }
    else { throw "junction creation reported success but '$link' is not a reparse point" }
  }
}

# --- targets ------------------------------------------------------------------------------------
$targets = @($Root)
if ($All) {
  $listPath = Join-Path $Root '.agents\maintained-projects.txt'
  if (-not (Test-Path $listPath)) { throw "-All needs '$listPath' (the maintained-projects source of truth)" }
  Get-Content $listPath | ForEach-Object { ($_ -replace '#.*$', '').Trim() } | Where-Object { $_ } | ForEach-Object {
    $p = Join-Path $Root ("Projects\{0}" -f $_)
    if (Test-Path $p) { $targets += (Resolve-Path $p).Path.TrimEnd('\') }
    else { Write-Warning ("maintained project '{0}' not found at '{1}' - skipped" -f $_, $p) }
  }
}

Write-Host ""
Write-Host "=============================================================================="
Write-Host ("CLAUDE MEMORY LINK  ({0})" -f $(if ($Apply) { 'APPLY' } else { 'DRY RUN - re-run with -Apply to write' }))
Write-Host "=============================================================================="
Write-Host ("store: {0}" -f $ProjectsStore)

foreach ($t in $targets) { Link-Workspace $t }

Write-Host ""
if (-not $Apply) { Write-Host "Nothing was written. Re-run with -Apply once the plan above looks right." }
else { Write-Host "Done. Commit the new _artifacts/_memory/ content in each repo it appeared in." }
