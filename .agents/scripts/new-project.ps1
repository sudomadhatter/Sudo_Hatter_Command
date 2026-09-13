<#
.SYNOPSIS
  Scaffold a new project workspace under Projects/ by cloning the thin skeleton.

.DESCRIPTION
  Clones sudomadhatter/sudo-project-skeleton into Projects/<Name>, strips its git history, re-inits
  the project's own repo, arms the git hooks, substitutes the project name into the skeleton's
  placeholders, and sets the project's POSTURE from one question (SCC-459).

  TWO POSTURES, ONE QUESTION - "does this project have a Jira board?" There is no third state:

    Jira = NO   (the default, and what you get by passing no -JiraSite/-JiraKeys)
        A quick project, for speed. Nothing is written and nothing is armed. That is not an
        unfinished setup, it is the finished one: every gate in this system is a marker file
        away from silent, by construction - pre-push-main-approval.sh exits 0 on its first
        line without MAIN-PUSH-ENFORCE, and commit-msg-jira.sh no-ops without a jira.conf.
        Branches are `chore/<slug>` or none at all; main is reached by pushing to it.
        It is said ONCE at the end and never again. There is no nag.

    Jira = YES  (-JiraSite and -JiraKeys, both or neither)
        The full enterprise dev system. jira.conf is written, the acli site is verified to
        MATCH the one declared, and all three *-ENFORCE markers are armed in the scaffold
        commit. Branches are `chore/<KEY>-<slug>`; main is reached by a pull request.

  ⛔ BEFORE SCC-459 THE "YES" HALF DID NOT EXIST. This script armed core.hooksPath so the hooks
  RAN, then created no marker at all, and named only JIRA-ENFORCE in closing prose for the reader
  to touch by hand. A project that wanted enterprise protection got warn-only gates and was told
  nothing. Arming is now what answering "yes" MEANS.

  Upgrading later costs nothing and needs no undo, because the "no" posture wrote nothing: write
  jira.conf, verify the site, touch the three markers.

  THIN MODEL (2026-08-07, SCC-31 — .agents/rules/project-law.md): the new project carries NO shared
  toolkit. No commands, no shared rules, no skills, no sync. Sessions run from this command center, so
  tier 1 is already loaded; the project holds only its own law (`.agents/rules|skills` + `INDEX.md`)
  plus the repo-local enforcement set. That is why this script no longer calls sync-agents — a project
  target is now a hard error there, and the local `templates/project-template` it used to copy was
  retired with the vendor.

.PARAMETER Name
  The new project's folder name.

.PARAMETER JiraSite
  This project's Jira site, e.g. https://your-site.atlassian.net. Supply it WITH -JiraKeys to take
  the "yes" posture. Omit both for the default.

.PARAMETER JiraKeys
  This project's Jira project key(s), e.g. NOVA. Space-separate only if the repo legitimately
  answers to more than one board. Supply it WITH -JiraSite.

.PARAMETER SkeletonUrl
  Override the clone source (defaults to the canonical skeleton repo).
#>
param(
  [Parameter(Mandatory = $true)][string]$Name,
  [string]$JiraSite = "",
  [string]$JiraKeys = "",
  [string]$SkeletonUrl = "https://github.com/sudomadhatter/sudo-project-skeleton.git"
)

$ErrorActionPreference = "Stop"
$Master = Split-Path $PSScriptRoot -Parent      # ...\.agents
$HomeRoot = Split-Path $Master -Parent            # ...\Sudo_Hatter_Command
# A project name becomes a folder, a repository identity, and a command argument on both Mac and
# Windows. Keep it to one portable segment so `../name`, drive paths, and Windows device names can
# never escape Projects/ or create a clone another machine cannot check out. Checked BEFORE the
# clone, because the damage of a traversing name is done the moment a path is built from it.
if ($Name -notmatch '^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,78}[A-Za-z0-9_-])?$' -or
    $Name -match '^(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)') {
  throw "Project name must be one portable folder name (letters, digits, dot, underscore, or hyphen; no paths or trailing dot): $Name"
}

