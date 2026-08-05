<#
.SYNOPSIS
    Generate a shareable "teaching edition" of a workspace from a manifest.

.DESCRIPTION
    The teaching repos are GENERATED, never hand-maintained. Improve the live repo, re-run
    this, push. Nothing ever flows back.

    Why generated rather than forked: a GitHub fork shares git HISTORY. Clean current files
    do not clean a dirty past - anyone can `git log` a fork and read every commit that ever
    touched _my_resources/, .env, or a client's name. An exported tree has no history to dig.

    The manifest IS the privacy audit. It is reviewed once, not re-decided on every push.

    A leak scan runs after every export and CANNOT be skipped. A guard that can be forgotten
    is not a guard, and this one is the only thing standing between a personal workspace and
    a public repo.

.PARAMETER Manifest
    Path to the manifest JSON (see .agents/scripts/teaching-edition/).

.PARAMETER Target
    Directory to write the export into. Overwritten in place; anything hand-edited there is
    destroyed on the next run. That is deliberate - see the header note above.

.PARAMETER WhatIf
    Report what would be copied, excluded and transformed. Writes nothing.

.EXAMPLE
    .\export-teaching-edition.ps1 -Manifest .agents/scripts/teaching-edition/lobby.manifest.json `
                                  -Target ../sudo-command-center -WhatIf
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Manifest,
    [Parameter(Mandatory)][string]$Target,
    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# --- load -------------------------------------------------------------------------------

if (-not (Test-Path -LiteralPath $Manifest)) { throw "Manifest not found: $Manifest" }
$manifestDir = Split-Path -Parent (Resolve-Path -LiteralPath $Manifest)
$m = Get-Content -LiteralPath $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json

$sourceRoot = Resolve-Path -LiteralPath (Join-Path $manifestDir $m.source)
if (-not (Test-Path -LiteralPath $sourceRoot)) { throw "Source not found: $sourceRoot" }

Write-Host ""
Write-Host "=== teaching-edition export: $($m.name) ===" -ForegroundColor Cyan
Write-Host "source : $sourceRoot"
Write-Host "target : $Target$(if ($WhatIf) { '   [WhatIf - nothing will be written]' })"
Write-Host ""

# --- exclusion matching -----------------------------------------------------------------

# Path segments that are never copied, wherever they appear in the tree.
$excludeDirs = @($m.excludeAnywhere)
# Repo-relative prefixes that are never copied.
$excludePaths = @($m.exclude) | ForEach-Object { $_.TrimEnd('/', '\') }

function Test-Excluded {
    param([string]$Rel)
    $norm = $Rel -replace '\\', '/'
    foreach ($p in $excludePaths) {
        if ($norm -eq $p -or $norm.StartsWith("$p/")) { return $p }
    }
    foreach ($d in $excludeDirs) {
        if ($norm -split '/' -contains $d) { return $d }
    }
    return $null
}

# --- walk -------------------------------------------------------------------------------

$copied = New-Object System.Collections.Generic.List[string]
$excluded = New-Object System.Collections.Generic.List[string]

foreach ($inc in $m.include) {
    $src = Join-Path $sourceRoot $inc
    if (-not (Test-Path -LiteralPath $src)) {
        Write-Warning "include path missing in source, skipped: $inc"
        continue
    }

    $items = if (Test-Path -LiteralPath $src -PathType Leaf) {
        @(Get-Item -LiteralPath $src)
    } else {
        Get-ChildItem -LiteralPath $src -Recurse -File -Force
    }

    foreach ($item in $items) {
        $rel = $item.FullName.Substring($sourceRoot.Path.Length).TrimStart('\', '/')
        $hit = Test-Excluded -Rel $rel
        if ($hit) { $excluded.Add("$rel   [$hit]"); continue }

        $copied.Add($rel)
        if ($WhatIf) { continue }

        $dest = Join-Path $Target $rel
        $destDir = Split-Path -Parent $dest
        if (-not (Test-Path -LiteralPath $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item -LiteralPath $item.FullName -Destination $dest -Force
    }
}

# --- substitutions ----------------------------------------------------------------------
# Literal token swaps applied to copied TEXT files, in manifest order (so a longer token can
# be handled before the shorter one it contains). This exists because most domain references
# in the core commands are incidental examples - "e.g. AGY_AVIATIONCHAT" - not structure.
# Rewriting those by hand would mean a replacement file per command; a short, readable
# from/to table is reviewable in a way a regex buried in JSON is not, and the leak scan
# below independently verifies the result.

# Dotfiles like .gitignore report their whole NAME as .Extension, so both are checked -
# missing that is how .gitignore shipped four project names past the substitution pass.
$TEXT_EXT = @('.md', '.txt', '.json', '.ps1', '.py', '.yaml', '.yml', '.toml', '.cfg', '.ini',
              '.sh', '.js', '.ts', '.html', '.css', '.xml', '.gitignore', '.gitattributes',
              '.env.example', '.editorconfig')
$subCount = 0
$subFiles = 0

if (-not $WhatIf -and $m.PSObject.Properties.Name -contains 'substitutions') {
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    foreach ($file in Get-ChildItem -LiteralPath $Target -Recurse -File -Force) {
        if ($TEXT_EXT -notcontains $file.Extension.ToLower() -and
            $TEXT_EXT -notcontains $file.Name.ToLower()) { continue }
        $text = [System.IO.File]::ReadAllText($file.FullName)
        $orig = $text
        foreach ($s in $m.substitutions) {
            if ($text.Contains($s.from)) {
                $n = ([regex]::Matches($text, [regex]::Escape($s.from))).Count
                $text = $text.Replace($s.from, $s.to)
                $subCount += $n
            }
        }
        if ($text -ne $orig) {
            [System.IO.File]::WriteAllText($file.FullName, $text, $utf8NoBom)
            $subFiles++
        }
    }
}

# --- transforms -------------------------------------------------------------------------
# A transform swaps in a hand-written replacement file. Deliberately NOT regex surgery:
# a replacement you can open and read is reviewable, a regex buried in JSON is not.

$transformed = New-Object System.Collections.Generic.List[string]
foreach ($t in $m.transforms) {
    $replacement = Join-Path $manifestDir $t.replaceWith
    if (-not (Test-Path -LiteralPath $replacement)) {
        throw "Transform replacement missing: $($t.replaceWith) (for $($t.path))"
    }
    $transformed.Add("$($t.path)  <-  $($t.replaceWith)")
    if ($WhatIf) { continue }

    $dest = Join-Path $Target $t.path
    $destDir = Split-Path -Parent $dest
    if (-not (Test-Path -LiteralPath $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    Copy-Item -LiteralPath $replacement -Destination $dest -Force
}

# --- report -----------------------------------------------------------------------------

Write-Host "copied      : $($copied.Count) files"
Write-Host "excluded    : $($excluded.Count) files"
Write-Host "substituted : $subCount token(s) across $subFiles file(s)"
Write-Host "transformed : $($transformed.Count) files"
Write-Host ""
Write-Host "-- transforms --" -ForegroundColor Yellow
$transformed | ForEach-Object { Write-Host "   $_" }
Write-Host ""

if (-not $WhatIf) {
    # The report NAMES every excluded path, so it necessarily contains the very strings the
    # leak scan hunts for. It is written OUTSIDE the export tree - never inside it. The first
    # version of this script put it in $Target and exempted it from the scan; the exemption
    # was the leak. A scanner with an exception list is a scanner with a hole.
    $absTarget = [System.IO.Path]::GetFullPath($Target)
    $reportPath = Join-Path (Split-Path -Parent $absTarget) `
                            ((Split-Path -Leaf $absTarget) + '.export-report.txt')
    $report = @(
        "teaching-edition export report",
        "manifest : $($m.name)",
        "source   : $sourceRoot",
        "",
        "--- transformed ($($transformed.Count)) ---"
    ) + $transformed + @(
        "",
        "--- excluded ($($excluded.Count)) ---"
    ) + $excluded
    Set-Content -LiteralPath $reportPath -Value $report -Encoding UTF8
    Write-Host "exclusion report: $reportPath"
}

