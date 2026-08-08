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
$Master   = Split-Path $PSScriptRoot -Parent      # ...\.agents
$HomeRoot = Split-Path $Master -Parent            # ...\Sudo_Hatter_Command
$Dest     = Join-Path $HomeRoot "Projects/$Name"

if (Test-Path $Dest) { throw "Project already exists: $Dest" }

Write-Host "new-project: cloning the skeleton -> Projects/$Name"
git clone --depth 1 $SkeletonUrl $Dest
if ($LASTEXITCODE -ne 0) { throw "skeleton clone failed (rc=$LASTEXITCODE). Check network / repo access: $SkeletonUrl" }

# Its history is the TEMPLATE's, not this project's — drop it and start clean.
Remove-Item -Recurse -Force (Join-Path $Dest ".git")

Push-Location $Dest
try {
  git init  | Out-Null
  # Hooks are per-clone AND per-machine: git never carries core.hooksPath. Arm it now so the encoding
  # guard and the commit-msg Jira gate are live from the first commit. (The Jira gate stays SILENT
  # until .agents/jira.conf exists — see .agents/jira.conf.example for the 4-step arming procedure.)
  git config core.hooksPath .githooks | Out-Null
  git add -A                            | Out-Null
  git commit -q -m "chore: scaffold $Name from the thin project skeleton" | Out-Null
} finally { Pop-Location }

Write-Host ""
Write-Host "new-project: created Projects/$Name — own git repo, hooks armed, NO vendored toolkit."
Write-Host "  Its .agents/ holds only its own law; the shared toolkit stays here at the command center."
Write-Host ""
Write-Host "NEXT (manual, three steps):"
Write-Host "  1. router.md — add a row mapping 'work about <X>' -> Projects/$Name/"
Write-Host "  2. .gitmodules + gitlink — add it as a submodule if it should travel with the lobby:"
Write-Host "       git submodule add <remote-url> Projects/$Name"
Write-Host "  3. Fill the placeholders: grep for '{{' and for '<PROJECT_NAME>' (AGENTS.md,"
Write-Host "     .agents/INDEX.md, _bmad-output/project-context.md, _my_resources/open_tasks/todo_list.md)."
Write-Host ""
Write-Host "  Optional, when it gets a Jira board: cp .agents/jira.conf.example .agents/jira.conf,"
Write-Host "  set JIRA_KEYS, then touch .agents/scripts/git-hooks/JIRA-ENFORCE to arm REJECT mode."
Write-Host ""
Write-Host "  Add it to .agents/maintained-projects.txt only if you want the lint to cover it."
exit 0
