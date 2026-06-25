<#
.SYNOPSIS
  Scaffold a new project workspace under Projects/ that is born with the routing design.

.DESCRIPTION
  Creates Projects/<Name> from .agents/templates/project-template, creates its _artifacts workspace,
  vendors the shared toolkit (sync-agents), and git-inits the new project's own repo. Projects/ is
  already covered by the home-base .gitignore, so the new repo stays independent.

  After it runs, add a row to router.md (manual, one line) so the lobby knows the new workspace.

.PARAMETER Name
  The new project's folder name.
#>
param([Parameter(Mandatory = $true)][string]$Name)

$ErrorActionPreference = "Stop"
$Master   = Split-Path $PSScriptRoot -Parent
$HomeRoot = Split-Path $Master -Parent
$Dest     = Join-Path $HomeRoot "Projects\$Name"

if (Test-Path $Dest) { throw "Project already exists: $Dest" }

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
robocopy (Join-Path $Master "templates\project-template") $Dest /E /NFL /NDL /NJH /NJS /NC /NS | Out-Null
if ($LASTEXITCODE -ge 8) { throw "template copy failed, rc=$LASTEXITCODE" }

New-Item -ItemType Directory -Force -Path (Join-Path $HomeRoot "_artifacts\$Name") | Out-Null

& (Join-Path $PSScriptRoot "sync-agents.ps1") -Target $Dest

Push-Location $Dest
try { git init | Out-Null } finally { Pop-Location }

Write-Host "new-project: created Projects\$Name (own git repo, toolkit vendored)."
Write-Host "NEXT (manual): add a row to router.md pointing 'work about <X>' -> Projects/$Name/."
exit 0
