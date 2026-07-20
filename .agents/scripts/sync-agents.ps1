<#
.SYNOPSIS
  Push the master .agents toolkit into every command surface: a target's local tool dirs (the lobby or a
  project) AND the machine-global command caches for opencode + Antigravity/Gemini.

.DESCRIPTION
  Single source of authorship = <home>\.agents. The canonical invocable set is .agents\commands\ — it mirrors
  to ALL FOUR platforms (Claude, opencode, Antigravity/Gemini, Codex). This copies commands / skills / hooks /
  opencode-agents into the target's .claude and .opencode dirs (Claude /commands + skills + hooks resolve there)
  and, for a LOBBY sync, also refreshes the machine-global caches so opencode, Antigravity, and Codex see the
  same set Claude does.

  Codex is the lightest surface: it reads AGENTS.md natively AND discovers Agent Skills from .agents\skills
  (repo) + ~\.codex\skills (global), so rules + our own skills need zero work. Only two globals are pushed for
  it: (1) custom prompts -> ~\.codex\prompts (its /commands equivalent, invoked /prompts:<name>), and (2) the
  bmad-* skills -> ~\.codex\skills (BMAD installs to .claude\skills, which Codex does not read).

  Use -WhatIf (alias -DryRun) to preview every copy, create, and delete action without touching disk.

  PLATFORM REACH. A command may declare its reach with frontmatter `platforms: [claude, opencode, antigravity, codex]`.
  Absent = universal (all four). The sync copies a command only to the platforms it lists, so e.g.
  /autopilot_claude (claude-only) never lands in the opencode/gemini/codex surfaces.

  PURGE POLICY.
    - Local tool dirs (.claude, .opencode): copy eligible commands; purge only commands that ARE master-managed
      but are no longer eligible for that platform. Files the master doesn't own (a project's own commands) are
      left alone. Skills / hooks / opencode-agents are an additive robocopy (no delete).
    - SYNC MANIFEST (`.agents\.sync-manifest.json`, per target). Additive copies alone leaked ghosts: a command
      DELETED or RENAMED in the master lingered in every copy forever, and because a project's vendored .agents
      is itself the SOURCE for that project's .claude/.opencode menus, the ghost was re-generated into the menus
      on every subsequent sync (the name-based purge above can't catch it — once the master drops the name the
      file reads as "project-own, leave alone"). Each run now records exactly what it wrote; the next run deletes
      what IT previously wrote and no longer owns. Anything the sync never wrote — project-authored commands,
      project rules, BMAD's own installs — is absent from the manifest and therefore CANNOT be purged by it.
      A missing/corrupt manifest degrades safely to "purge nothing this run".
    - Global caches (opencode + Antigravity + Codex prompts): MIRROR-EXACT — copy eligible, purge anything not
      eligible, EXCEPT `bmad-*` (BMAD installs its own global agents/workflows; never ours to delete).
    - Codex skills cache (~\.codex\skills): mirror `bmad-*` skill dirs from .claude\skills (per-dir /MIR); purge
      codex-side bmad-* dirs whose source is gone; PRESERVE `.system` and any foreign (non-bmad) dirs.
    - Project .agents vendor: ADDITIVE. The vendored .agents is a HYBRID (master toolkit + project-owned
      rules\, skills\, and bmad\), so it is NEVER mirrored/purged wholesale. bmad\ is EXCLUDED from the vendor
      robocopy entirely (BMAD's module config is project-identity — each repo's own `project_name` — and BMAD
      self-installs per project; master must never overwrite it). The lone deletion is a narrow prune of
      stale workflows\ command-ghosts — a workflows\ file whose name is a master COMMAND but not a master
      WORKFLOW (a leftover from when commands lived in workflows\). That test provably never hits rules\,
      skills\, bmad\, or a project-authored workflow.

  For a PROJECT target (not the lobby root) it ALSO vendors master's .agents into the project so the repo is
  clone-safe. That vendor is ADDITIVE (/E, no purge): a project's .agents is a HYBRID — master toolkit copied
  in, layered OVER project-OWNED content master does NOT have (notably .agents\rules\ and project-specific
  .agents\skills\). .agents\bmad\ is EXCLUDED from the vendor (project-owned identity; see PURGE POLICY). So
  NEVER /MIR or blanket-/PURGE the vendored .agents — that deletes the project's own files. The only deletion
  here is the narrow workflows\ command-ghost prune (see PURGE POLICY). A project
  sync does NOT touch the machine-global caches (globals reflect the lobby's canonical set).

  Always edit the master; never hand-edit the copies. Re-run this to propagate changes.

.PARAMETER Target
  Directory to sync into. Default: the home-base root (lobby).

.PARAMETER GlobalsOnly
  Refresh only the machine-global caches (opencode + Antigravity command caches, Codex prompts, and the Codex
  bmad-* skills mirror) from the lobby master. Skips local tool dirs. /slash_command_updating delegates to this.

.PARAMETER NoGlobals
  Sync local tool dirs only; skip the machine-global caches (incl. the Codex prompts + skills mirror) even on a
  lobby sync.

.PARAMETER WhatIf
  Preview mode. Report every copy, directory creation, and deletion that would happen, but perform no writes.
  Alias: -DryRun.
#>
param(
  [string]$Target,
  [switch]$GlobalsOnly,
  [switch]$NoGlobals,
  [switch]$Maintained,
  [switch]$Status,
  [switch]$Reconcile,
  [Alias('DryRun')][switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$Master   = Split-Path $PSScriptRoot -Parent     # ...\.agents
$HomeRoot = Split-Path $Master -Parent           # ...\Sudo_Hatter_Command

# -Maintained: the ONLY sanctioned "sync everything" — the lobby + ONLY the projects on the
# .agents\maintained-projects.txt allowlist (shared with check_maps.py). Never hand-loop over
# Projects\* : that touches child repos we deliberately do not keep in sync. -Target is ignored here.
if ($Maintained) {
  Write-Host "sync-agents: -Maintained fan-out (lobby + .agents\maintained-projects.txt)"
  & $PSCommandPath -Status:$Status -Reconcile:$Reconcile -WhatIf:$WhatIf   # lobby (default target; refreshes globals)
  $listFile = Join-Path $HomeRoot ".agents\maintained-projects.txt"
  if (Test-Path $listFile) {
    foreach ($line in Get-Content $listFile) {
      $name = ($line -replace '#.*$', '').Trim()
      if (-not $name) { continue }
      $proj = Join-Path $HomeRoot "Projects\$name"
      if (Test-Path $proj) {
        & $PSCommandPath -Target $proj -NoGlobals -Status:$Status -Reconcile:$Reconcile -WhatIf:$WhatIf
      } else {
        Write-Warning "sync-agents: maintained project '$name' not found under Projects\ - skipping"
      }
    }
  } else {
    Write-Warning "sync-agents: no .agents\maintained-projects.txt found - only the lobby was synced"
  }
  exit 0
}

if (-not $Target) { $Target = $HomeRoot }
$Target   = (Resolve-Path $Target).Path
$IsLobby  = ($Target.TrimEnd('\') -ieq $HomeRoot.TrimEnd('\'))

$AllPlatforms = @('claude','opencode','antigravity','codex')

# --- helpers ------------------------------------------------------------------

function Sync-Dir($src, $dst, [string[]]$ExcludeDirs, [string[]]$ExcludeFiles, [switch]$WhatIf) {
  if (-not (Test-Path $src)) { return }
  $xd = @('node_modules') + (@($ExcludeDirs) | Where-Object { $_ })
  $xf = @(@($ExcludeFiles) | Where-Object { $_ })
  if (-not $WhatIf) {
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    if ($xf) { robocopy $src $dst /E /XD @xd /XF @xf /NFL /NDL /NJH /NJS /NC /NS | Out-Null }
    else     { robocopy $src $dst /E /XD @xd          /NFL /NDL /NJH /NJS /NC /NS | Out-Null }
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($src -> $dst), rc=$LASTEXITCODE" }
  } else {
    Write-Host ("WHATIF: would robocopy '{0}' -> '{1}' (excluding: {2})" -f $src,$dst,($xd -join ', '))
  }
}

# --- sync manifest: the fix for the "sync never purges" blind spot ------------
# See PURGE POLICY in the header. The manifest is a record of what THIS sync wrote, so the next run can
# delete its own retired output without ever touching a file it did not create.
$ManifestName = '.sync-manifest.json'

function Get-SyncManifest([string]$target) {
  $p = Join-Path $target ".agents\$ManifestName"
  $empty = @{ vendor = @(); local = @{} }
  if (-not (Test-Path $p)) { return $empty }
  try {
    $j = Get-Content $p -Raw | ConvertFrom-Json
    $local = @{}
    if ($j.local) { foreach ($prop in $j.local.PSObject.Properties) { $local[$prop.Name] = @($prop.Value) } }
    return @{ vendor = @($j.vendor); local = $local }
  } catch {
    # Fail SAFE, never destructive: an unreadable manifest means we cannot prove ownership, so we purge nothing.
    Write-Warning ("sync-agents: unreadable {0} ({1}) - purging nothing this run" -f $ManifestName, $_.Exception.Message)
    return $empty
  }
}

function Save-SyncManifest([string]$target, $manifest, [switch]$WhatIf) {
  $p = Join-Path $target ".agents\$ManifestName"
  if ($WhatIf) { Write-Host ("WHATIF: would write sync manifest '{0}'" -f $p); return }
  New-Item -ItemType Directory -Force -Path (Split-Path $p -Parent) | Out-Null
  $out = [ordered]@{
    version   = 1
    generated = (Get-Date).ToString('s')
    note      = 'Generated by sync-agents.ps1. Records what the sync wrote so the next run can purge its own retired files. Do not hand-edit.'
    vendor    = @($manifest.vendor)
    local     = $manifest.local
  }
  ($out | ConvertTo-Json -Depth 6) | Set-Content -Path $p -Encoding utf8
}

# --- reconcile: a git-status-style three-way view of the invocable surfaces ---
# Mental model: the master is the remote, each copy is a working tree, the manifest is the index.
#   M  differs  — the copy's content is not master's. Either the copy was hand-edited (master wins: the next
#                 sync overwrites it, so surfacing it first means the edit isn't lost silently) or master moved
#                 ahead and this copy simply hasn't been synced yet. Both resolve the same way — run a sync.
#   ?  orphan   — present in the copy, but master has no such command. Either a PROJECT-AUTHORED command
#                 (legitimate, e.g. /autopilot_glm) or a PRE-MANIFEST GHOST (a file retired before the manifest
#                 existed, so no record proves we wrote it). Nothing can tell these apart automatically, which
#                 is exactly what project-own.txt is for.
# Scope is deliberately the INVOCABLE surfaces only. rules\ and skills\ are legitimately hybrid (project-owned
# content lives beside master's), so flagging orphans there would be pure noise, and purging there would be
# destructive. Ghosts only do harm where they become typeable commands, and that is precisely what we cover.
$OwnListName = 'project-own.txt'

# $null = no list authored yet (which BLOCKS purging); @() = an authored, deliberately empty list (purge all orphans).
function Get-OwnAllowList([string]$target) {
  $p = Join-Path $target ".agents\$OwnListName"
  if (-not (Test-Path $p)) { return $null }
  $items = @(Get-Content $p | ForEach-Object { ($_ -replace '#.*$','').Trim() } | Where-Object { $_ })
  # The leading comma is load-bearing: PowerShell unrolls a returned EMPTY array back to $null, which would
  # make a fully-curated list ("claim nothing, purge everything") read as "no list authored yet" and stage
  # forever instead of purging. Wrapping preserves @() as a real, distinct value.
  return ,$items
}

function Get-SurfaceState {
  param([string]$Target, [string]$MasterDir)
  $mCmd = @(Get-ChildItem (Join-Path $MasterDir 'commands')  -Filter *.md -File -ErrorAction SilentlyContinue)
  $mWf  = @(Get-ChildItem (Join-Path $MasterDir 'workflows') -Filter *.md -File -ErrorAction SilentlyContinue)
  # .claude/.opencode hold a platform-FILTERED subset, so "absent" there is normal and never a finding; we only
  # ever ask whether a file present in the copy corresponds to a master command at all.
  $map = [ordered]@{
    '.agents\commands'   = $mCmd
    '.agents\workflows'  = $mWf
    '.claude\commands'   = $mCmd
    '.opencode\commands' = $mCmd
  }
  $rows = @()
  foreach ($key in $map.Keys) {
    $dir = Join-Path $Target $key
    if (-not (Test-Path $dir)) { continue }
    $byName = @{}
    foreach ($f in $map[$key]) { $byName[$f.Name] = $f.FullName }
    foreach ($f in (Get-ChildItem $dir -Filter *.md -File -ErrorAction SilentlyContinue)) {
      $state = $null
      if (-not $byName.ContainsKey($f.Name)) {
        $state = 'orphan'
      } elseif ((Get-FileHash $f.FullName -Algorithm MD5).Hash -ne (Get-FileHash $byName[$f.Name] -Algorithm MD5).Hash) {
        $state = 'modified'
      }
      if ($state) { $rows += [pscustomobject]@{ Surface = $key; Name = $f.Name; State = $state; Path = $f.FullName } }
    }
  }
  return $rows
}

# Files under the master that a vendor copy is expected to place (relative paths), mirroring Sync-Dir's excludes.
function Get-VendorFileSet([string]$masterDir) {
  $root = (Resolve-Path $masterDir).Path
  Get-ChildItem $masterDir -File -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { ($_.FullName -notmatch '\\(bmad|node_modules)\\') -and ($_.Name -ne $ManifestName) } |
    ForEach-Object { $_.FullName.Substring($root.Length).TrimStart('\') }
}

# Delete what a previous run wrote into $dst and this run no longer owns. Returns the purged relative paths.
function Invoke-ManifestPurge([string]$dst, [string[]]$was, [string[]]$now, [switch]$WhatIf) {
  $purged = @()
  foreach ($rel in @($was | Where-Object { $_ -and ($now -notcontains $_) })) {
    $f = Join-Path $dst $rel
    if (-not (Test-Path $f)) { continue }
    if ($WhatIf) { Write-Host ("WHATIF: would purge retired file '{0}' (master no longer owns it)" -f $f) }
    else         { Remove-Item $f -Force }
    $purged += $rel
  }
  return $purged
}

# Read a command file's `platforms:` frontmatter. Absent / no frontmatter => universal (all three).
# Recognized inline form only:  platforms: [claude, opencode]
# An explicit empty list (platforms: []) means "nowhere" — the file is documentation, not an invocable command.
function Get-CommandPlatforms($file) {
  $inFM = $false; $n = 0
  foreach ($line in [System.IO.File]::ReadAllLines($file)) {
    $n++
    $t = $line.Trim()
    if ($n -eq 1 -and $t -ne '---') { return $AllPlatforms }      # no frontmatter at all
    if ($t -eq '---') { if ($inFM) { break } else { $inFM = $true; continue } }
    if ($inFM -and $line -match '^\s*platforms:\s*\[(.*?)\]') {
      $items = $matches[1].Split(',') |
               ForEach-Object { $_.Trim().Trim('"').Trim("'").ToLower() } |
               Where-Object { $_ }
      # A matched, explicit empty list is intentionally "nowhere"; missing/empty key falls through to universal.
      return @($items)
    }
  }
  return $AllPlatforms
}

# Sync the canonical command set into $Dst for a given $Platform.
#   $MasterCmdDir : the authoritative .agents\commands to read from
#   -Mirror       : global-cache mode (purge non-eligible ghosts; preserve only FOREIGN bmad-* = BMAD's own
#                   global install); else local mode (purge only master-managed-but-ineligible; leave
#                   unknown/project-own files untouched)
#   -WhatIf       : report actions but do not copy or delete
# Returns the list of eligible file names.
function Sync-CommandDir {
  # -SkipAP: robot-lane commands (*_AP.md — invoked by the autopilot engines, never typed by a human) are
  # vendored ONLY into project tool dirs (the engines Push-Location into the project and resolve them there).
  # The lobby's typeable menus and the machine-global caches skip them; the purge branch below then removes
  # any stale copies automatically on every sync.
  param([string]$MasterCmdDir, [string]$Dst, [string]$Platform, [switch]$Mirror, [switch]$SkipAP, [switch]$WhatIf)
  New-Item -ItemType Directory -Force -Path $Dst | Out-Null
  $masterFiles = Get-ChildItem -Path $MasterCmdDir -Filter '*.md' -File
  $masterNames = @($masterFiles | Select-Object -ExpandProperty Name)
  $eligible = @()
  foreach ($f in $masterFiles) {
    if ($SkipAP -and ($f.Name -match '_AP\.md$')) { continue }
    if ((Get-CommandPlatforms $f.FullName) -contains $Platform) {
      if (-not $WhatIf) {
        Copy-Item -Path $f.FullName -Destination $Dst -Force
      } else {
        Write-Host ("WHATIF: would copy command '{0}' -> '{1}' for platform '{2}'" -f $f.Name,$Dst,$Platform)
      }
      $eligible += $f.Name
    }
  }
  $toPurge = Get-ChildItem -Path $Dst -Filter '*.md' -File -ErrorAction SilentlyContinue | Where-Object {
    $name = $_.Name
    if ($eligible -contains $name)        { $false }                      # keep: eligible for this platform
    elseif ($masterNames -contains $name) { $true }                       # purge: OUR command, not eligible here
    elseif ($Mirror)                      { -not ($name -match '^bmad-') } # global: purge foreign ghosts, keep BMAD's own
    else                                  { $false }                      # local: keep foreign/project-own files
  }
  if (-not $WhatIf) {
    $toPurge | Remove-Item -Force
  } else {
    $toPurge | ForEach-Object { Write-Host ("WHATIF: would delete command '{0}' from '{1}'" -f $_.Name,$Dst) }
  }
  return $eligible
}

# Mirror the sudo-* dev flow into .agents/workflows/ so ANTIGRAVITY sees it. Antigravity surfaces / from
# workflows/ (+ skills/), never commands/ (a Claude/opencode concept). The sudo flow is authored as
# commands; copy the antigravity-eligible ones (sudo-*, excluding _AP claude-only) into workflows/ VERBATIM
# (frontmatter stays line 1 -- no injected header) so the same / works in all three tools from ONE source.
# Mirror ONLY sudo-* on purpose: BMAD personas are skills and 1_* are real workflows, so mirroring those too
# would make duplicate / entries. Generated copies, regenerated every sync -- edit the command, not these.
function Sync-AntigravityWorkflowMirror {
  param([string]$MasterDir, [switch]$WhatIf)
  $cmdDir = Join-Path $MasterDir "commands"
  $wfDir  = Join-Path $MasterDir "workflows"
  if (-not $WhatIf) { New-Item -ItemType Directory -Force -Path $wfDir | Out-Null } else { Write-Host "WHATIF: would ensure dir '$wfDir'" }
  $mirrored = @()
  
  $allowed = @('sudo-*.md', '1_*.md', 'new-project.md', 'slash_command_updating.md', 'merge_main_debug.md')
  $excluded = @('update-maps-indexes.md', 'sudo-adviser-board.md') # Real workflow lives in workflows/, do not overwrite with command wrapper (adviser-board: hand-authored thin launcher — the full command is ~25k, over AG's 12k limit)
  
  $files = Get-ChildItem -Path $cmdDir -Filter '*.md' -File | Where-Object {
    $name = $_.Name
    $match = $false
    foreach ($p in $allowed) { if ($name -like $p) { $match = $true; break } }
    $match -and ($excluded -notcontains $name)
  }

  foreach ($f in $files) {
    if (($f.Name -notmatch '_AP\.md$') -and ((Get-CommandPlatforms $f.FullName) -contains 'antigravity')) {
      if ((Get-Item $f.FullName).Length -gt 12000) {
        Write-Warning ("sync-agents: '{0}' exceeds Antigravity's 12000-char workflow limit; mirrored anyway" -f $f.Name)
      }
      if (-not $WhatIf) {
        Copy-Item -Path $f.FullName -Destination (Join-Path $wfDir $f.Name) -Force
      } else {
        Write-Host ("WHATIF: would mirror '{0}' -> workflows/' for antigravity" -f $f.FullName)
      }
      $mirrored += $f.Name
    }
  }
  # Prune stale generated mirrors: any file in workflows/ that matches our allowed patterns but is NO LONGER mirrored.
  # (Except the excluded ones which we intentionally don't mirror, but might legitimately exist in workflows/)
  $stale = Get-ChildItem -Path $wfDir -Filter '*.md' -File -ErrorAction SilentlyContinue |
    Where-Object { 
      $name = $_.Name
      $match = $false
      foreach ($p in $allowed) { if ($name -like $p) { $match = $true; break } }
      $match -and ($excluded -notcontains $name) -and ($mirrored -notcontains $name)
    }
    
  if (-not $WhatIf) {
    $stale | ForEach-Object { Remove-Item $_.FullName -Force }
  } else {
    $stale | ForEach-Object { Write-Host ("WHATIF: would delete stale mirror '{0}' from workflows/'" -f $_.Name) }
  }
  return $mirrored
}

# Mirror the BMAD skills into Codex's machine-global skills cache (~/.codex/skills). Codex implements the
# open Agent Skills standard and discovers .agents/skills (repo) + ~/.codex/skills (global) -- but NOT
# .claude/skills, which is where BMAD installs its 56 bmad-* skills (its manifest targets claude-code +
# antigravity only). Our OWN skills already live in .agents/skills, so Codex sees them from the repo; only the
# bmad-* set is missing. This mirrors each .claude/skills/bmad-* dir into ~/.codex/skills so Codex invokes BMAD
# natively via /skills (same model as Claude -- no /prompts: stub, which would double the menu entry). Machine-
# local by design, exactly like the prompts + opencode/antigravity command caches; re-run sync to refresh.
# Per-dir /MIR is safe (mirrors WITHIN one skill dir only). Codex-side bmad-* dirs whose source is gone are
# purged; .system and any foreign (non-bmad) dirs are preserved.
function Sync-CodexSkills {
  param([string]$SkillSrcDir, [string]$Dst, [switch]$WhatIf)
  if (-not (Test-Path $SkillSrcDir)) { Write-Warning "sync-agents: SKIPPED codex skills - no source '$SkillSrcDir'"; return 0 }
  try {
    if (-not $WhatIf) { New-Item -ItemType Directory -Force -Path $Dst -ErrorAction SilentlyContinue | Out-Null }
    if (-not (Test-Path $Dst) -and -not $WhatIf) { throw "path not writable (broken junction or missing target?)" }
  } catch {
    Write-Warning ("sync-agents: SKIPPED codex skills cache '{0}' - {1}" -f $Dst, $_.Exception.Message); return 0
  }
  $srcSkills = Get-ChildItem -Path $SkillSrcDir -Directory -Filter 'bmad-*' -ErrorAction SilentlyContinue
  $srcNames  = @($srcSkills | Select-Object -ExpandProperty Name)
  foreach ($s in $srcSkills) {
    $tgt = Join-Path $Dst $s.Name
    if (-not $WhatIf) {
      New-Item -ItemType Directory -Force -Path $tgt | Out-Null
      robocopy $s.FullName $tgt /MIR /NFL /NDL /NJH /NJS /NC /NS /XD node_modules | Out-Null
      if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($($s.FullName) -> $tgt), rc=$LASTEXITCODE" }
    } else {
      Write-Host ("WHATIF: would mirror codex skill '{0}' -> '{1}'" -f $s.Name, $tgt)
    }
  }
  # Purge codex-side bmad-* dirs whose source no longer exists. Never touch .system or foreign (non-bmad) dirs.
  $stale = Get-ChildItem -Path $Dst -Directory -Filter 'bmad-*' -ErrorAction SilentlyContinue |
    Where-Object { $srcNames -notcontains $_.Name }
  if (-not $WhatIf) {
    $stale | ForEach-Object { Remove-Item $_.FullName -Recurse -Force }
  } else {
    $stale | ForEach-Object { Write-Host ("WHATIF: would delete stale codex skill '{0}'" -f $_.Name) }
  }
  return $srcNames.Count
}

Write-Host "sync-agents: master=$Master"
Write-Host "sync-agents: target=$Target (lobby=$IsLobby)"
if ($WhatIf) { Write-Host "sync-agents: *** WHATIF / DRY-RUN MODE *** no files will be changed" }

# --- -Status: read-only reconciliation report, then stop (writes NOTHING) -----
if ($Status) {
  $rows = @(Get-SurfaceState $Target $Master)
  $own  = Get-OwnAllowList $Target
  Write-Host ("sync-agents: STATUS {0} (read-only)" -f $Target)
  if (-not $rows) {
    Write-Host "  clean - every invocable file matches the master."
  } else {
    foreach ($r in ($rows | Sort-Object Surface, Name)) {
      $tag = if ($r.State -eq 'modified')            { 'M  ' }
             elseif ($own -and ($own -contains $r.Name)) { 'own' }
             else                                    { '?  ' }
      Write-Host ("  {0} {1,-20} {2}" -f $tag, $r.Surface, $r.Name)
    }
    $m = @($rows | Where-Object { $_.State -eq 'modified' }).Count
    $o = @($rows | Where-Object { $_.State -eq 'orphan' -and -not ($own -and ($own -contains $_.Name)) }).Count
    $k = @($rows | Where-Object { $_.State -eq 'orphan' -and ($own -and ($own -contains $_.Name)) }).Count
    Write-Host ("  legend: M = differs from master (a sync overwrites it with master's) - ? = orphan, master has no such command - own = kept by {0}" -f $OwnListName)
    Write-Host ("  totals: {0} differing, {1} unclaimed orphan(s), {2} project-owned" -f $m, $o, $k)
    if ($o) { Write-Host "  resolve with: -Reconcile (stages a keep-list first; never deletes unreviewed)" }
  }
  exit 0
}

# Regenerate the Antigravity workflow mirrors in the master BEFORE vendoring, so projects pick them up via
# the (additive) .agents vendor. (Global command cache still mirrors commands/ separately, unchanged.)
$agWf = Sync-AntigravityWorkflowMirror $Master -WhatIf:$WhatIf
Write-Host "sync-agents: antigravity workflow mirror -> $($agWf.Count) sudo-* in .agents/workflows/"

# --- local tool dirs ----------------------------------------------------------
if (-not $GlobalsOnly) {
  # What the LAST run wrote here. Everything purged below is drawn from this record, never from a bare
  # "not in master" test — that test cannot tell a retired ghost from a project's own command.
  $manifest = Get-SyncManifest $Target
  # Rebuilt from scratch each run and swapped in at save time, so keys from an older layout (or an older
  # absolute-path scheme) age out instead of accumulating forever.
  $newLocal = @{}
  # Project target → vendor master's .agents into the project ADDITIVELY (Sync-Dir = /E, no purge). The
  # project's .agents is a HYBRID: master toolkit layered over project-OWNED rules\ + project skills\ that
  # master does NOT have. Do NOT change this to /MIR or a blanket /PURGE — it deletes the project's own files.
  if (-not $IsLobby) {
    # Exclude bmad\ from the vendor: BMAD's module config is PROJECT-OWNED (each repo carries its own
    # `project_name` etc.) and BMAD self-installs per project, so it must NOT be overwritten from master.
    # This keeps it project-owned the same way rules\ already are (additive vendor, master never clobbers it).
    Sync-Dir $Master (Join-Path $Target ".agents") @((Join-Path $Master 'bmad')) @($ManifestName) -WhatIf:$WhatIf

    # THE BLIND-SPOT FIX. The vendor above is additive, so a master file that was deleted or renamed used to
    # live on here forever — and since this vendored .agents is the SOURCE for this project's .claude/.opencode
    # menus (see $src below), the ghost was re-published into the menus on every sync. Purge strictly what a
    # previous run of this script wrote and the master has since dropped; project-owned rules\, project skills\,
    # bmad\ and any project-authored command were never in the manifest and are structurally unreachable here.
    $vendorNow    = @(Get-VendorFileSet $Master)
    $vendorPurged = Invoke-ManifestPurge (Join-Path $Target ".agents") $manifest.vendor $vendorNow -WhatIf:$WhatIf
    if ($vendorPurged.Count) {
      Write-Host "sync-agents: purged $($vendorPurged.Count) retired vendor file(s): $($vendorPurged -join ', ')"
    }
    $manifest.vendor = $vendorNow

    # Inventory (never delete) the project's OWN invocables, so local-only additions stay visible instead of
    # being mistaken for drift later. These are legitimately outside the master — reported, not touched.
    foreach ($sub in @('commands','workflows')) {
      $d = Join-Path $Target ".agents\$sub"
      if (-not (Test-Path $d)) { continue }
      $own = @(Get-ChildItem $d -Filter *.md -File -ErrorAction SilentlyContinue |
               Where-Object { $vendorNow -notcontains "$sub\$($_.Name)" } |
               Select-Object -ExpandProperty Name)
      if ($own.Count) { Write-Host ("sync-agents: .agents\{0}\ has {1} project-owned file(s), left alone: {2}" -f $sub, $own.Count, ($own -join ', ')) }
    }
    # Prune stale command-ghosts from the vendored workflows/: a file that is a master COMMAND but NOT a
    # master workflow is a leftover from the old layout (commands used to live in workflows/). This is the
    # ONLY purge on the vendored .agents and it is provably safe — it can never touch rules/, skills/, or a
    # project-authored workflow (none of those are master commands). Everything else stays additive (/E).
    $mWf  = @(Get-ChildItem (Join-Path $Master "workflows") -Filter *.md -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
    $mCmd = @(Get-ChildItem (Join-Path $Master "commands")  -Filter *.md -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
    $purged = 0
    $ghosts = Get-ChildItem (Join-Path $Target ".agents\workflows") -Filter *.md -File -ErrorAction SilentlyContinue |
      Where-Object { ($mWf -notcontains $_.Name) -and ($mCmd -contains $_.Name) }
    if (-not $WhatIf) {
      $ghosts | ForEach-Object { Remove-Item $_.FullName -Force; $purged++ }
    } else {
      $ghosts | ForEach-Object { Write-Host ("WHATIF: would delete stale vendor command-ghost '{0}'" -f $_.FullName); $purged++ }
    }
    if ($purged) { Write-Host "sync-agents: purged $purged stale workflows/ command-ghost(s) from the vendor" }
  }

  # Source of truth for this target's tool dirs: master for the lobby, vendored copy for a project.
  $src    = if ($IsLobby) { $Master } else { Join-Path $Target ".agents" }
  $cmdDir = Join-Path $src "commands"

  # Manifest keys are RELATIVE to the target, so the record stays valid if the repo is moved or re-cloned.
  $claudeCmdKey = ".claude\commands"
  $claudeCmdDst = Join-Path $Target $claudeCmdKey
  $cl = Sync-CommandDir $cmdDir $claudeCmdDst "claude" -SkipAP:$IsLobby -WhatIf:$WhatIf
  # Second half of the blind-spot fix: a command the master RENAMED or DELETED stops being master-managed, so
  # Sync-CommandDir's name test reclassifies it as "project-own, keep". The manifest remembers we wrote it.
  $clGone = Invoke-ManifestPurge $claudeCmdDst $manifest.local[$claudeCmdKey] $cl -WhatIf:$WhatIf
  if ($clGone.Count) { Write-Host "sync-agents: purged $($clGone.Count) retired .claude command(s): $($clGone -join ', ')" }
  $newLocal[$claudeCmdKey] = $cl
  # bmad-* skills are BMAD-OWNED. BMAD self-installs them (its `ides:` = claude-code, antigravity) directly into
  # .claude\skills, .opencode, and .agent\skills, and refreshes them on every `bmad` update. Our toolkit must NOT
  # carry or shadow them: a stale vendored copy in .agents\skills would clobber BMAD's current install on each
  # sync (robocopy overwrites same-named files). Exclude bmad-* so BMAD stays the single source for its own skills.
  Sync-Dir (Join-Path $src "skills")          (Join-Path $Target ".claude\skills") @('bmad-*') -WhatIf:$WhatIf
  Sync-Dir (Join-Path $src "hooks")           (Join-Path $Target ".claude\hooks") -WhatIf:$WhatIf
  $ocCmdKey = ".opencode\commands"
  $ocCmdDst = Join-Path $Target $ocCmdKey
  $oc = Sync-CommandDir $cmdDir $ocCmdDst "opencode" -SkipAP:$IsLobby -WhatIf:$WhatIf
  $ocGone = Invoke-ManifestPurge $ocCmdDst $manifest.local[$ocCmdKey] $oc -WhatIf:$WhatIf
  if ($ocGone.Count) { Write-Host "sync-agents: purged $($ocGone.Count) retired .opencode command(s): $($ocGone -join ', ')" }
  $newLocal[$ocCmdKey] = $oc
  Sync-Dir (Join-Path $src "opencode-agents") (Join-Path $Target ".opencode\agent") -WhatIf:$WhatIf

  Write-Host "sync-agents: .claude\commands   -> $($cl.Count) cmds"
  Write-Host "sync-agents: .opencode\commands -> $($oc.Count) cmds"

  # Record what THIS run wrote, so the next one can retire it. Written last: a mid-run failure leaves the
  # older manifest in place, which only ever means "purge less next time" — never an unowned deletion.
  $manifest.local = $newLocal
  Save-SyncManifest $Target $manifest -WhatIf:$WhatIf

  # --- -Reconcile: clear out orphans the manifest can't vouch for ------------
  # The manifest retires what the sync ITSELF wrote, which cannot cover files retired before the manifest
  # existed (Fresh's 8 restructure ghosts) or dropped in by hand. Those are indistinguishable from a project's
  # own commands, so this NEVER guesses: the first run STAGES a keep-list and deletes nothing. The human edits
  # that list (delete a line = "purge this"), and only the second run acts. Same staging idea as `git add`.
  if ($Reconcile) {
    $orphans = @(Get-SurfaceState $Target $Master | Where-Object { $_.State -eq 'orphan' })
    $own     = Get-OwnAllowList $Target
    $ownPath = Join-Path $Target ".agents\$OwnListName"
    if (-not $orphans.Count) {
      Write-Host "sync-agents: reconcile - no orphans, nothing to resolve."
    } elseif ($null -eq $own) {
      $names = @($orphans | Select-Object -ExpandProperty Name -Unique | Sort-Object)
      Write-Warning ("sync-agents: reconcile found {0} orphan(s) and no {1} yet - STAGING, deleting nothing." -f $names.Count, $OwnListName)
      if ($WhatIf) {
        Write-Host ("WHATIF: would stage keep-list '{0}' with: {1}" -f $ownPath, ($names -join ', '))
      } else {
        $header = @(
          "# project-own.txt - commands/workflows THIS repo owns that the master toolkit does not.",
          "# Every name listed here is preserved forever; sync-agents will never purge it.",
          "# DELETE a line to mark that file as a stale ghost - the next -Reconcile removes it everywhere.",
          "# Staged automatically on the first -Reconcile. Review before re-running.",
          ""
        )
        Set-Content -Path $ownPath -Value ($header + $names) -Encoding utf8
        Write-Host ("sync-agents: staged {0} - review it, delete the lines you want purged, then re-run -Reconcile" -f $ownPath)
      }
      $names | ForEach-Object { Write-Host ("    staged (kept): {0}" -f $_) }
    } else {
      $kill = @($orphans | Where-Object { $own -notcontains $_.Name })
      if (-not $kill.Count) {
        Write-Host ("sync-agents: reconcile - all {0} orphan(s) are claimed by {1}, nothing purged." -f $orphans.Count, $OwnListName)
      } else {
        foreach ($o in $kill) {
          if ($WhatIf) { Write-Host ("WHATIF: would reconcile-purge unclaimed orphan '{0}'" -f $o.Path) }
          else         { Remove-Item $o.Path -Force }
        }
        $verb = if ($WhatIf) { 'would purge' } else { 'purged' }
        Write-Host ("sync-agents: reconcile {0} {1} unclaimed orphan(s): {2}" -f $verb, $kill.Count, (($kill | Select-Object -ExpandProperty Name -Unique) -join ', '))
      }
    }
  }
}

# --- machine-global caches (lobby only; always source the true master) --------
# Each cache is guarded independently: a missing/broken target (e.g. a dangling junction) is SKIPPED with a
# warning, never crashes the run — so one bad path can't block the other cache or the (already-done) local sync.
if ((-not $NoGlobals) -and ($IsLobby -or $GlobalsOnly)) {
  $GlobalCmdSrc = Join-Path $Master "commands"
  $caches = @(
    @{ Name = 'opencode';    Platform = 'opencode';    Path = (Join-Path $env:USERPROFILE ".config\opencode\commands") },
    @{ Name = 'antigravity'; Platform = 'antigravity'; Path = (Join-Path $env:USERPROFILE ".gemini\antigravity\global_workflows") },
    # Codex custom prompts (invoked /prompts:<name>). Global-only -- Codex has no repo-level prompts dir; its
    # repo surface is AGENTS.md + .agents/skills (already handled). bmad-* skills go to ~/.codex/skills below.
    @{ Name = 'codex';       Platform = 'codex';       Path = (Join-Path $env:USERPROFILE ".codex\prompts") }
  )
  foreach ($c in $caches) {
    try {
      if (-not $WhatIf) {
        New-Item -ItemType Directory -Force -Path $c.Path -ErrorAction SilentlyContinue | Out-Null
      } else {
        Write-Host ("WHATIF: would ensure global cache dir '{0}'" -f $c.Path)
      }
      if (-not (Test-Path $c.Path)) { throw "path not writable (broken junction or missing target?)" }
    } catch {
      Write-Warning ("sync-agents: SKIPPED {0} global cache '{1}' - {2}" -f $c.Name, $c.Path, $_.Exception.Message)
      continue
    }
    $names = Sync-CommandDir $GlobalCmdSrc $c.Path $c.Platform -Mirror -SkipAP -WhatIf:$WhatIf
    Write-Host ("sync-agents: {0} global -> {1} cmds  ({2})" -f $c.Name, $names.Count, $c.Path)
  }
  Write-Host "sync-agents: (global caches mirror-exact; bmad-* preserved; restart opencode to pick up)"

  # Codex reads Agent Skills natively but NOT .claude/skills (where BMAD installs). Mirror the bmad-* skills
  # into ~/.codex/skills so BMAD is reachable from Codex via /skills (Daniel: "we use bmad in everything").
  $codexSkillsDst = Join-Path $env:USERPROFILE ".codex\skills"
  $bmadSkillSrc   = Join-Path $HomeRoot ".claude\skills"
  $codexSkillCount = Sync-CodexSkills $bmadSkillSrc $codexSkillsDst -WhatIf:$WhatIf
  Write-Host ("sync-agents: codex skills -> {0} bmad-* mirrored  ({1})" -f $codexSkillCount, $codexSkillsDst)
}

# --- Fresh living-template drift check (lobby sync only) ----------------------
# Fresh_Workspace_BMAD is the skeleton new projects clone from. This sync already vendors .agents/ into it
# (additive, above), but the FRONT DOOR + docs are per-workspace and are NOT synced (copying them would wipe
# the skeleton's own content). So instead of a blind copy, FLAG when Fresh's front-door pattern has drifted
# from the lobby — the agent reconciles it by hand (living-template-sync rule), keeping it generic.
if ($IsLobby -and -not $GlobalsOnly) {
  $fresh = Join-Path $HomeRoot "Projects\Fresh_Workspace_BMAD"
  if (Test-Path $fresh) {
    $warn = @()
    if (-not (Test-Path (Join-Path $fresh "docs\gitnexus.md"))) { $warn += "missing docs/gitnexus.md (GitNexus own-file pattern)" }
    $fa = Join-Path $fresh "AGENTS.md"
    if (Test-Path $fa) {
      $t = Get-Content $fa -Raw
      if ($t -notmatch 'read that FIRST') { $warn += "AGENTS.md is missing the reading-order rule" }
      if ($t -match 'gitnexus:start')     { $warn += "AGENTS.md still inlines a GitNexus block (should be docs/gitnexus.md + pointer)" }
    } else { $warn += "no root AGENTS.md" }
    $lws = Join-Path $HomeRoot "docs\workspace-standard.md"
    $fws = Join-Path $fresh "docs\workspace-standard.md"
    if ((Test-Path $lws) -and (Test-Path $fws)) {
      if ((Get-FileHash $lws).Hash -ne (Get-FileHash $fws).Hash) { $warn += "docs/workspace-standard.md differs from the lobby canon" }
    } elseif (-not (Test-Path $fws)) { $warn += "missing docs/workspace-standard.md" }
    if ($warn.Count) {
      Write-Warning "sync-agents: Fresh_Workspace_BMAD (living template) has drifted from the lobby front-door pattern:"
      $warn | ForEach-Object { Write-Warning ("  - {0}" -f $_) }
      Write-Warning "  reconcile by hand per the living-template-sync rule (keep generic; placeholders where a real project fills in)."
    } else {
      Write-Host "sync-agents: Fresh living-template check OK (front-door pattern current)."
    }
  }
}

Write-Host "sync-agents: done. (Edit the master .agents/ - never the copies - and re-run to propagate.)"
exit 0
