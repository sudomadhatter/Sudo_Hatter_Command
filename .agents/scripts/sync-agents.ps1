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
  [Alias('DryRun')][switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$Master   = Split-Path $PSScriptRoot -Parent     # ...\.agents
$HomeRoot = Split-Path $Master -Parent           # ...\Sudo_Hatter_Command
if (-not $Target) { $Target = $HomeRoot }
$Target   = (Resolve-Path $Target).Path
$IsLobby  = ($Target.TrimEnd('\') -ieq $HomeRoot.TrimEnd('\'))

$AllPlatforms = @('claude','opencode','antigravity','codex')

# --- helpers ------------------------------------------------------------------

function Sync-Dir($src, $dst, [string[]]$ExcludeDirs, [switch]$WhatIf) {
  if (-not (Test-Path $src)) { return }
  $xd = @('node_modules') + (@($ExcludeDirs) | Where-Object { $_ })
  if (-not $WhatIf) {
    New-Item -ItemType Directory -Force -Path $dst | Out-Null
    robocopy $src $dst /E /XD @xd /NFL /NDL /NJH /NJS /NC /NS | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($src -> $dst), rc=$LASTEXITCODE" }
  } else {
    Write-Host ("WHATIF: would robocopy '{0}' -> '{1}' (excluding: {2})" -f $src,$dst,($xd -join ', '))
  }
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
  param([string]$MasterCmdDir, [string]$Dst, [string]$Platform, [switch]$Mirror, [switch]$WhatIf)
  New-Item -ItemType Directory -Force -Path $Dst | Out-Null
  $masterFiles = Get-ChildItem -Path $MasterCmdDir -Filter '*.md' -File
  $masterNames = @($masterFiles | Select-Object -ExpandProperty Name)
  $eligible = @()
  foreach ($f in $masterFiles) {
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
  $excluded = @('1_update-maps.md') # Real workflow lives in workflows/, do not overwrite with command wrapper
  
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

# Regenerate the Antigravity workflow mirrors in the master BEFORE vendoring, so projects pick them up via
# the (additive) .agents vendor. (Global command cache still mirrors commands/ separately, unchanged.)
$agWf = Sync-AntigravityWorkflowMirror $Master -WhatIf:$WhatIf
Write-Host "sync-agents: antigravity workflow mirror -> $($agWf.Count) sudo-* in .agents/workflows/"

# --- local tool dirs ----------------------------------------------------------
if (-not $GlobalsOnly) {
  # Project target → vendor master's .agents into the project ADDITIVELY (Sync-Dir = /E, no purge). The
  # project's .agents is a HYBRID: master toolkit layered over project-OWNED rules\ + project skills\ that
  # master does NOT have. Do NOT change this to /MIR or a blanket /PURGE — it deletes the project's own files.
  if (-not $IsLobby) {
    # Exclude bmad\ from the vendor: BMAD's module config is PROJECT-OWNED (each repo carries its own
    # `project_name` etc.) and BMAD self-installs per project, so it must NOT be overwritten from master.
    # This keeps it project-owned the same way rules\ already are (additive vendor, master never clobbers it).
    Sync-Dir $Master (Join-Path $Target ".agents") @((Join-Path $Master 'bmad')) -WhatIf:$WhatIf
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

  $cl = Sync-CommandDir $cmdDir (Join-Path $Target ".claude\commands")  "claude" -WhatIf:$WhatIf
  # bmad-* skills are BMAD-OWNED. BMAD self-installs them (its `ides:` = claude-code, antigravity) directly into
  # .claude\skills, .opencode, and .agent\skills, and refreshes them on every `bmad` update. Our toolkit must NOT
  # carry or shadow them: a stale vendored copy in .agents\skills would clobber BMAD's current install on each
  # sync (robocopy overwrites same-named files). Exclude bmad-* so BMAD stays the single source for its own skills.
  Sync-Dir (Join-Path $src "skills")          (Join-Path $Target ".claude\skills") @('bmad-*') -WhatIf:$WhatIf
  Sync-Dir (Join-Path $src "hooks")           (Join-Path $Target ".claude\hooks") -WhatIf:$WhatIf
  $oc = Sync-CommandDir $cmdDir (Join-Path $Target ".opencode\commands") "opencode" -WhatIf:$WhatIf
  Sync-Dir (Join-Path $src "opencode-agents") (Join-Path $Target ".opencode\agent") -WhatIf:$WhatIf

  Write-Host "sync-agents: .claude\commands   -> $($cl.Count) cmds"
  Write-Host "sync-agents: .opencode\commands -> $($oc.Count) cmds"
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
    $names = Sync-CommandDir $GlobalCmdSrc $c.Path $c.Platform -Mirror -WhatIf:$WhatIf
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
