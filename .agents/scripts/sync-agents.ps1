<#
.SYNOPSIS
  Push the master .agents toolkit into every command surface: the LOBBY's local tool dirs AND the
  machine-global command caches for opencode + Antigravity/Gemini + Codex. (Project targets are retired —
  thin model 2026-08-07, .agents/rules/project-law.md: projects carry tier-2 law only, no vendor.)

.DESCRIPTION
  Single source of authorship = <home>\.agents. The canonical AUTHORING set is .agents\commands\ and it reaches
  ALL FOUR platforms (Claude, opencode, Antigravity/Gemini, Codex) — but Antigravity is reached INDIRECTLY,
  through the generated .agents\workflows\ door, because it truncates a workflow over 12,000 chars instead of
  rejecting it. Both Antigravity surfaces (the repo door and the machine-global cache) mirror workflows\,
  never commands\ (SCC-332). The other three read commands\ verbatim at any size. This copies commands / skills / hooks /
  opencode-agents into the target's .claude and .opencode dirs (Claude /commands + skills + hooks resolve there)
  and, for a LOBBY sync, also refreshes the machine-global caches so opencode, Antigravity, and Codex see the
  same set Claude does.

  THE DOOR MODEL (SCC-66): one door per platform per command. Claude and Codex enter through a LAUNCHER
  SKILL (generated per claude/codex-eligible command into .agents\skills, tree-copied to .claude\skills;
  hand-authored SKILL.md always wins); opencode through its command mirror; Antigravity through its
  workflow mirror. Publishing .claude\commands and ~\.codex\prompts is RETIRED - both double-doored every
  command beside its skill. Codex reads AGENTS.md + .agents\skills natively; the only global pushed for it
  is the bmad-* skills mirror -> ~\.codex\skills (BMAD installs to .claude\skills, which Codex does not read).

  Use -WhatIf (alias -DryRun) to preview every copy, create, and delete action without touching disk.

  PLATFORM REACH. A command may declare its reach with frontmatter `platforms: [claude, opencode, antigravity, codex]`.
  Absent = universal (all four). The sync copies a command only to the platforms it lists, so e.g.
  /cicd-autopilot-claude (claude-only) never lands in the opencode/gemini/codex surfaces.

  PURGE POLICY.
    - Local tool dirs (.claude, .opencode): copy eligible commands; purge only commands that ARE master-managed
      but are no longer eligible for that platform. Files the master doesn't own (a project's own commands) are
      left alone. Hooks / opencode-agents are an additive robocopy (no delete). .claude\skills is additive too,
      but is ALSO manifest-tracked per skill FOLDER — Claude Code turns every SKILL.md into a typeable slash
      command, so a retired skill dir is a command ghost and gets the same ownership-proven purge as a command.
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
    - Project vendoring: RETIRED (thin model, 2026-08-07). A project holds ONLY its own tier-2 law
      (rules\ + skills\ + INDEX.md — .agents/rules/project-law.md); sessions run from the center, so the
      lobby dirs + machine-global caches are the entire sync surface. -Maintained and project -Target now
      exit with an explanatory error instead of vendoring.

  Always edit the master; never hand-edit the copies. Re-run this to propagate changes.

.PARAMETER Target
  Must resolve to the home-base root (the default). Project targets are retired — thin model 2026-08-07.

.PARAMETER GlobalsOnly
  Refresh only the machine-global caches (opencode + Antigravity command caches, Codex prompts, and the Codex
  bmad-* skills mirror) from the lobby master. Skips local tool dirs. /smh-slash-command-updating delegates to this.

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

# Machine home for the global caches. $env:USERPROFILE is WINDOWS-ONLY - on macOS/Linux pwsh it is
# $null, and `Join-Path $null ...` THROWS, which killed the entire global-cache stage (opencode +
# Antigravity + Codex prompts + Codex skills) on the Mac while the local sync above had already
# succeeded, so the run looked mostly fine. Resolve it once, cross-platform.
# (Everything else in this script is separator-safe: PowerShell 7's Join-Path normalises the `\`
# in path literals to `/` on Unix. The `.claude\commands`-style MANIFEST KEYS are deliberately left
# back-slashed - they are dictionary keys, not paths, and must stay byte-identical across machines
# or a manifest written on Windows would stop matching here and skip its retire-purge.)
$UserHome = if ($env:USERPROFILE) { $env:USERPROFILE }
            elseif ($env:HOME)    { $env:HOME }
            else                  { [Environment]::GetFolderPath('UserProfile') }
if (-not $UserHome) { throw "sync-agents: cannot resolve the machine home dir (USERPROFILE/HOME both unset)" }

# -Maintained is RETIRED (thin model, 2026-08-07 — .agents/rules/project-law.md): projects carry no
# vendored toolkit, so there is nothing to fan out to. A plain /sync-agents (lobby + machine-global
# caches) already reaches every platform from any cwd. .agents\maintained-projects.txt lives on as the
# check_maps.py --all LINT worklist only — it no longer drives any sync.
if ($Maintained) {
  Write-Error ("sync-agents: -Maintained is retired (thin model, 2026-08-07). Projects hold only their " +
    "own tier-2 law (rules/ + skills/ + INDEX.md - see .agents/rules/project-law.md); there is no " +
    "per-project vendor to sync. Run /sync-agents with no flags: the lobby + machine-global caches " +
    "serve every session from any cwd. (maintained-projects.txt remains the check_maps --all worklist.)")
  exit 1
}