# ── The posture, resolved and VERIFIED BEFORE anything is created ────────────────────────────
# Same reasoning as the name check above: a half-made project is worse than none. If the "yes"
# answer cannot be verified, nothing is cloned and the operator still has an empty Projects/ to
# retry into, rather than a scaffold whose gates may or may not be armed.
$WantJira = $JiraSite -or $JiraKeys
if ($WantJira -and -not ($JiraSite -and $JiraKeys)) {
  throw ("-JiraSite and -JiraKeys go together: a key prefix alone is half an address. " +
         "Pass both, or neither for a project with no board.")
}
if ($WantJira) {
  if ($JiraKeys -notmatch '^[A-Z][A-Z0-9]+( [A-Z][A-Z0-9]+)*$') {
    throw "JiraKeys must be one or more space-separated uppercase project keys (e.g. 'NOVA'): $JiraKeys"
  }
  # ⛔ THE SITE IS VERIFIED, NOT TAKEN ON TRUST. acli validates against whatever board this
  # machine happens to be logged into, so a correct-looking key can bind a project to someone
  # else's site and nothing downstream would notice.
  $JiraHostName = ($JiraSite -replace '^https?://', '') -replace '/.*$', ''
  if (-not $JiraHostName) { throw "JiraSite does not contain a host: $JiraSite" }
  if (-not (Get-Command acli -ErrorAction SilentlyContinue)) {
    throw ("acli is not on PATH, so the Jira site cannot be verified. Install it and re-run, or " +
           "run with no -JiraSite/-JiraKeys and add the board later (the upgrade needs no undo).")
  }
  $AuthOut = (& acli jira auth status 2>&1) -join "`n"
  if ($LASTEXITCODE -ne 0) {
    throw "acli jira auth status failed (rc=$LASTEXITCODE). Log in, then re-run.`n$AuthOut"
  }
  if ($AuthOut -notmatch [regex]::Escape($JiraHostName)) {
    throw ("acli is authenticated against a DIFFERENT site than -JiraSite ($JiraHostName). " +
           "Binding this project to it would point its tickets at the wrong board.`n$AuthOut")
  }
  Write-Host "new-project: Jira site verified — acli is authenticated against $JiraHostName"
}

$Dest = Join-Path $HomeRoot "Projects/$Name"

if (Test-Path $Dest) { throw "Project already exists: $Dest" }

Write-Host "new-project: cloning the skeleton -> Projects/$Name"
git clone --depth 1 $SkeletonUrl $Dest
if ($LASTEXITCODE -ne 0) { throw "skeleton clone failed (rc=$LASTEXITCODE). Check network / repo access: $SkeletonUrl" }

# Its history is the TEMPLATE's, not this project's — drop it and start clean.
Remove-Item -Recurse -Force (Join-Path $Dest ".git")

