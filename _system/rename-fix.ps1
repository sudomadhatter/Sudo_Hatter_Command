<#
.SYNOPSIS
  Rename-day restructure: move projects into Projects/ AND repair all absolute-path references,
  in a single pass - so each project's paths are rewritten ONCE, straight to their final location.

.DESCRIPTION
  Run this AFTER you have renamed  C:\<OldName>  ->  C:\<NewName>  in Explorer and reopened the IDE
  at the new path. With -Apply it:
    1. Moves each known project from the home-base root into  <NewName>\Projects\<project>.
    2. Rewrites every absolute reference in TEXT files straight to the FINAL path:
         <OldName>\<project>\...   ->  <NewName>\Projects\<project>\...
         <OldName>\<infra>\...     ->  <NewName>\<infra>\...   (.agents, _artifacts, docs, etc.)
         bare "<OldName>"          ->  "<NewName>"             (names in prose)
       ...in the home base AND your user ~/.claude/settings.json.
    3. Lists virtual envs to recreate (they hardcode the old path).

  Safe by construction: DRY-RUN by default (shows everything first); skips node_modules, venvs, .git,
  __pycache__, .ruff_cache, .pytest_cache, .next, dist, build; only known text extensions; writes
  UTF-8 (no BOM). Add -Apply to do it; -RemoveVenvs to delete venvs for a clean recreate;
  -NoMove to fix paths only (no Projects/ move).

.EXAMPLE
  .\_system\rename-fix.ps1                          # dry-run preview (move + fixes)
  .\_system\rename-fix.ps1 -Apply                   # move projects + fix paths
  .\_system\rename-fix.ps1 -Apply -RemoveVenvs      # also delete venvs to recreate
#>
param(
  [string]$OldName = 'Sudo_Hatter_Command',
  [string]$NewName = 'Sudo_Hatter_Command',
  [switch]$Apply,
  [switch]$RemoveVenvs,
  [switch]$NoMove
)

$ErrorActionPreference = 'Stop'
$HomeRoot = Split-Path $PSScriptRoot -Parent   # _system -> home-base root (rename-safe)
$Projects = @('aviationChat-AGY','clean-bmad-workspace','jetChat-AGY','B&L WorldWide',
              'NEXGen Films','ingestion-Pipeline-AC','openCode')

Write-Host "Home root : $HomeRoot"
Write-Host "Replace   : '$OldName' -> '$NewName'   (projects -> Projects\<name>: $(-not $NoMove))"
Write-Host ("Mode      : " + $(if ($Apply) { 'APPLY (writing changes)' } else { 'DRY-RUN (no changes)' }))
Write-Host ""

# ---- STEP 1: move projects into Projects\ -----------------------------------
Write-Host "=== STEP 1: move projects into Projects\ ==="
$projDir = Join-Path $HomeRoot 'Projects'
if (-not $NoMove) {
  foreach ($p in $Projects) {
    $src = Join-Path $HomeRoot $p
    if (-not (Test-Path $src)) { continue }
    $dst = Join-Path $projDir $p
    if (-not $Apply) { Write-Host "  would move: $p  ->  Projects\$p"; continue }
    New-Item -ItemType Directory -Force -Path $projDir | Out-Null
    if (Test-Path $dst) { Write-Host "  SKIP (target exists): $p"; continue }
    try { Move-Item -LiteralPath $src -Destination $dst -Force; Write-Host "  moved: $p  ->  Projects\$p" }
    catch { Write-Host "  MOVE FAILED ($p): $($_.Exception.Message)  - close anything using it and retry." }
  }
} else { Write-Host "  (skipped: -NoMove)" }
Write-Host ""

# ---- STEP 2: rewrite absolute references in text files ----------------------
$textExt = @('.md','.markdown','.json','.jsonc','.toml','.cfg','.ini','.ps1','.psm1','.bat','.cmd',
             '.sh','.py','.pyi','.ts','.tsx','.js','.jsx','.mjs','.cjs','.css','.scss','.html','.yaml',
             '.yml','.txt','.env','.example','.firebaserc','.gitignore','.gitattributes','.code-workspace')
$excludeDir = @('node_modules','.venv','venv','.git','__pycache__','.ruff_cache','.pytest_cache',
                '.next','dist','build','.turbo','.cache')

function Convert-Refs([string]$raw) {
  $s = $raw
  if (-not $NoMove) {
    foreach ($p in $Projects) {
      $s = $s.Replace("$OldName\$p", "$NewName\Projects\$p")
      $s = $s.Replace("$OldName/$p", "$NewName/Projects/$p")
    }
  }
  return $s.Replace($OldName, $NewName)
}

function Get-TextFiles($root) {
  $out = New-Object System.Collections.Generic.List[string]
  $stack = New-Object System.Collections.Generic.Stack[string]; $stack.Push($root)
  while ($stack.Count -gt 0) {
    $cur = $stack.Pop()
    foreach ($e in $(try { Get-ChildItem -LiteralPath $cur -Force -EA Stop } catch { @() })) {
      if ($e.PSIsContainer) { if ($excludeDir -notcontains $e.Name) { $stack.Push($e.FullName) } }
      elseif ($textExt -contains $e.Extension.ToLower()) { $out.Add($e.FullName) }
    }
  }
  return $out
}

Write-Host "=== STEP 2: text files containing '$OldName' ==="
$files = Get-TextFiles $HomeRoot
$userSettings = Join-Path $env:USERPROFILE '.claude\settings.json'
if (Test-Path $userSettings) { $files += $userSettings }

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$changed = 0
foreach ($f in $files) {
  $raw = try { [System.IO.File]::ReadAllText($f) } catch { $null }
  if ($null -eq $raw -or $raw -notlike "*$OldName*") { continue }
  $changed++
  $n = ([regex]::Matches($raw, [regex]::Escape($OldName))).Count
  Write-Host ("  [{0,3}]  {1}" -f $n, ($f.Replace($HomeRoot + '\', '').Replace($env:USERPROFILE, '~')))
  if ($Apply) { [System.IO.File]::WriteAllText($f, (Convert-Refs $raw), $utf8NoBom) }
}
Write-Host "  ($changed files)"
Write-Host ""

# ---- STEP 3: virtual envs --------------------------------------------------
Write-Host "=== STEP 3: virtual envs (recreate - they hardcode the old path) ==="
$stack = New-Object System.Collections.Generic.Stack[string]; $stack.Push($HomeRoot)
while ($stack.Count -gt 0) {
  $cur = $stack.Pop()
  foreach ($d in $(try { Get-ChildItem -LiteralPath $cur -Directory -Force -EA Stop } catch { @() })) {
    if ($d.Name -in @('.venv','venv')) {
      Write-Host ("  " + $d.FullName.Replace($HomeRoot + '\', ''))
      if ($RemoveVenvs -and $Apply) { Remove-Item -LiteralPath $d.FullName -Recurse -Force; Write-Host "      -> removed (recreate: uv sync  OR  python -m venv .venv)" }
    } elseif ($d.Name -notin @('node_modules','.git','.next','dist','build')) { $stack.Push($d.FullName) }
  }
}

Write-Host ""
if (-not $Apply) { Write-Host "DRY-RUN done. Re-run with -Apply. Add -RemoveVenvs to delete venvs." }
else { Write-Host "APPLY done. Recreate venvs above, reload the IDE window, then tell Claude: 'pick up'." }
exit 0
