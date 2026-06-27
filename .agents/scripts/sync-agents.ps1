<#
.SYNOPSIS
  Push the master .agents toolkit into every command surface: a target's local tool dirs (the lobby or a
  project) AND the machine-global command caches for opencode + Antigravity/Gemini.

.DESCRIPTION
  Single source of authorship = <home>\.agents. The canonical invocable set is .agents\commands\ — it mirrors
  to ALL three platforms. This copies commands / skills / hooks / opencode-agents into the target's .claude
  and .opencode dirs (Claude /commands + skills + hooks resolve there) and, for a LOBBY sync, also refreshes
  the two machine-global caches so opencode and Antigravity see the same set Claude does.

  PLATFORM REACH. A command may declare its reach with frontmatter `platforms: [claude, opencode, antigravity]`.
  Absent = universal (all three). The sync copies a command only to the platforms it lists, so e.g.
  /autopilot_claude (claude-only) never lands in the opencode/gemini surfaces.

  PURGE POLICY.
    - Local tool dirs (.claude, .opencode): copy eligible commands; purge only commands that ARE master-managed
      but are no longer eligible for that platform. Files the master doesn't own (a project's own commands) are
      left alone. Skills / hooks / opencode-agents are an additive robocopy (no delete).
    - Global caches: MIRROR-EXACT — copy eligible, purge anything not eligible, EXCEPT `bmad-*` (BMAD installs
      its own global agents/workflows; never ours to delete).
    - Project .agents vendor: ADDITIVE. The vendored .agents is a HYBRID (master toolkit + project-owned
      rules\ and skills\), so it is NEVER mirrored/purged wholesale. The lone deletion is a narrow prune of
      stale workflows\ command-ghosts — a workflows\ file whose name is a master COMMAND but not a master
      WORKFLOW (a leftover from when commands lived in workflows\). That test provably never hits rules\,
      skills\, or a project-authored workflow.

  For a PROJECT target (not the lobby root) it ALSO vendors master's .agents into the project so the repo is
  clone-safe. That vendor is ADDITIVE (/E, no purge): a project's .agents is a HYBRID — master toolkit copied
  in, layered OVER project-OWNED content master does NOT have (notably .agents\rules\ and project-specific
  .agents\skills\). So NEVER /MIR or blanket-/PURGE the vendored .agents — that deletes the project's own
  files. The only deletion here is the narrow workflows\ command-ghost prune (see PURGE POLICY). A project
  sync does NOT touch the machine-global caches (globals reflect the lobby's canonical set).

  Always edit the master; never hand-edit the copies. Re-run this to propagate changes.

.PARAMETER Target
  Directory to sync into. Default: the home-base root (lobby).

.PARAMETER GlobalsOnly
  Refresh only the machine-global caches (opencode + Antigravity) from the lobby master. Skips local tool dirs.
  This is what /slash_command_updating now delegates to.

.PARAMETER NoGlobals
  Sync local tool dirs only; skip the machine-global caches even on a lobby sync.
#>
param(
  [string]$Target,
  [switch]$GlobalsOnly,
  [switch]$NoGlobals
)

$ErrorActionPreference = "Stop"
$Master   = Split-Path $PSScriptRoot -Parent     # ...\.agents
$HomeRoot = Split-Path $Master -Parent           # ...\Sudo_Hatter_Command
if (-not $Target) { $Target = $HomeRoot }
$Target   = (Resolve-Path $Target).Path
$IsLobby  = ($Target.TrimEnd('\') -ieq $HomeRoot.TrimEnd('\'))

$AllPlatforms = @('claude','opencode','antigravity')

# --- helpers ------------------------------------------------------------------

function Sync-Dir($src, $dst) {
  if (-not (Test-Path $src)) { return }
  New-Item -ItemType Directory -Force -Path $dst | Out-Null
  robocopy $src $dst /E /XD node_modules /NFL /NDL /NJH /NJS /NC /NS | Out-Null
  if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($src -> $dst), rc=$LASTEXITCODE" }
}

# Read a command file's `platforms:` frontmatter. Absent / no frontmatter => universal (all three).
# Recognized inline form only:  platforms: [claude, opencode]
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
      if ($items) { return @($items) } else { return $AllPlatforms }
    }
  }
  return $AllPlatforms
}

