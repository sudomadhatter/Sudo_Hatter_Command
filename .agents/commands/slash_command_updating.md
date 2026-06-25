---
description: Sync project slash commands to both the Antigravity global cache AND the opencode global commands directory. Purges ghosts; copies fresh.
---

# /slash_command_updating — Sync Slash Commands (Antigravity + opencode)

This is an **adapted** version of the Antigravity workflow at @.agent/workflows/slash_command_updating.md. It now also syncs the opencode global commands directory.

## Execute this PowerShell unconditionally

```powershell
# ---- Paths ----
$ProjectRoot           = "$env:CD"
$LocalAntigravityWf    = "$ProjectRoot\.agent\workflows"
$LocalOpencodeCmds     = "$ProjectRoot\.opencode\commands"
$GlobalAntigravityWf   = "$env:USERPROFILE\.gemini\antigravity\global_workflows"
$GlobalOpencodeCmds    = "$env:USERPROFILE\.config\opencode\commands"

# Ensure global dirs exist
New-Item -ItemType Directory -Force -Path $GlobalAntigravityWf | Out-Null
New-Item -ItemType Directory -Force -Path $GlobalOpencodeCmds  | Out-Null

# ==== 1. Antigravity sync (legacy bug-fix logic preserved) ====
$LocalAgFiles = Get-ChildItem -Path $LocalAntigravityWf -Filter "*.md" -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty Name
Get-ChildItem -Path $GlobalAntigravityWf -Filter "*.md" -ErrorAction SilentlyContinue | Where-Object {
    ($_.Name -notmatch '^bmad-') -and ($LocalAgFiles -notcontains $_.Name)
} | Remove-Item -Force
if ($LocalAgFiles) {
    Copy-Item -Path "$LocalAntigravityWf\*.md" -Destination $GlobalAntigravityWf -Force
}

# ==== 2. opencode sync ====
$LocalOcFiles = Get-ChildItem -Path $LocalOpencodeCmds -Filter "*.md" -ErrorAction SilentlyContinue |
                Select-Object -ExpandProperty Name
# Purge global opencode ghosts that are not in the project (no bmad-* exclusion needed —
# all opencode bmad commands are project-canonical in .opencode/commands/)
Get-ChildItem -Path $GlobalOpencodeCmds -Filter "*.md" -ErrorAction SilentlyContinue | Where-Object {
    $LocalOcFiles -notcontains $_.Name
} | Remove-Item -Force
if ($LocalOcFiles) {
    Copy-Item -Path "$LocalOpencodeCmds\*.md" -Destination $GlobalOpencodeCmds -Force
}

Write-Host "✅ Antigravity workflows: $($LocalAgFiles.Count) synced → $GlobalAntigravityWf"
Write-Host "✅ opencode commands:     $($LocalOcFiles.Count) synced → $GlobalOpencodeCmds"
Write-Host "🧹 Ghosts purged from both global directories."
```

**Notes for opencode execution:**
- `external_directory` permission allows `~/.config/opencode/**` so the opencode global copies write through. Antigravity's `.gemini/antigravity/global_workflows` will trigger an `external_directory: ask` prompt — confirm to Don.
- After running, remind Don to **restart opencode** so the global config + commands are picked up if he opens another project.
- This command is also runnable directly: `pwsh scripts/mirror-opencode-commands.ps1` (for the opencode half only).

Optional additional input: $ARGUMENTS