if (-not $Target) { $Target = $HomeRoot }
$Target   = (Resolve-Path $Target).Path
# Trim BOTH separators: off Windows a trailing '/' survives TrimEnd('\'), and the lobby would then
# compare unequal to itself and silently run the project branch against the master tree.
$IsLobby  = ($Target.TrimEnd('\', '/') -ieq $HomeRoot.TrimEnd('\', '/'))

# Project targets are RETIRED with the same 2026-08-07 thin model: vendoring tier 1 into a project is
# now a rule violation (project-law.md hard stop), so fail LOUD with the why instead of writing files.
if (-not $IsLobby) {
  Write-Error ("sync-agents: project targets are retired (thin model, 2026-08-07). '$Target' must not " +
    "carry the tier-1 toolkit - a project holds only its own rules/ + skills/ + INDEX.md " +
    "(.agents/rules/project-law.md). Run /sync-agents with no target: the lobby + machine-global " +
    "caches serve every session, from any cwd.")
  exit 1
}

# 'zoo' is Zoo Code (ZooCodeOrganization.zoo-code), the coordinated community continuation of the
# archived Roo Code (SCC-349). It deliberately keeps the .roo/* paths and settings shapes; its doors
# are generated by Sync-ZooSurfaces below and TRACKED in git (they travel to both machines).
$AllPlatforms = @('claude','opencode','antigravity','codex','zoo')

# --- helpers ------------------------------------------------------------------

# Is this path, or any directory above it inside $Root, excluded? Mirrors robocopy's /XD /XF, which match
# by NAME anywhere in the tree; an /XD entry given as an absolute path is honoured as that exact directory
# (the .agents vendor passes `<master>\bmad` that way).
function Test-TreeExcluded {
  param([string]$Full, [string]$Root, [bool]$IsDir, [string[]]$DirNames, [string[]]$DirPaths, [string[]]$FileNames)
  if ((-not $IsDir) -and ($FileNames -contains (Split-Path $Full -Leaf))) { return $true }
  $probe = if ($IsDir) { $Full } else { Split-Path $Full -Parent }
  while ($probe -and ($probe.Length -gt $Root.Length)) {
    if ($DirNames -contains (Split-Path $probe -Leaf)) { return $true }
    if ($DirPaths -contains $probe) { return $true }
    $probe = Split-Path $probe -Parent
  }
  return $false
}

# Cross-platform tree copy. robocopy is WINDOWS-ONLY, and on macOS/Linux these call sites aborted the run
# mid-way instead of degrading - the Mac's first /sync-agents died after creating exactly one codex skill
# dir, leaving a half-built cache that looked deliberate. Windows keeps robocopy VERBATIM (the proven path
# on the primary machines); every other platform takes the PowerShell-native equivalent below. Semantics
# both sides implement:
#   -Mirror off (robocopy /E)  : additive - copy the tree, never delete anything already at the target
#   -Mirror on  (robocopy /MIR): additive PLUS delete target entries the source no longer has
# Excluded paths are skipped on BOTH passes, so -Mirror never deletes an excluded dir at the target either
# (robocopy /MIR /XD behaves the same way: an excluded dir is out of scope, not "extra").
function Copy-Tree {
  param([string]$Src, [string]$Dst, [string[]]$ExcludeDirs, [string[]]$ExcludeFiles, [switch]$Mirror)
  $xd = @(@($ExcludeDirs)  | Where-Object { $_ })
  $xf = @(@($ExcludeFiles) | Where-Object { $_ })

  if ($IsWindows) {
    New-Item -ItemType Directory -Force -Path $Dst | Out-Null
    $mode = if ($Mirror) { '/MIR' } else { '/E' }
    if ($xf) { robocopy $Src $Dst $mode /XD @xd /XF @xf /NFL /NDL /NJH /NJS /NC /NS | Out-Null }
    else     { robocopy $Src $Dst $mode /XD @xd          /NFL /NDL /NJH /NJS /NC /NS | Out-Null }
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($Src -> $Dst), rc=$LASTEXITCODE" }
    return
  }

  $srcRoot  = (Resolve-Path -LiteralPath $Src).Path
  $dirNames = @($xd | Where-Object { -not [IO.Path]::IsPathRooted($_) })
  $dirPaths = @($xd | Where-Object { [IO.Path]::IsPathRooted($_) } |
                ForEach-Object { $r = Resolve-Path -LiteralPath $_ -ErrorAction SilentlyContinue; if ($r) { $r.Path } })
  New-Item -ItemType Directory -Force -Path $Dst | Out-Null
  $dstRoot = (Resolve-Path -LiteralPath $Dst).Path

  # -Force: on Unix a dot-file is "hidden", and without it every .gitkeep / .env.example would be skipped.
  $kept = New-Object 'System.Collections.Generic.HashSet[string]'
  foreach ($item in Get-ChildItem -LiteralPath $srcRoot -Recurse -Force -ErrorAction SilentlyContinue) {
    if (Test-TreeExcluded $item.FullName $srcRoot $item.PSIsContainer $dirNames $dirPaths $xf) { continue }
    $rel = $item.FullName.Substring($srcRoot.Length).TrimStart([char]'/', [char]'\')
    [void]$kept.Add($rel)
    $target = Join-Path $dstRoot $rel
    if ($item.PSIsContainer) {
      New-Item -ItemType Directory -Force -Path $target | Out-Null
    } else {
      $parent = Split-Path $target -Parent
      if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
      Copy-Item -LiteralPath $item.FullName -Destination $target -Force
    }
  }

  if (-not $Mirror) { return }
  # Deepest-first, so a directory is only removed after its own contents have been considered.
  $extra = @(Get-ChildItem -LiteralPath $dstRoot -Recurse -Force -ErrorAction SilentlyContinue |
             Sort-Object { $_.FullName.Length } -Descending)
  foreach ($item in $extra) {
    if (-not (Test-Path -LiteralPath $item.FullName)) { continue }   # already gone with its parent
    if (Test-TreeExcluded $item.FullName $dstRoot $item.PSIsContainer $dirNames $dirPaths $xf) { continue }
    $rel = $item.FullName.Substring($dstRoot.Length).TrimStart([char]'/', [char]'\')
    if (-not $kept.Contains($rel)) { Remove-Item -LiteralPath $item.FullName -Recurse -Force }
  }
}

function Sync-Dir($src, $dst, [string[]]$ExcludeDirs, [string[]]$ExcludeFiles, [switch]$WhatIf) {
  if (-not (Test-Path $src)) { return }
  # __pycache__ alongside node_modules: .pyc names embed the interpreter version (cpython-314 here,
  # something else on the Windows box), so vendoring them churns the TRACKED manifest every time a
  # different machine syncs — and they are regenerable caches no project should carry.
  $xd = @('node_modules', '__pycache__') + (@($ExcludeDirs) | Where-Object { $_ })
  $xf = @(@($ExcludeFiles) | Where-Object { $_ })
  if (-not $WhatIf) {
    Copy-Tree $src $dst $xd $xf
  } else {
    Write-Host ("WHATIF: would copy tree '{0}' -> '{1}' (excluding: {2})" -f $src,$dst,($xd -join ', '))
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

function ConvertTo-ManifestString([string]$s) {
  # Back-slash FIRST or the escapes we add get re-escaped. Manifest strings are path keys and file names.
  $e = $s.Replace('\','\\').Replace('"','\"').Replace("`r",'\r').Replace("`n",'\n').Replace("`t",'\t')
  return '"' + $e + '"'
}

# The manifest is TRACKED, so its bytes are a diff every machine reads. `ConvertTo-Json` cannot own them:
# Windows PowerShell 5.1 and pwsh 7 serialise differently (5.1 emits a BOM and its own spacing -
# `"version":  1` with two spaces), so the file rewrote ENTIRELY the first time it was generated on the
# Mac - 250 lines of pure formatting churn burying the one line that carries meaning, and a guaranteed
# conflict every time the two machines sync in turn. Emitting it by hand makes both engines write the
# same bytes: fixed key order, sorted arrays, 2-space indent, LF, no BOM. Sorting is safe - every reader
# tests membership (`-notcontains`), never position.
function Save-SyncManifest([string]$target, $manifest, [switch]$WhatIf) {
  $p = Join-Path $target ".agents\$ManifestName"
  if ($WhatIf) { Write-Host ("WHATIF: would write sync manifest '{0}'" -f $p); return }
  New-Item -ItemType Directory -Force -Path (Split-Path $p -Parent) | Out-Null

  $note  = 'Generated by sync-agents.ps1. Records what the sync wrote so the next run can purge its own retired files. Do not hand-edit.'
  $lines = New-Object 'System.Collections.Generic.List[string]'
  $lines.Add('{')
  $lines.Add('  "version": 1,')
  $lines.Add('  "generated": ' + (ConvertTo-ManifestString ((Get-Date).ToString('s'))) + ',')
  $lines.Add('  "note": ' + (ConvertTo-ManifestString $note) + ',')

  # An array as `[]` when empty, else one entry per line - matching what ConvertTo-Json produced, so this
  # change alone does not re-churn the file on top of the format switch.
  $emit = {
    param([string]$label, [string[]]$items, [string]$indent, [string]$tail)
    $vals = @(@($items) | Where-Object { $_ } | Sort-Object)
    if (-not $vals.Count) { $lines.Add("$indent$label[]$tail"); return }
    $lines.Add("$indent$label[")
    for ($i = 0; $i -lt $vals.Count; $i++) {
      $comma = if ($i -lt $vals.Count - 1) { ',' } else { '' }
      $lines.Add("$indent  " + (ConvertTo-ManifestString $vals[$i]) + $comma)
    }
    $lines.Add("$indent]$tail")
  }

  & $emit '"vendor": ' @($manifest.vendor) '  ' ','
  $keys = @($manifest.local.Keys | Sort-Object)
  if (-not $keys.Count) {
    $lines.Add('  "local": {}')
  } else {
    $lines.Add('  "local": {')
    for ($k = 0; $k -lt $keys.Count; $k++) {
      $tail = if ($k -lt $keys.Count - 1) { ',' } else { '' }
      & $emit ((ConvertTo-ManifestString $keys[$k]) + ': ') @($manifest.local[$keys[$k]]) '    ' $tail
    }
    $lines.Add('  }')
  }
  $lines.Add('}')

  # WriteAllText, not Set-Content: -Encoding utf8 means "with BOM" on 5.1 and "without" on 7, and
  # Set-Content would also stamp the platform's line ending on every line.
  [IO.File]::WriteAllText($p, (($lines -join "`n") + "`n"), (New-Object Text.UTF8Encoding($false)))
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
#
# ⛔ SEPARATORS ARE LOAD-BEARING HERE — this set is compared against the TRACKED manifest, which every
# machine shares. Windows produces `commands\analyst.md`; an unnormalised macOS run produces
# `/commands/analyst.md`, and the two sets then have ZERO overlap. Invoke-ManifestPurge reads that as
# "the master dropped every file it ever owned" and deletes the entire vendored toolkit — ~570 files per
# project — while Join-Path still happily resolves the back-slashed manifest paths on macOS, so every
# delete succeeds and the run reports itself as a normal purge. Emit BACK-slashed, leading-separator-free
# paths on every OS so the manifest stays byte-comparable across machines.
# (Get-VendorFileSet deleted 2026-08-07 with the project-vendor path — thin model, project-law.md.
#  It had just gained a `jira.conf` exclusion (SCC-10) to stop the vendor overwriting each repo's Jira
#  identity. Deleting the vendor makes that exclusion moot — nothing copies into a project at all — and
#  supersedes it with the stronger guarantee. `jira.conf`, `.githooks/`, and `.agents/scripts/git-hooks/`
#  are repo-local ENFORCEMENT: git runs hooks in the repo they gate, so they live there permanently and
#  are never centralized. Same class as BMAD's `_bmad/custom/*.toml`.)

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

# Directory variant of the above, for a surface whose UNIT IS A FOLDER rather than a file: .claude\skills holds
# one dir per skill, and Claude Code publishes a typeable slash command for every SKILL.md it finds there. Same
# ownership rule, so it is exactly as safe — only a NAME a previous run recorded writing is ever removed, which
# leaves project-authored skills and BMAD's own installs structurally unreachable.
function Invoke-ManifestPurgeDir([string]$dst, [string[]]$was, [string[]]$now, [switch]$WhatIf) {
  $purged = @()
  foreach ($rel in @($was | Where-Object { $_ -and ($now -notcontains $_) })) {
    $d = Join-Path $dst $rel
    if (-not (Test-Path $d)) { continue }
    if ($WhatIf) { Write-Host ("WHATIF: would purge retired skill dir '{0}' (master no longer owns it)" -f $d) }
    else         { Remove-Item $d -Recurse -Force }
    $purged += $rel
  }
  return $purged
}

# Top-level skill folder names a sync places into a .claude\skills copy — the same set Sync-Dir writes, so the
# manifest records precisely what was copied. bmad-* is BMAD's own install: never ours to record, never ours to
# purge (mirrors Sync-Dir's exclude at the call site).
function Get-SkillDirSet([string]$skillSrc) {
  if (-not (Test-Path $skillSrc)) { return @() }
  return ,@(Get-ChildItem $skillSrc -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -notlike 'bmad-*' } |
            Select-Object -ExpandProperty Name)
}

# Remove directories left empty by a purge. A manifest purge deletes FILES, so retiring a skill emptied its
# folder but left the folder itself behind — harmless in .agents\, but it reads as drift and it is the shell a
# ghost re-grows in. Only prunes dirs that are empty all the way down, so it can never remove real content.
function Remove-EmptyDirs([string]$root, [switch]$WhatIf) {
  if (-not (Test-Path $root)) { return 0 }
  $n = 0
  # Deepest-first, so a parent emptied by its children's removal is itself collected on the same pass.
  foreach ($d in @(Get-ChildItem $root -Directory -Recurse -Force -ErrorAction SilentlyContinue |
                   Sort-Object { $_.FullName.Length } -Descending)) {
    if (@(Get-ChildItem $d.FullName -Force -ErrorAction SilentlyContinue).Count) { continue }
    if ($WhatIf) { Write-Host ("WHATIF: would prune empty dir '{0}'" -f $d.FullName) }
    else         { Remove-Item $d.FullName -Force -ErrorAction SilentlyContinue }
    $n++
  }
  return $n
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
  # -SkipAP: robot-lane commands (*-AP.md — invoked by the autopilot engines, never typed by a human) are
  # vendored ONLY into project tool dirs (the engines Push-Location into the project and resolve them there).
  # The lobby's typeable menus and the machine-global caches skip them; the purge branch below then removes
  # any stale copies automatically on every sync.
  param([string]$MasterCmdDir, [string]$Dst, [string]$Platform, [switch]$Mirror, [switch]$SkipAP, [switch]$WhatIf)
  New-Item -ItemType Directory -Force -Path $Dst | Out-Null
  $masterFiles = Get-ChildItem -Path $MasterCmdDir -Filter '*.md' -File
  $masterNames = @($masterFiles | Select-Object -ExpandProperty Name)
  $eligible = @()
  foreach ($f in $masterFiles) {
    if ($SkipAP -and ($f.Name -match '-AP\.md$')) { continue }
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

# Mirror the antigravity-eligible commands into .agents/workflows/ so ANTIGRAVITY sees them. Antigravity
# surfaces / from workflows/ (+ skills/), never commands/ (a Claude/opencode concept). The flow is authored
# as commands; copy the eligible ones into workflows/ VERBATIM (frontmatter stays line 1 -- no injected
# header) so the same / works in every tool from ONE source. Generated copies, regenerated every sync --
# edit the command, not these.
# THE GATE IS `platforms:`, NOT THE FILENAME (SCC-56, 2026-08-09). This used to filter by NAME first
# ($allowed = sudo-*, 1_*, new-project, slash_command_updating) and only then consult Get-CommandPlatforms,
# so a command's DECLARED reach was never read unless its filename happened to match. Four commands that
# claim Antigravity reached it zero times: close-task-merge-tree, sync-agents, review,
# and clean-code-audit -- which declares `platforms: [opencode, antigravity]` in the documented mechanism
# and was dropped anyway. The name filter was ALSO redundant: its stated reason was keeping BMAD personas
# and 1_* workflows out of the / menu, but every persona and testarch-* wrapper already declares
# `platforms: [opencode]` (so Get-CommandPlatforms excludes them unaided) and no 1_*.md command has existed
# for some time. It blocked nothing it was written to block. Now: absent/empty `platforms:` == universal ==
# mirrored; `platforms: []` == nowhere; -AP stays claude-only by name convention.
# BIG COMMANDS (2026-07-25): a command over ~11.5 KB gets a GENERATED THIN LAUNCHER instead of a verbatim
# copy -- Antigravity does not honour a workflow over its 12,000-char cap, and hand-trimmed twins drifted and
# needed byte-golf on every edit. The launcher points the agent at .agents/commands/<name>.md (the single
# source of truth), so the command can grow freely and no workflow can ever hit the cap again. Same pattern
# as the hand-authored smh-adviser-board launcher, now automatic.
# WHAT OVER-CAP ACTUALLY DOES (measured, SCC-135 -- this was previously written here as "silently drops"):
# Antigravity TRUNCATES at 12,000 chars, it does not reject the file. smh-update-maps-indexes shipped a
# 39,594-char body and the agent received the header, the target list, Step 0 and half of Step 0.5 -- cut
# mid-sentence -- then improvised the remaining 70%, including past the Step 4 approval gate it never saw.
# That is the important distinction: a dropped workflow fails visibly, a truncated one runs and looks fine.
# ── SCC-195 · THE ANTIGRAVITY DESCRIPTION BUDGET ───────────────────────────────────────────────
# Antigravity builds its slash-command menu from the `description:` frontmatter of every
# .agents/workflows/*.md. This repo's descriptions run 400-950+ chars (they are written for an agent
# reading the command, not for a menu), and the TOTAL blew the menu's context budget: 15 workflows
# were dropped from the agent's command list outright.
#
# ⛔ Shortening them BY HAND in workflows/ cannot work, twice over: these files are GENERATED, so the
# next sync overwrites them; and test_command_surfaces.py's door-parity check demands a mirror be
# byte-identical to its brain (or a launcher whose description EQUALS the brain's), so a hand-edited
# door reads as `stale` and main-write-gate goes red. So the rule lives HERE, in the generator, and
# the parity check learned the same rule: truncated-from-the-brain IS parity on this surface.
#
# ⚠ TWO IMPLEMENTATIONS OF ONE RULE (this, and `ag_description` in test_command_surfaces.py). That is
# the same shape as Get-CommandPlatforms vs platforms_declared, and it is checked rather than
# trusted: if the two ever disagree the door reads `stale` and the test names the file.
# `-ge 0` on LastIndexOf, not `-gt 0`, so a leading-space description cuts identically on both sides.
function Get-AgDescription {
  param([string]$Desc)
  if ($null -eq $Desc) { return '' }
  if ($Desc.Length -le 135) { return $Desc }
  $cut = $Desc.Substring(0, 132)
  $i = $cut.LastIndexOf(' ')
  if ($i -ge 0) { $cut = $cut.Substring(0, $i) }
  return $cut.TrimEnd(' ', ',', ';', ':', '-') + '...'
}

# The brain with ONLY its description line replaced by the budgeted one, byte-for-byte otherwise.
# Every command file under .agents/commands is LF and BOM-less except the eight testarch-* bridges,
# which declare `platforms: [opencode]` and so never reach this surface (verified 2026-08-17).
function Set-AgDescriptionLine {
  param([string]$Raw)
  # (\r?) is captured and PUT BACK. `.` matches CR in .NET, `$` in multiline matches before the
  # LF, so on a CRLF brain the CR landed inside group 1, TrimEnd() ate it, and the rewritten
  # line shipped LF-only among CRLF siblings -- a mixed-ending file from a pure text edit.
  # No brain is CRLF today (all LF, BOM-less); this is the writer not being the thing that
  # introduces one. The Python twin in test_command_surfaces.py does the same.
  $m = [regex]::Match($Raw, '(?m)^description:[ \t]*(.*?)(\r?)$')
  if (-not $m.Success) { return $Raw }
  $short = Get-AgDescription $m.Groups[1].Value.TrimEnd()
  if ($short -eq $m.Groups[1].Value) { return $Raw }
  return $Raw.Remove($m.Index, $m.Length).Insert($m.Index, ('description: ' + $short + $m.Groups[2].Value))
}

function Sync-AntigravityWorkflowMirror {
  param([string]$MasterDir, [switch]$WhatIf)
  $cmdDir = Join-Path $MasterDir "commands"
  $wfDir  = Join-Path $MasterDir "workflows"
  if (-not $WhatIf) { New-Item -ItemType Directory -Force -Path $wfDir | Out-Null } else { Write-Host "WHATIF: would ensure dir '$wfDir'" }
  $mirrored = @()

  # HAND-OWNED files in workflows/: never written by this mirror, never pruned by it. Each has a reason.
  #   smh-adviser-board.md   - hand-authored thin launcher (the command is 19.8k, over AG's 12k cap).
  #   INDEX.md               - the workflows router. It has NO frontmatter and NO source in commands/, and
  #                            survived only because it failed the old name filter. With that filter gone
  #                            the prune below would DELETE it on the next sync. Load-bearing guard.
  # smh-update-maps-indexes.md was here until SCC-135. It was the ONLY command whose body lived in
  # workflows/ while commands/ held a wrapper, and this exclusion is what exempted it from the launcher
  # rule below -- so its 39.6k body shipped to Antigravity and was TRUNCATED at 12,000 chars, losing 70%
  # of the steps including the Step 4 approval gate. Un-inverted: the body is now the command, and this
  # function generates its launcher like every other big command. Do not re-add it.
  $excluded = @('smh-adviser-board.md', 'INDEX.md')

  $files = Get-ChildItem -Path $cmdDir -Filter '*.md' -File |
    Where-Object { $excluded -notcontains $_.Name }

  foreach ($f in $files) {
    if (($f.Name -notmatch '-AP\.md$') -and ((Get-CommandPlatforms $f.FullName) -contains 'antigravity')) {
      $dest = Join-Path $wfDir $f.Name
      if ((Get-Item $f.FullName).Length -gt 11500) {
        # Over (or near) the 12k cap: emit a generated launcher, never a doomed verbatim copy.
        $desc = ''
        foreach ($line in (Get-Content $f.FullName -TotalCount 30 -Encoding UTF8)) {
          if ($line -match '^description:\s*(.+)$') { $desc = $Matches[1]; break }
        }
        # Stub literals are ASCII-only on purpose: PS 5.1 parses a BOM-less .ps1 as ANSI, which would
        # mangle any non-ASCII literal here into mojibake in every generated file.
        $stub = @(
          '---',
          ('description: ' + (Get-AgDescription $desc)),
          'platforms: [opencode, antigravity]',
          '---',
          '',
          ('# /' + $f.BaseName + ' - launcher (GENERATED by sync-agents; do not edit)'),
          '',
          '**THIN LAUNCHER - carries NO steps of its own.** Generated because the command body exceeds',
          "Antigravity's 12,000-char workflow cap. A verbatim mirror would be TRUNCATED at the cap, not",
          'rejected, so the agent would run on partial steps and look like it worked. Regenerated every sync.',
          '',
          ('**Execute now:** read `' + '.agents/commands/' + $f.Name + '` (relative to the repo root of the'),
          'workspace you are in) and follow it **END TO END**, passing any arguments through verbatim. If that',
          'file does not exist in this workspace, STOP and tell the operator - never improvise the flow from memory.',
          ''
        ) -join "`n"
        if (-not $WhatIf) {
          # Explicit UTF-8 WITHOUT BOM - frontmatter '---' must stay byte 0 for the workflow parser
          [IO.File]::WriteAllText($dest, $stub, (New-Object Text.UTF8Encoding($false)))
        } else {
          Write-Host ("WHATIF: would emit LAUNCHER for '{0}' (command over 11.5 KB) -> workflows/" -f $f.Name)
        }
      } else {
        # Under the size cap: a verbatim mirror, EXCEPT that the description is cut to the menu
        # budget (SCC-195). Untouched when it already fits, so most files still copy byte-for-byte.
        $raw = [IO.File]::ReadAllText($f.FullName)
        $out = Set-AgDescriptionLine $raw
        if (-not $WhatIf) {
          if ($out -eq $raw) {
            Copy-Item -Path $f.FullName -Destination $dest -Force
          } else {
            [IO.File]::WriteAllText($dest, $out, (New-Object Text.UTF8Encoding($false)))
          }
        } else {
          Write-Host ("WHATIF: would mirror '{0}' -> workflows/' for antigravity{1}" -f `
                      $f.FullName, $(if ($out -ne $raw) { ' (description cut to the menu budget)' } else { '' }))
        }
      }
      $mirrored += $f.Name
    }
  }
  # Prune stale generated mirrors: anything in workflows/ that is NO LONGER mirrored and is not hand-owned.
  # This is now the ONLY thing standing between workflows/ and a stale twin, so $excluded above is the whole
  # safety list -- a file that belongs in workflows/ without a commands/ source MUST be named there.
  $stale = Get-ChildItem -Path $wfDir -Filter '*.md' -File -ErrorAction SilentlyContinue |
    Where-Object { ($excluded -notcontains $_.Name) -and ($mirrored -notcontains $_.Name) }


  if (-not $WhatIf) {
    $stale | ForEach-Object { Remove-Item $_.FullName -Force }
  } else {
    $stale | ForEach-Object { Write-Host ("WHATIF: would delete stale mirror '{0}' from workflows/'" -f $_.Name) }
  }
  return $mirrored
}

# One launcher-skill body, shared by the master emit and the claude-only cache emit. ASCII-only literals
# (same reason as the Antigravity stubs: PS 5.1 would mangle non-ASCII into mojibake in every generated
# file). The marker line is the ownership record: a SKILL.md WITHOUT it is hand-authored and this script
# never overwrites or prunes it.
function New-LauncherSkillStub {
  param([System.IO.FileInfo]$CommandFile)
  $desc = ''
  foreach ($line in (Get-Content $CommandFile.FullName -TotalCount 30 -Encoding UTF8)) {
    if ($line -match '^description:\s*(.+)$') { $desc = $Matches[1]; break }
  }
  if (-not $desc) {
    $desc = ('Launcher for /' + $CommandFile.BaseName + ' - reads .agents/commands/' +
             $CommandFile.Name + ' and follows it end to end.')
  }
  return @(
    '---',
    ('name: ' + $CommandFile.BaseName),
    ('description: ' + $desc),
    '---',
    '',
    ('# /' + $CommandFile.BaseName + ' - launcher (GENERATED by sync-agents; do not edit)'),
    '',
    '**THIN LAUNCHER - carries NO steps of its own.** The single source of truth is the command body;',
    'this skill exists so the same / works in Claude and Codex, whose menus read skills, not commands.',
    'Regenerated every sync - edit the command, not this file.',
    '',
    ('**Execute now:** read `' + '.agents/commands/' + $CommandFile.Name + '` (relative to the repo root of'),
    'the workspace you are in) and follow it **END TO END**, passing any arguments through verbatim. If',
    'that file does not exist in this workspace, STOP and tell the operator - never improvise the flow',
    'from memory.',
    ''
  ) -join "`n"
}

# THE DOOR MODEL (SCC-66): one door per platform per command.
#   claude      -> a launcher skill (Claude's menu reads .claude\skills; every SKILL.md is a typeable /command)
#   codex       -> the SAME launcher skill, read natively from .agents\skills
#   opencode    -> the command mirror in .opencode\commands (unchanged)
#   antigravity -> the workflow mirror in .agents\workflows (unchanged)
# Publishing commands into .claude\commands and ~/.codex/prompts is RETIRED - both double-doored every
# command beside its skill. This stage generates the skill door for every claude/codex-eligible command:
#   - eligible = `platforms:` includes claude or codex (absent = universal = eligible); -AP robot lane skipped;
#   - a HAND-AUTHORED SKILL.md (no GENERATED marker) always wins - it already IS the door; never overwritten;
#   - claude-ONLY commands are NOT emitted here: .agents\skills is Codex-visible by definition, so their
#     launcher goes straight into the .claude\skills cache at the local stage instead;
#   - stale GENERATED launchers (command deleted / renamed / no longer eligible) are pruned; hand skills never.
function Sync-LauncherSkills {
  param([string]$MasterDir, [switch]$WhatIf)
  $cmdDir = Join-Path $MasterDir 'commands'
  $skDir  = Join-Path $MasterDir 'skills'
  if (-not $WhatIf) { New-Item -ItemType Directory -Force -Path $skDir | Out-Null }
  $made = @()
  foreach ($f in (Get-ChildItem -Path $cmdDir -Filter '*.md' -File)) {
    if ($f.Name -match '-AP\.md$') { continue }
    $pl = Get-CommandPlatforms $f.FullName
    if (-not (($pl -contains 'claude') -or ($pl -contains 'codex'))) { continue }
    if (($pl -contains 'claude') -and -not ($pl -contains 'codex')) { continue }
    $dstDir    = Join-Path $skDir $f.BaseName
    $skillFile = Join-Path $dstDir 'SKILL.md'
    if ((Test-Path $skillFile) -and ((Get-Content $skillFile -Raw) -notmatch 'GENERATED by sync-agents')) {
      continue
    }
    if (-not $WhatIf) {
      New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
      [IO.File]::WriteAllText($skillFile, (New-LauncherSkillStub $f), (New-Object Text.UTF8Encoding($false)))
    } else {
      Write-Host ("WHATIF: would emit launcher skill '{0}' -> .agents/skills/" -f $f.BaseName)
    }
    $made += $f.BaseName
  }
  # Prune stale GENERATED launchers. Only a SKILL.md carrying the marker is a candidate - hand-authored
  # skills (knowledge skills, the rich cicd-*/smh-* launchers) are structurally unreachable here.
  foreach ($d in @(Get-ChildItem -Path $skDir -Directory -ErrorAction SilentlyContinue)) {
    if ($made -contains $d.Name) { continue }
    $sf = Join-Path $d.FullName 'SKILL.md'
    if (-not (Test-Path $sf)) { continue }
    if ((Get-Content $sf -Raw) -match 'GENERATED by sync-agents') {
      if ($WhatIf) { Write-Host ("WHATIF: would prune stale generated skill '{0}'" -f $d.Name) }
      else         { Remove-Item $d.FullName -Recurse -Force }
    }
  }
  return ,$made
}

# ZOO CODE SURFACES (SCC-349). Zoo's three doors, all generated, all TRACKED in git:
#   .roo/commands/<name>.md  - one thin launcher per zoo-eligible command (same door model as every
#                              other platform: the command body stays the single source of truth);
#   .roomodes                - the six BMAD personas as custom modes, each pointing at its persona
#                              command master; per-mode rules in .roo/rules-<slug>/;
#   .roo/rules/*.md          - Zoo injects EVERY file here into EVERY prompt, so the three FLOOR
#                              rules are copied in (generated header) - the always-on tier becomes
#                              mechanical in Zoo instead of depending on the agent following the
#                              AGENTS.md pointer chain (SCC-346 Part F).
# Generated launchers carry the GENERATED marker and are pruned when their source retires - same
# contract as the Antigravity workflow mirror. Hand-authored files without the marker are never
# touched. ASCII-only literals (PS 5.1 would mangle non-ASCII into mojibake in every generated file).
function Sync-ZooSurfaces {
  param([string]$MasterDir, [string]$RepoRoot, [switch]$WhatIf)
  $cmdDir   = Join-Path $MasterDir 'commands'
  $ruleDir  = Join-Path $MasterDir 'rules'
  $rooCmd   = Join-Path $RepoRoot '.roo\commands'
  $rooRules = Join-Path $RepoRoot '.roo\rules'
  if (-not $WhatIf) {
    New-Item -ItemType Directory -Force -Path $rooCmd | Out-Null
    New-Item -ItemType Directory -Force -Path $rooRules | Out-Null
  }

  # 1) command launchers
  $made = @()
  foreach ($f in (Get-ChildItem -Path $cmdDir -Filter '*.md' -File)) {
    if ($f.Name -match '-AP\.md$') { continue }
    if (-not ((Get-CommandPlatforms $f.FullName) -contains 'zoo')) { continue }
    $desc = ''
    foreach ($line in (Get-Content $f.FullName -TotalCount 30 -Encoding UTF8)) {
      if ($line -match '^description:\s*(.+)$') { $desc = $Matches[1]; break }
    }
    $stub = @(
      '---',
      ('description: ' + (Get-AgDescription $desc)),
      '---',
      '',
      ('# /' + $f.BaseName + ' - launcher (GENERATED by sync-agents; do not edit)'),
      '',
      '**THIN LAUNCHER - carries NO steps of its own.** The single source of truth is the command body;',
      'this file exists so the same / works in Zoo Code, whose menu reads .roo/commands. Regenerated',
      'every sync - edit the command, not this file.',
      '',
      ('**Execute now:** read `' + '.agents/commands/' + $f.Name + '` (relative to the repo root of the'),
      'workspace you are in) and follow it **END TO END**, passing any arguments through verbatim. If',
      'that file does not exist in this workspace, STOP and tell the operator - never improvise the',
      'flow from memory.',
      ''
    ) -join "`n"
    if (-not $WhatIf) {
      [IO.File]::WriteAllText((Join-Path $rooCmd $f.Name), $stub, (New-Object Text.UTF8Encoding($false)))
    } else {
      Write-Host ("WHATIF: would emit zoo launcher '{0}' -> .roo/commands/" -f $f.Name)
    }
    $made += $f.Name
  }
  # Prune stale GENERATED launchers only - a hand-authored file here is not ours to delete.
  foreach ($g in @(Get-ChildItem -Path $rooCmd -Filter '*.md' -File -ErrorAction SilentlyContinue)) {
    if ($made -contains $g.Name) { continue }
    if ((Get-Content $g.FullName -Raw) -match 'GENERATED by sync-agents') {
      if ($WhatIf) { Write-Host ("WHATIF: would prune stale zoo launcher '{0}'" -f $g.Name) }
      else         { Remove-Item $g.FullName -Force }
    }
  }

  # 2) FLOOR rules -> .roo/rules/ (the always-on tier, injected by Zoo into every prompt)
  $floor = @('operator-profile.md', 'constitution.md', 'karpathy-guidelines.md')
  foreach ($rn in $floor) {
    $srcF = Join-Path $ruleDir $rn
    if (-not (Test-Path $srcF)) { Write-Warning ("sync-agents: zoo floor rule MISSING in master: '{0}'" -f $rn); continue }
    $body = ('<!-- GENERATED by sync-agents from .agents/rules/' + $rn +
             ' - edit the master, never this copy -->') + "`n" + [IO.File]::ReadAllText($srcF)
    if (-not $WhatIf) {
      [IO.File]::WriteAllText((Join-Path $rooRules $rn), $body, (New-Object Text.UTF8Encoding($false)))
    } else {
      Write-Host ("WHATIF: would copy floor rule '{0}' -> .roo/rules/" -f $rn)
    }
  }

  # 3) .roomodes - six BMAD personas as custom modes; per-mode rules in .roo/rules-<slug>/
  $personas = @(
    @{ Slug = 'analyst';     Name = 'BMAD Analyst (Mary)' },
    @{ Slug = 'architect';   Name = 'BMAD Architect (Winston)' },
    @{ Slug = 'dev';         Name = 'BMAD Dev (James)' },
    @{ Slug = 'pm';          Name = 'BMAD PM (John)' },
    @{ Slug = 'tech-writer'; Name = 'BMAD Tech Writer (Paige)' },
    @{ Slug = 'ux-designer'; Name = 'BMAD UX Designer (Sally)' }
  )
  $yaml = @('# GENERATED by sync-agents (SCC-349; do not edit - edit .agents/commands/<slug>.md).',
            '# Six BMAD personas as Zoo Code custom modes. Per-mode rules live in .roo/rules-<slug>/.',
            'customModes:')
  foreach ($p in $personas) {
    $src = Join-Path $cmdDir ($p.Slug + '.md')
    $desc = ''
    if (Test-Path $src) {
      foreach ($line in (Get-Content $src -TotalCount 10 -Encoding UTF8)) {
        if ($line -match '^description:\s*(.+)$') { $desc = $Matches[1]; break }
      }
    }
    $yaml += ('  - slug: ' + $p.Slug)
    $yaml += ('    name: ' + $p.Name)
    $yaml += '    roleDefinition: >-'
    $yaml += ('      You are the ' + $p.Name + ' persona. Read .agents/commands/' + $p.Slug + '.md')
    $yaml += ('      (repo root) and follow it END TO END - it activates the bmad-agent-' + $p.Slug)
    $yaml += '      skill with its full ritual. AGENTS.md is the front door; never improvise the persona.'
    $yaml += '    whenToUse: >-'
    $yaml += ('      ' + (Get-AgDescription $desc))
    $yaml += '    groups:'
    $yaml += '      - read'
    $yaml += '      - edit'
    $yaml += '      - command'
    $modeDir = Join-Path $RepoRoot ('.roo\rules-' + $p.Slug)
    $modeRule = @(
      ('<!-- GENERATED by sync-agents (SCC-349; do not edit). -->'),
      ('# ' + $p.Name + ' - mode rule'),
      '',
      ('Read `.agents/commands/' + $p.Slug + '.md` (repo root) and follow it end to end. The'),
      'three floor rules in `.roo/rules/` bind this mode like every other; `AGENTS.md` is the',
      'front door and single source of truth for how to act in this repo.',
      ''
    ) -join "`n"
    if (-not $WhatIf) {
      New-Item -ItemType Directory -Force -Path $modeDir | Out-Null
      [IO.File]::WriteAllText((Join-Path $modeDir '01-persona.md'), $modeRule, (New-Object Text.UTF8Encoding($false)))
    } else {
      Write-Host ("WHATIF: would emit mode rule for '{0}' -> .roo/rules-{0}/" -f $p.Slug)
    }
  }
  $roomodesPath = Join-Path $RepoRoot '.roomodes'
  if (-not $WhatIf) {
    [IO.File]::WriteAllText($roomodesPath, (($yaml -join "`n") + "`n"), (New-Object Text.UTF8Encoding($false)))
  } else {
    Write-Host ("WHATIF: would write .roomodes with {0} modes" -f $personas.Count)
  }
  return ,$made
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
      Copy-Tree $s.FullName $tgt @('node_modules') @() -Mirror
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
# the (additive) .agents vendor. This also runs BEFORE the machine-global block below, which mirrors this
# same workflows/ dir into the Antigravity cache (SCC-332) - so that cache is always built from a fresh
# door set. Do NOT move this call below the globals block. The opencode cache still mirrors commands/.
$agWf = Sync-AntigravityWorkflowMirror $Master -WhatIf:$WhatIf
Write-Host "sync-agents: antigravity workflow mirror -> $($agWf.Count) commands in .agents/workflows/"

# Regenerate the Claude+Codex skill doors in the master BEFORE the local copy stage picks them up.
$genSk = Sync-LauncherSkills $Master -WhatIf:$WhatIf
Write-Host "sync-agents: launcher skills -> $($genSk.Count) generated in .agents/skills/ (hand-authored skills untouched)"

# Zoo Code doors (SCC-349): tracked in-repo like the workflow mirror, so they travel via git.
$zooCmds = Sync-ZooSurfaces $Master $HomeRoot -WhatIf:$WhatIf
Write-Host "sync-agents: zoo surfaces -> $($zooCmds.Count) launchers in .roo/commands/; .roomodes (6 BMAD modes); floor rules in .roo/rules/"

# --- local tool dirs ----------------------------------------------------------
if (-not $GlobalsOnly) {
  # What the LAST run wrote here. Everything purged below is drawn from this record, never from a bare
  # "not in master" test — that test cannot tell a retired ghost from a project's own command.
  $manifest = Get-SyncManifest $Target
  # Rebuilt from scratch each run and swapped in at save time, so keys from an older layout (or an older
  # absolute-path scheme) age out instead of accumulating forever.
  $newLocal = @{}
  # Project vendoring RETIRED (thin model, 2026-08-07 — .agents/rules/project-law.md): projects carry
  # tier-2 law only, and the non-lobby guard above makes this whole stage lobby-only. The manifest's
  # `vendor` key stays in the schema (older manifests carry it) but nothing writes it anymore.

  # Source of truth: the master (the only sanctioned target is the lobby).
  $src    = $Master
  $cmdDir = Join-Path $src "commands"

  # Manifest keys are RELATIVE to the target, so the record stays valid if the repo is moved or re-cloned.
  # .claude\commands publishing is RETIRED (SCC-66 - see THE DOOR MODEL above): Claude's menu reads skills,
  # so command mirrors here double-doored every command beside its launcher skill. This run claims NOTHING,
  # which makes Invoke-ManifestPurge retire everything previous runs wrote; files the sync never wrote are
  # untouched, exactly like any other retirement. The manifest key stays so older records keep resolving.
  $claudeCmdKey = ".claude\commands"
  $claudeCmdDst = Join-Path $Target $claudeCmdKey
  $cl = @()
  $clGone = Invoke-ManifestPurge $claudeCmdDst $manifest.local[$claudeCmdKey] $cl -WhatIf:$WhatIf
  if ($clGone.Count) { Write-Host "sync-agents: purged $($clGone.Count) retired .claude command(s): $($clGone -join ', ')" }
  $newLocal[$claudeCmdKey] = $cl
  # bmad-* skills are BMAD-OWNED. BMAD self-installs them (its `ides:` = claude-code, antigravity) directly into
  # .claude\skills, .opencode, and .agent\skills, and refreshes them on every `bmad` update. Our toolkit must NOT
  # carry or shadow them: a stale vendored copy in .agents\skills would clobber BMAD's current install on each
  # sync (robocopy overwrites same-named files). Exclude bmad-* so BMAD stays the single source for its own skills.
  # Skills are the THIRD invocable surface, not just content: Claude Code publishes a slash command for every
  # .claude\skills\*\SKILL.md, so a RENAMED skill leaves a typeable ghost exactly the way a retired command file
  # does (/cicd-write-epics-stories-sprint survived its own rename this way). Sync-Dir is additive robocopy, so
  # the manifest carries the same ownership record here that it already carries for commands.
  # Per-platform reach for the SKILL door (SCC-66): .agents\skills is Codex's NATIVE surface and
  # .claude\skills is Claude's cache, so `platforms:` splits here rather than in Sync-CommandDir -
  # a codex-only command's launcher must not ride the tree copy into Claude's menu, and a claude-only
  # command's launcher never enters the master at all (it is emitted below, cache-only).
  $doorCmds = @(Get-ChildItem -Path $cmdDir -Filter '*.md' -File | Where-Object { $_.Name -notmatch '-AP\.md$' })
  $cxOnly = @(); $clOnly = @()
  foreach ($f in $doorCmds) {
    $pl = Get-CommandPlatforms $f.FullName
    if (($pl -contains 'codex')  -and -not ($pl -contains 'claude')) { $cxOnly += $f.BaseName }
    if (($pl -contains 'claude') -and -not ($pl -contains 'codex'))  { $clOnly += $f }
  }
  $skillSrcDir = Join-Path $src "skills"
  $claudeSkKey = ".claude\skills"
  $claudeSkDst = Join-Path $Target $claudeSkKey
  try {
    Sync-Dir $skillSrcDir $claudeSkDst (@('bmad-*') + $cxOnly) -WhatIf:$WhatIf
    # claude-only launchers, emitted straight into the cache - and recorded in the manifest set below, so a
    # later retirement purges them like any other sync-written skill. A hand-authored SKILL.md wins here too.
    $clOnlyMade = @()
    foreach ($f in $clOnly) {
      $dstDir    = Join-Path $claudeSkDst $f.BaseName
      $skillFile = Join-Path $dstDir 'SKILL.md'
      if ((Test-Path $skillFile) -and ((Get-Content $skillFile -Raw) -notmatch 'GENERATED by sync-agents')) { continue }
      if (-not $WhatIf) {
        New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
        [IO.File]::WriteAllText($skillFile, (New-LauncherSkillStub $f), (New-Object Text.UTF8Encoding($false)))
      } else {
        Write-Host ("WHATIF: would emit claude-only launcher skill '{0}' -> .claude/skills/" -f $f.BaseName)
      }
      $clOnlyMade += $f.BaseName
    }
    # ⛔ PLAIN assignment, and filter the VARIABLE - never pipe Get-SkillDirSet directly, and never wrap the
    # call in @(). It returns `,@(...)` (the wrapper idiom that stops an empty/1-element array from unrolling),
    # and only a bare assignment unrolls that wrapper back into the real array. `@(Get-SkillDirSet ...)` yields
    # a 1-element array whose single item IS the inner array, and piping hands Where-Object that same single
    # object - either way $now then matches no name and the manifest purge proposes deleting all 32 skill dirs
    # it ever wrote, hand-authored ones included. Caught by -WhatIf, twice, before it ran.
    $masterSk = Get-SkillDirSet $skillSrcDir
    $sk       = @(@($masterSk | Where-Object { $cxOnly -notcontains $_ }) + $clOnlyMade)
    $skGone = Invoke-ManifestPurgeDir $claudeSkDst $manifest.local[$claudeSkKey] $sk -WhatIf:$WhatIf
    if ($skGone.Count) { Write-Host "sync-agents: purged $($skGone.Count) retired .claude skill(s): $($skGone -join ', ')" }
    $newLocal[$claudeSkKey] = $sk
  } catch {
    Write-Warning ("sync-agents: .claude/skills is read-only under OS sandbox in-session ({0}) - skipping .claude/skills write" -f $_.Exception.Message)
    if ($manifest.local[$claudeSkKey]) { $newLocal[$claudeSkKey] = $manifest.local[$claudeSkKey] }
  }

  # --- .claude\rules: the PATH-SCOPED rules only (SCC-270) -------------------------------------------
  # Claude Code loads a .claude\rules\*.md file ONLY when it reads a file matching that rule's `paths:`
  # frontmatter - which is exactly the behaviour the on-demand tier wants, and exactly the behaviour a
  # rule WITHOUT `paths:` must never get: no-paths means "load at launch, unconditionally", so mirroring
  # the whole master dir would drag every floor and protocol rule into every session twice over (they
  # already load through AGENTS.md) and quietly re-classify the entire tier system.
  #
  # ⛔ COPIES, never symlinks. Claude Code does resolve symlinked rules, but a Windows checkout without
  # Developer Mode materialises a symlink as a TEXT FILE containing the target path - the rule would
  # then "load" as one line of nonsense, on the machine least likely to notice (two-machines rule).
  #
  # Manifest-tracked, so a rule that stops being path-scoped has its copy retired on the next run
  # instead of lingering as a rule nobody can find the master for.
  $clRulesKey = ".claude\rules"
  $clRulesDst = Join-Path $Target $clRulesKey
  $ruleSrcDir = Join-Path $src "rules"
  $pathScoped = @()
  if (Test-Path $ruleSrcDir) {
    foreach ($rf in (Get-ChildItem $ruleSrcDir -Filter '*.md' -File | Sort-Object Name)) {
      if ($rf.Name -eq 'INDEX.md') { continue }
      # Frontmatter only: `paths:` must be a top-level key in the leading --- block, never a mention
      # in the body (a rule that DISCUSSES paths: is not itself path-scoped).
      $lines = [IO.File]::ReadAllLines($rf.FullName)
      if ($lines.Count -lt 2 -or $lines[0].Trim() -ne '---') { continue }
      $fmEnd = -1
      for ($i = 1; $i -lt $lines.Count; $i++) { if ($lines[$i].Trim() -eq '---') { $fmEnd = $i; break } }
      if ($fmEnd -lt 0) { continue }
      $hasPaths = $false
      for ($i = 1; $i -lt $fmEnd; $i++) { if ($lines[$i] -match '^paths:\s*$|^paths:\s*\[') { $hasPaths = $true; break } }
      if (-not $hasPaths) { continue }
      $pathScoped += $rf.Name
      if ($WhatIf) {
        Write-Host ("WHATIF: would copy path-scoped rule '{0}' -> .claude/rules/" -f $rf.Name)
      } else {
        if (-not (Test-Path $clRulesDst)) { New-Item -ItemType Directory -Path $clRulesDst -Force | Out-Null }
        Copy-Item $rf.FullName (Join-Path $clRulesDst $rf.Name) -Force
      }
    }
  }
  $clRulesGone = Invoke-ManifestPurge $clRulesDst $manifest.local[$clRulesKey] $pathScoped -WhatIf:$WhatIf
  if ($clRulesGone.Count) { Write-Host "sync-agents: purged $($clRulesGone.Count) rule(s) no longer path-scoped: $($clRulesGone -join ', ')" }
  $newLocal[$clRulesKey] = $pathScoped
  $ocCmdKey = ".opencode\commands"
  $ocCmdDst = Join-Path $Target $ocCmdKey
  $oc = Sync-CommandDir $cmdDir $ocCmdDst "opencode" -SkipAP:$IsLobby -WhatIf:$WhatIf
  $ocGone = Invoke-ManifestPurge $ocCmdDst $manifest.local[$ocCmdKey] $oc -WhatIf:$WhatIf
  if ($ocGone.Count) { Write-Host "sync-agents: purged $($ocGone.Count) retired .opencode command(s): $($ocGone -join ', ')" }
  $newLocal[$ocCmdKey] = $oc
  # -ExcludeFiles INDEX.md: opencode's agent loader treats EVERY .md in this dir as an agent definition, so
  # the folder's own map file was being registered as a selectable agent named "INDEX" (mode `all`) whose
  # entire prompt is a list of its sibling files. It showed up in the agent picker in all six projects that
  # have a .opencode. The command surface never had this bug because .agents/commands/INDEX.md declares
  # `platforms: []` and Sync-CommandDir filters on that — but Sync-Dir is a plain tree copy with no such
  # filter, so the exclusion has to be stated here. check_maps.py never descends into .opencode, so the
  # master's INDEX.md still satisfies the map lint; only the vendored copy is suppressed.
  Sync-Dir (Join-Path $src "opencode-agents") (Join-Path $Target ".opencode\agent") -ExcludeFiles 'INDEX.md' -WhatIf:$WhatIf

  Write-Host "sync-agents: .claude\commands   -> RETIRED (SCC-66; Claude's door is .claude\skills)"
  Write-Host "sync-agents: .claude\skills     -> $($sk.Count) skill dirs ($($clOnlyMade.Count) claude-only launcher(s))"
  Write-Host "sync-agents: .claude\rules      -> $($pathScoped.Count) path-scoped rule(s) (floor/protocol deliberately NOT mirrored)"
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
  # SCC-332: each cache names its OWN source. opencode reads /-commands and wants the full body.
  # -WhatIf FIDELITY, stated because it changed here: Sync-AntigravityWorkflowMirror writes nothing
  # under -WhatIf, so a dry run enumerates the doors the LAST REAL SYNC wrote. A brand-new command
  # prints "would emit LAUNCHER" above and then does not appear in this cache's preview. The opencode
  # cache still previews from commands/ and is always current. Dry-run counts here are a floor.
  # Antigravity TRUNCATES at 12,000 chars instead of rejecting (SCC-135), so a verbatim 30 KB command
  # runs on partial steps and looks fine. It must be fed the already-generated thin-launcher surface in
  # .agents\workflows - the same doors the per-project sync writes - never the raw command bodies.
  $GlobalCmdSrc = Join-Path $Master "commands"
  $GlobalWfSrc  = Join-Path $Master "workflows"
  $caches = @(
    @{ Name = 'opencode';    Platform = 'opencode';    Src = $GlobalCmdSrc; Path = (Join-Path $UserHome ".config\opencode\commands") },
    @{ Name = 'antigravity'; Platform = 'antigravity'; Src = $GlobalWfSrc;  Path = (Join-Path $UserHome ".gemini\antigravity\global_workflows") }
  )
  foreach ($c in $caches) {
    try {
      if (-not $WhatIf) {
        New-Item -ItemType Directory -Force -Path $c.Path -ErrorAction SilentlyContinue | Out-Null
        # Guard the REAL run only. Under -WhatIf the dir was deliberately not created, so this test
        # would fail on every not-yet-existing cache and report a fake "broken junction" on a fresh
        # machine - which is exactly the state a dry run is most often used to inspect.
        if (-not (Test-Path $c.Path)) { throw "path not writable (broken junction or missing target?)" }
      } else {
        Write-Host ("WHATIF: would ensure global cache dir '{0}'" -f $c.Path)
      }
    } catch {
      Write-Warning ("sync-agents: SKIPPED {0} global cache '{1}' - {2}" -f $c.Name, $c.Path, $_.Exception.Message)
      continue
    }
    $names = Sync-CommandDir $c.Src $c.Path $c.Platform -Mirror -SkipAP -WhatIf:$WhatIf
    Write-Host ("sync-agents: {0} global -> {1} cmds  ({2})" -f $c.Name, $names.Count, $c.Path)
  }
  Write-Host "sync-agents: (global caches mirror-exact; bmad-* preserved; restart opencode to pick up)"

  # Codex prompts cache RETIRED (SCC-66): /prompts:<name> is Codex's deprecated door and double-doored
  # every command beside the native skill in .agents\skills. Purge our prompts once per machine; bmad-*
  # stays BMAD's own, exactly as in the mirror caches above.
  $codexPrompts = Join-Path $UserHome ".codex\prompts"
  if (Test-Path $codexPrompts) {
    $stalePrompts = @(Get-ChildItem -Path $codexPrompts -Filter '*.md' -File -ErrorAction SilentlyContinue |
                      Where-Object { $_.Name -notmatch '^bmad-' })
    if (-not $WhatIf) { $stalePrompts | ForEach-Object { Remove-Item $_.FullName -Force } }
    else { $stalePrompts | ForEach-Object { Write-Host ("WHATIF: would purge retired codex prompt '{0}'" -f $_.Name) } }
    if ($stalePrompts.Count) { Write-Host ("sync-agents: codex prompts cache RETIRED - purged {0} prompt(s); Codex's door is .agents/skills" -f $stalePrompts.Count) }
  }

  # Codex FLOOR-rule cache (SCC-346 Part F). Codex reads the repo's AGENTS.md natively and merges
  # ~/.codex/AGENTS.md globally, but it has no @import mechanism, so the three FLOOR rules are
  # written into that machine cache between GENERATED markers. Content OUTSIDE the markers is the
  # operator's own and is preserved verbatim; the block is regenerated every sync. The law stays in
  # .agents/rules/ - this is a delivery cache, exactly like .roo/rules/ and .claude/rules/.
  $codexAgents = Join-Path $UserHome ".codex\AGENTS.md"
  $floorBegin  = '<!-- BEGIN GENERATED floor-rules (sync-agents, SCC-346) - edit .agents/rules/, never this block -->'
  $floorEnd    = '<!-- END GENERATED floor-rules -->'
  $floorRules  = @('operator-profile.md', 'constitution.md', 'karpathy-guidelines.md')
  $floorParts  = @($floorBegin)
  foreach ($rn in $floorRules) {
    $srcF = Join-Path (Join-Path $Master 'rules') $rn
    if (Test-Path $srcF) { $floorParts += ('<!-- from .agents/rules/' + $rn + ' -->'); $floorParts += [IO.File]::ReadAllText($srcF) }
    else { Write-Warning ("sync-agents: codex floor rule MISSING in master: '{0}'" -f $rn) }
  }
  $floorParts += $floorEnd
  $floorBlock = ($floorParts -join "`n")
  try {
    if (Test-Path $codexAgents) {
      $existing = [IO.File]::ReadAllText($codexAgents)
      $bIdx = $existing.IndexOf($floorBegin)
      $eIdx = $existing.IndexOf($floorEnd)
      if (($bIdx -ge 0) -and ($eIdx -gt $bIdx)) {
        $newText = $existing.Substring(0, $bIdx) + $floorBlock + $existing.Substring($eIdx + $floorEnd.Length)
      } else {
        $newText = $existing.TrimEnd() + "`n`n" + $floorBlock + "`n"
      }
    } else {
      $newText = $floorBlock + "`n"
    }
    if (-not $WhatIf) {
      New-Item -ItemType Directory -Force -Path (Split-Path $codexAgents -Parent) | Out-Null
      [IO.File]::WriteAllText($codexAgents, $newText, (New-Object Text.UTF8Encoding($false)))
      Write-Host ("sync-agents: codex floor cache -> {0} rule(s) in {1} (outside-marker content preserved)" -f $floorRules.Count, $codexAgents)
    } else {
      Write-Host ("WHATIF: would write floor-rules block ({0} rules) into '{1}'" -f $floorRules.Count, $codexAgents)
    }
  } catch {
    Write-Warning ("sync-agents: SKIPPED codex floor cache '{0}' - {1}" -f $codexAgents, $_.Exception.Message)
  }

  # Codex reads Agent Skills natively but NOT .claude/skills (where BMAD installs). Mirror the bmad-* skills
  # into ~/.codex/skills so BMAD is reachable from Codex via /skills (Daniel: "we use bmad in everything").
  $codexSkillsDst = Join-Path $UserHome ".codex\skills"
  $bmadSkillSrc   = Join-Path $HomeRoot ".claude\skills"
  $codexSkillCount = Sync-CodexSkills $bmadSkillSrc $codexSkillsDst -WhatIf:$WhatIf
  Write-Host ("sync-agents: codex skills -> {0} bmad-* mirrored  ({1})" -f $codexSkillCount, $codexSkillsDst)
}

# (Fresh living-template drift check RETIRED 2026-08-07: Fresh_Workspace_BMAD is frozen — the clone
# source is now the sudo-project-skeleton repo, and lobby canon changes no longer propagate to Fresh.
# The living-template-sync rule is rewritten against the skeleton in the centralization epic's P6.)

Write-Host "sync-agents: done. (Edit the master .agents/ - never the copies - and re-run to propagate.)"
exit 0