Push-Location $Dest
try {
  git init  | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "project git init failed (rc=$LASTEXITCODE)" }
  # Hooks are per-clone AND per-machine: git never carries core.hooksPath. Arm it now so the encoding
  # guard and the commit-msg Jira gate are live from the first commit. (The Jira gate stays SILENT
  # until .agents/jira.conf exists — see .agents/jira.conf.example for the 4-step arming procedure.)
  # ⛔ NOT `git config core.hooksPath .githooks`: that key, sitting in .git/config, is what
  # Claude Code's worktree setup finds, resolves to an ABSOLUTE path and writes back to the
  # SHARED config - after which every worktree runs the MAIN checkout's hooks (SCC-323).
  & (Join-Path $PSScriptRoot '..\..\docs\migrations\scripts\Arm-HooksInclude.ps1') -Repos @('.') | Out-Null

  # Seed .claude/settings.local.json from OS template so worktrees auto-approve immediately
  $isWin = [System.Environment]::OSVersion.Platform -match "Win" -or $env:OS -match "Windows"
  $exampleTemplate = if ($isWin) {
      Join-Path $Dest ".claude/settings.local.json.example-pc"
  } else {
      Join-Path $Dest ".claude/settings.local.json.example-mac"
  }
  $localSettings = Join-Path $Dest ".claude/settings.local.json"
  if (Test-Path $exampleTemplate) {
      $currentUser = if ($isWin) { $env:USERNAME } else { $env:USER }
      $content = Get-Content $exampleTemplate -Raw -Encoding UTF8
      $content = $content.Replace("{{PROJECT_NAME}}", $Name).Replace("{{USER}}", $currentUser)
      [System.IO.File]::WriteAllText($localSettings, $content, (New-Object System.Text.UTF8Encoding($false)))
      Write-Host "  .claude/settings.local.json initialized from $(Split-Path $exampleTemplate -Leaf)"
  }

  # ── Question 1: what is this project called? ──────────────────────────────────────────────
  # The skeleton ships {{PROJECT_NAME}} / <PROJECT_NAME> / sudo-project-skeleton placeholders
  # across 24 files, and `scripts/rename-project.py` has always existed to substitute them —
  # this script simply never called it, so every clone began with a README telling a human to
  # run it by hand (SCC-459). Its own history is dropped above, so the substitution lands in
  # the scaffold commit and the project has never been called anything else.
  # ⛔ ABSENT AND FAILED ARE DIFFERENT, and conflating them made this step able to destroy the
  # thing it was added to improve. `-SkeletonUrl` is overridable, so the clone source is not
  # guaranteed to ship this helper — and the first cut threw on a missing file, AFTER the clone,
  # leaving exactly the half-made project the pre-clone checks above exist to prevent. Measured:
  # it took down three cases in test_teaching_edition.py, whose fixture skeleton carries no
  # `scripts/`. Same rule the fixture builder states for itself — copied IF PRESENT, never
  # demanded.
  #
  # ⛔ But absent is reported LOUDLY, never silently skipped: unsubstituted placeholders in a
  # project's first commit is the defect this whole step was added to close (SCC-459), and a
  # quiet skip would restore it while looking like success.
  $Renamer = Join-Path $Dest "scripts/rename-project.py"
  if (Test-Path $Renamer) {
    $Py = if (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { "python" }
    & $Py "scripts/rename-project.py" --name $Name --root "." | Out-Null
    # Present but non-zero IS a real failure — the helper ran and could not do its job.
    if ($LASTEXITCODE -ne 0) { throw "placeholder substitution failed (rc=$LASTEXITCODE)" }
    Write-Host "  placeholders substituted -> $Name"
    $Renamed = $true
  } else {
    Write-Host "  ⚠ this clone source ships no scripts/rename-project.py — placeholders NOT"
    Write-Host "    substituted. Fill them by hand: grep for '{{' and for '<PROJECT_NAME>'."
    $Renamed = $false
  }

  # ── Question 2: does this project have a Jira board? ──────────────────────────────────────
  # Verified above, before the clone. Answering "yes" is what ARMS the project; there is no
  # separate arming step and no marker left for the reader to touch by hand.
  if ($WantJira) {
    $Conf = Join-Path $Dest ".agents/jira.conf"
    $ConfBody = @(
      "# Jira binding for THIS repo. Written by new-project.ps1 at scaffold time (SCC-459).",
      "# Sourced as shell — keep it to plain KEY=`"value`" assignments.",
      "# The authenticated ``acli jira auth status`` site must match JIRA_SITE; it was verified",
      "# against this value before this project was created.",
      "JIRA_SITE=`"$JiraSite`"",
      "JIRA_KEYS=`"$JiraKeys`""
    ) -join "`n"
    [System.IO.File]::WriteAllText($Conf, $ConfBody + "`n", (New-Object System.Text.UTF8Encoding($false)))

    # ⛔ ALL THREE, NOT JUST THE JIRA ONE. They are tracked files, so they ride the scaffold
    # commit and are armed for every later clone of this project — that is why arming is a
    # `touch` and not a git config. One flag per gate:
    #   JIRA-ENFORCE          commit-msg-jira.sh   — a commit message must carry this board's key
    #   MERGE-TARGET-ENFORCE  merge-target-guard   + pre-push-merge-backstop (ONE flag, both halves)
    #   MAIN-PUSH-ENFORCE     pre-push-main-approval — main needs a minted, unspent token
    foreach ($m in @("JIRA-ENFORCE", "MERGE-TARGET-ENFORCE", "MAIN-PUSH-ENFORCE")) {
      $Marker = Join-Path $Dest ".agents/scripts/git-hooks/$m"
      [System.IO.File]::WriteAllText($Marker, "", (New-Object System.Text.UTF8Encoding($false)))
    }
    Write-Host "  Jira armed: jira.conf written, all three *-ENFORCE markers created."
  }

  # ⛔ EVERY ONE OF THESE THREE IS CHECKED, because `| Out-Null` swallows git's output and
  # PowerShell does not stop on a non-zero native exit code. Without the checks this script
  # printed "created Projects/<name>" over a repo with NO HEAD - the scaffold staged, the
  # commit refused (an unconfigured user.name is enough), and nothing said so. A new project
  # that reports success with no first commit is the worst shape available: the operator moves
  # on, and the failure surfaces days later as an empty history.
  git add -A                            | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "could not stage the scaffold (rc=$LASTEXITCODE)" }
  git commit -q -m "chore: scaffold $Name from the thin project skeleton" | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw ("scaffold commit failed (rc=$LASTEXITCODE). Configure git user.name/user.email, " +
           "then commit the staged scaffold in Projects/$Name; the tour must not report " +
           "success until HEAD exists.")
  }
}
finally { Pop-Location }

