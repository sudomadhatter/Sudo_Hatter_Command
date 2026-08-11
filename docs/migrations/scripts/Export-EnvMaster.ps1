# Export-EnvMaster.ps1 — gather every secret env/credential file in the lobby +
# all sub-projects into ONE master file: docs/migrations/auth_keys/_secrets/master.env
#
# Run from anywhere:  powershell -File docs\migrations\scripts\Export-EnvMaster.ps1
# Output is GITIGNORED (**/auth_keys/ AND **/_secrets/ both match it). Carry it to the new machine yourself
# (USB / password manager attachment) — never commit, email, or cloud-sync it in plaintext.
#
# What it collects (auto-discovered, so new projects are picked up automatically):
#   1. Lobby root .env
#   2. Every real env file under Projects/  (.env, .env.local, .env.production)
#      — skips .env.example, node_modules, venvs, and git worktrees
#   3. Everything inside any auth_keys/ folder (service-account JSONs etc.)
#
# Companion: Restore-EnvMaster.ps1 splits the master back into files on the new machine.

# $Root must be the LOBBY ROOT — every path in the manifest is stored relative to
# it, and Restore-EnvMaster.ps1 rebuilds against the same base. This script lives
# three levels down (docs/migrations/scripts/), so walk up three times.
param([string]$Root = (Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent))

$ErrorActionPreference = 'Stop'
Set-Location $Root

$found = New-Object System.Collections.Generic.List[string]

if (Test-Path '.env') { $found.Add('.env') }

$envNames = @('.env', '.env.local', '.env.production')
Get-ChildItem -Path 'Projects' -Recurse -Force -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.FullName -notmatch '\\node_modules\\|\\\.venv\\|\\venv\\|\\worktrees\\' -and
        ($envNames -contains $_.Name -or $_.FullName -match '\\auth_keys\\')
    } |
    ForEach-Object {
        $rel = $_.FullName.Substring($Root.Length).TrimStart('\').Replace('\', '/')
        $found.Add($rel)
    }

$targets = $found | Sort-Object -Unique
if ($targets.Count -eq 0) { throw 'No env files found — wrong root?' }

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine('# ================================================================')
[void]$sb.AppendLine('# MASTER ENV — Sudo_Hatter_Command lobby + all sub-projects')
[void]$sb.AppendLine("# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm') on $env:COMPUTERNAME")
[void]$sb.AppendLine('# NEVER COMMIT THIS FILE. It contains live credentials.')
[void]$sb.AppendLine('#')
[void]$sb.AppendLine('# Format: each original file appears verbatim between a marker pair:')
[void]$sb.AppendLine('#   # >>> FILE: <path relative to lobby root>')
[void]$sb.AppendLine('#   ...content...')
[void]$sb.AppendLine('#   # <<< END FILE: <same path>')
[void]$sb.AppendLine('# Restore with docs/migrations/scripts/Restore-EnvMaster.ps1 (or by hand per the guide).')
[void]$sb.AppendLine('#')
[void]$sb.AppendLine("# MANIFEST ($($targets.Count) files):")
foreach ($t in $targets) { [void]$sb.AppendLine("#   - $t") }
[void]$sb.AppendLine('# ================================================================')
[void]$sb.AppendLine('')

foreach ($t in $targets) {
    $content = [System.IO.File]::ReadAllText((Join-Path $Root ($t.Replace('/', '\'))))
    [void]$sb.AppendLine("# >>> FILE: $t")
    [void]$sb.Append($content)
    if (-not $content.EndsWith("`n")) { [void]$sb.AppendLine('') }
    [void]$sb.AppendLine("# <<< END FILE: $t")
    [void]$sb.AppendLine('')
}

$vaultRel = 'docs/migrations/auth_keys/_secrets/master.env'
New-Item -ItemType Directory -Force -Path (Split-Path (Join-Path $Root ($vaultRel.Replace('/', '\'))) -Parent) | Out-Null
$out = Join-Path $Root ($vaultRel.Replace('/', '\'))
[System.IO.File]::WriteAllText($out, $sb.ToString(), (New-Object System.Text.UTF8Encoding $false))

# Refuse to leave the master in place if git would track it.
$ignored = git -C $Root check-ignore $vaultRel 2>$null
if (-not $ignored) {
    Remove-Item $out -Force
    throw ($vaultRel + ' is NOT gitignored — the vault lives under auth_keys/, so "**/auth_keys/" is the rule that must be in .gitignore ("**/_secrets/" alone no longer covers it). Add it, then re-run.')
}

Write-Host "Wrote $out ($($targets.Count) files bundled):"
$targets | ForEach-Object { Write-Host "  - $_" }