# Sync the canonical command set into $Dst for a given $Platform.
#   $MasterCmdDir : the authoritative .agents\commands to read from
#   -Mirror       : global-cache mode (purge non-eligible ghosts; preserve only FOREIGN bmad-* = BMAD's own
#                   global install); else local mode (purge only master-managed-but-ineligible; leave
#                   unknown/project-own files untouched)
# Returns the list of eligible file names.
function Sync-CommandDir {
  param([string]$MasterCmdDir, [string]$Dst, [string]$Platform, [switch]$Mirror)
  New-Item -ItemType Directory -Force -Path $Dst | Out-Null
  $masterFiles = Get-ChildItem -Path $MasterCmdDir -Filter '*.md' -File
  $masterNames = @($masterFiles | Select-Object -ExpandProperty Name)
  $eligible = @()
  foreach ($f in $masterFiles) {
    if ((Get-CommandPlatforms $f.FullName) -contains $Platform) {
      Copy-Item -Path $f.FullName -Destination $Dst -Force
      $eligible += $f.Name
    }
  }
  Get-ChildItem -Path $Dst -Filter '*.md' -File -ErrorAction SilentlyContinue | Where-Object {
    $name = $_.Name
    if ($eligible -contains $name)        { $false }                      # keep: eligible for this platform
    elseif ($masterNames -contains $name) { $true }                       # purge: OUR command, not eligible here
    elseif ($Mirror)                      { -not ($name -match '^bmad-') } # global: purge foreign ghosts, keep BMAD's own
    else                                  { $false }                      # local: keep foreign/project-own files
  } | Remove-Item -Force
  return $eligible
}

Write-Host "sync-agents: master=$Master"
Write-Host "sync-agents: target=$Target (lobby=$IsLobby)"

# --- local tool dirs ----------------------------------------------------------
if (-not $GlobalsOnly) {
  # Project target → vendor master's .agents into the project ADDITIVELY (Sync-Dir = /E, no purge). The
  # project's .agents is a HYBRID: master toolkit layered over project-OWNED rules\ + project skills\ that
  # master does NOT have. Do NOT change this to /MIR or a blanket /PURGE — it deletes the project's own files.
  if (-not $IsLobby) {
    Sync-Dir $Master (Join-Path $Target ".agents")
    # Prune stale command-ghosts from the vendored workflows/: a file that is a master COMMAND but NOT a
    # master workflow is a leftover from the old layout (commands used to live in workflows/). This is the
    # ONLY purge on the vendored .agents and it is provably safe — it can never touch rules/, skills/, or a
    # project-authored workflow (none of those are master commands). Everything else stays additive (/E).
    $mWf  = @(Get-ChildItem (Join-Path $Master "workflows") -Filter *.md -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
    $mCmd = @(Get-ChildItem (Join-Path $Master "commands")  -Filter *.md -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
    $purged = 0
    Get-ChildItem (Join-Path $Target ".agents\workflows") -Filter *.md -File -ErrorAction SilentlyContinue |
      Where-Object { ($mWf -notcontains $_.Name) -and ($mCmd -contains $_.Name) } |
      ForEach-Object { Remove-Item $_.FullName -Force; $purged++ }
    if ($purged) { Write-Host "sync-agents: purged $purged stale workflows/ command-ghost(s) from the vendor" }
  }

  # Source of truth for this target's tool dirs: master for the lobby, vendored copy for a project.
  $src    = if ($IsLobby) { $Master } else { Join-Path $Target ".agents" }
  $cmdDir = Join-Path $src "commands"

  $cl = Sync-CommandDir $cmdDir (Join-Path $Target ".claude\commands")  "claude"
  Sync-Dir (Join-Path $src "skills")          (Join-Path $Target ".claude\skills")
  Sync-Dir (Join-Path $src "hooks")           (Join-Path $Target ".claude\hooks")
  $oc = Sync-CommandDir $cmdDir (Join-Path $Target ".opencode\commands") "opencode"
  Sync-Dir (Join-Path $src "opencode-agents") (Join-Path $Target ".opencode\agent")

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
    @{ Name = 'antigravity'; Platform = 'antigravity'; Path = (Join-Path $env:USERPROFILE ".gemini\antigravity\global_workflows") }
  )
  foreach ($c in $caches) {
    try {
      New-Item -ItemType Directory -Force -Path $c.Path -ErrorAction SilentlyContinue | Out-Null
      if (-not (Test-Path $c.Path)) { throw "path not writable (broken junction or missing target?)" }
    } catch {
      Write-Warning ("sync-agents: SKIPPED {0} global cache '{1}' - {2}" -f $c.Name, $c.Path, $_.Exception.Message)
      continue
    }
    $names = Sync-CommandDir $GlobalCmdSrc $c.Path $c.Platform -Mirror
    Write-Host ("sync-agents: {0} global -> {1} cmds  ({2})" -f $c.Name, $names.Count, $c.Path)
  }
  Write-Host "sync-agents: (global caches mirror-exact; bmad-* preserved; restart opencode to pick up)"
}

Write-Host "sync-agents: done. (Edit the master .agents/ - never the copies - and re-run to propagate.)"
exit 0