# --- leak scan (never optional) ---------------------------------------------------------

Write-Host ""
Write-Host "-- leak scan --" -ForegroundColor Yellow

$needles = @($m.leakScan.literals)

# Every VALUE from the live .env, so a key that was pasted into a doc is caught even
# though the .env itself was excluded.
$envPath = Join-Path $sourceRoot '.env'
if (Test-Path -LiteralPath $envPath) {
    foreach ($line in Get-Content -LiteralPath $envPath) {
        if ($line -match '^\s*[#;]') { continue }
        if ($line -notmatch '=') { continue }
        $val = ($line -split '=', 2)[1].Trim().Trim('"').Trim("'")
        # Short values are common words, not secrets - they would only produce noise.
        if ($val.Length -ge 12) { $needles += $val }
    }
}

$scanRoot = if ($WhatIf) { $null } else { $Target }
$hits = @()
if ($scanRoot -and (Test-Path -LiteralPath $scanRoot)) {
    # No exemptions. Every file in the export tree is scanned, without exception.
    foreach ($file in Get-ChildItem -LiteralPath $scanRoot -Recurse -File -Force) {
        $text = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
        if (-not $text) { continue }
        foreach ($n in $needles) {
            if ($text -like "*$n*") {
                $rel = $file.FullName.Substring($scanRoot.Length).TrimStart('\', '/')
                $hits += "$rel  contains: $n"
            }
        }
    }
}

if ($WhatIf) {
    Write-Host "   skipped (WhatIf) - $($needles.Count) needles would be scanned"
} elseif ($hits.Count -gt 0) {
    Write-Host ""
    Write-Host "LEAK SCAN FAILED - $($hits.Count) hit(s):" -ForegroundColor Red
    $hits | Select-Object -Unique | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "Do NOT push this export. Fix the manifest (exclude or transform the file) and re-run." -ForegroundColor Red
    exit 1
} else {
    Write-Host "   clean - $($needles.Count) needles, 0 hits" -ForegroundColor Green
}

Write-Host ""
Write-Host "done." -ForegroundColor Cyan