Write-Host ""
Write-Host "new-project: created Projects/$Name — own git repo, hooks armed, NO vendored toolkit."
Write-Host "  Its .agents/ holds only its own law; the shared toolkit stays here at the command center."
Write-Host ""
if ($WantJira) {
  Write-Host "POSTURE: Jira — the full enterprise dev system."
  Write-Host "  jira.conf binds $JiraKeys to $JiraSite (site verified against acli before the clone)."
  Write-Host "  Armed: JIRA-ENFORCE, MERGE-TARGET-ENFORCE, MAIN-PUSH-ENFORCE."
  Write-Host "  Branches are chore/<KEY>-<slug>; main is reached by a pull request, never a push."
} else {
  Write-Host "POSTURE: no Jira — a quick project, for speed."
  Write-Host "  Nothing was written and nothing is armed. Branch as chore/<slug> or just commit on"
  Write-Host "  main, and push it. You can add a board at ANY time — nothing has to be undone first:"
  Write-Host "    cd Projects/$Name && cp .agents/jira.conf.example .agents/jira.conf"
  Write-Host "  set JIRA_SITE and JIRA_KEYS, confirm 'acli jira auth status' names that same site,"
  Write-Host "  then touch .agents/scripts/git-hooks/{JIRA,MERGE-TARGET,MAIN-PUSH}-ENFORCE."
}
Write-Host ""
Write-Host "NEXT (manual, two steps):"
if (-not $Renamed) {
  Write-Host "  0. ⚠ PLACEHOLDERS — this clone source shipped no scripts/rename-project.py, so"
  Write-Host "     they are still in the tree. grep for '{{' and for '<PROJECT_NAME>'."
}
Write-Host "  1. router.md — add a row mapping 'work about <X>' -> Projects/$Name/"
Write-Host "  2. .gitmodules + gitlink — add it as a submodule if it should travel with the lobby:"
Write-Host "       git submodule add <remote-url> Projects/$Name"
Write-Host ""
Write-Host "  Add it to .agents/maintained-projects.txt only if you want the lint to cover it."
exit 0
