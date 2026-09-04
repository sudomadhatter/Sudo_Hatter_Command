<#
.SYNOPSIS
  Scaffold a new project workspace under Projects/ by cloning the thin skeleton.

.DESCRIPTION
  Clones sudomadhatter/sudo-project-skeleton into Projects/<Name>, strips its git history, re-inits
  the project's own repo, arms the git hooks, and prints the two manual wiring steps.

  THIN MODEL (2026-08-07, SCC-31 — .agents/rules/project-law.md): the new project carries NO shared
  toolkit. No commands, no shared rules, no skills, no sync. Sessions run from this command center, so
  tier 1 is already loaded; the project holds only its own law (`.agents/rules|skills` + `INDEX.md`)
  plus the repo-local enforcement set. That is why this script no longer calls sync-agents — a project
  target is now a hard error there, and the local `templates/project-template` it used to copy was
  retired with the vendor.

.PARAMETER Name
  The new project's folder name.

.PARAMETER SkeletonUrl
  Override the clone source (defaults to the canonical skeleton repo).
#>
param(
  [Parameter(Mandatory = $true)][string]$Name,
  [string]$SkeletonUrl = "https://github.com/sudomadhatter/sudo-project-skeleton.git"
)

$ErrorActionPreference = "Stop"
$Master = Split-Path $PSScriptRoot -Parent      # ...\.agents
$HomeRoot = Split-Path $Master -Parent            # ...\Sudo_Hatter_Command
# A project name becomes a folder, repository identity, and command argument on both Mac and
# Windows. Keep it to one portable segment so `../name`, drive paths, and Windows device names can
# never escape Projects/ or create a clone that another machine cannot check out.
if ($Name -notmatch '^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,78}[A-Za-z0-9_-])?$' -or
    $Name -match '^(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)') {
  throw "Project name must be one portable folder name (letters, digits, dot, underscore, or hyphen; no paths or trailing dot): $Name"
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

  # Automated placeholder renaming
  $RenameScript = Join-Path $Dest "scripts/rename-project.py"
  if (Test-Path $RenameScript) {
    try {
      python3 $RenameScript --name $Name | Out-Null
    } catch {
      Write-Warning "Automated rename step encountered an issue: $_"
    }
  }

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

  git add -A                            | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "could not stage the scaffold (rc=$LASTEXITCODE)" }
  git commit -q -m "chore: scaffold $Name from the thin project skeleton" | Out-Null
  if ($LASTEXITCODE -ne 0) {
    throw "scaffold commit failed (rc=$LASTEXITCODE). Configure git user.name/user.email, then commit the staged scaffold in Projects/$Name; the tour must not report success until HEAD exists."
  }
}
finally { Pop-Location }

Write-Host ""
Write-Host "new-project: created Projects/$Name — own git repo, hooks armed, NO vendored toolkit."
Write-Host "  Its .agents/ holds only its own law; the shared toolkit stays here at the command center."
Write-Host ""
Write-Host "NEXT (three steps):"
Write-Host "  1. router.md — add a row mapping 'work about <X>' -> Projects/$Name/"
Write-Host "  2. .gitmodules + gitlink — add it as a submodule if it should travel with the lobby:"
Write-Host "       git submodule add <remote-url> Projects/$Name"
Write-Host "  3. Optional: Create remote repository (gh repo create $Name --private --source Projects/$Name)"
Write-Host ""
Write-Host "  Optional, only after this project gets a Jira board:"
Write-Host "       cd Projects/$Name"
Write-Host "       cp .agents/jira.conf.example .agents/jira.conf"
Write-Host "  Set JIRA_SITE and JIRA_KEYS, run 'acli jira auth status', and require its site to match."
Write-Host "  Only then touch .agents/scripts/git-hooks/JIRA-ENFORCE to arm REJECT mode."
Write-Host ""
Write-Host "  Add it to .agents/maintained-projects.txt only if you want the lint to cover it."
exit 0
