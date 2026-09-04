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
    New or empty directory to write the export into. A non-empty target is refused so an old file or
    git history cannot survive a refresh invisibly.

.PARAMETER WhatIf
    Report what would be copied, excluded and transformed. Writes nothing.

.EXAMPLE
    .\export-teaching-edition.ps1 -Manifest .agents/scripts/teaching-edition/lobby.manifest.json `
                                  -Target ../sudo-command-center -WhatIf
#>
[CmdletBinding(DefaultParameterSetName = 'Export')]
param(
    [Parameter(Mandatory, ParameterSetName = 'Export')][string]$Manifest,
    [Parameter(Mandatory, ParameterSetName = 'Export')][string]$Target,
    [Parameter(ParameterSetName = 'Export')][switch]$WhatIf,
    [Parameter(Mandatory, ParameterSetName = 'LeakMatcherSelfTest')][switch]$SelfTestLeakMatcher
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Test-LiteralContains {
    param([AllowNull()][string]$Text, [AllowNull()][string]$Needle)
    if ([string]::IsNullOrEmpty($Text) -or [string]::IsNullOrEmpty($Needle)) { return $false }
    return $Text.IndexOf($Needle, [StringComparison]::OrdinalIgnoreCase) -ge 0
}

function Test-IsWithinDirectory {
    param([string]$Candidate, [string]$Directory)
    $candidatePath = [System.IO.Path]::GetFullPath($Candidate)
    $directoryPath = [System.IO.Path]::TrimEndingDirectorySeparator(
        [System.IO.Path]::GetFullPath($Directory)
    )
    $directoryPrefix = $directoryPath + [System.IO.Path]::DirectorySeparatorChar
    $comparison = if ([System.IO.Path]::DirectorySeparatorChar -eq '\') {
        [StringComparison]::OrdinalIgnoreCase
    } else {
        [StringComparison]::Ordinal
    }
    return $candidatePath.Equals($directoryPath, $comparison) -or
        $candidatePath.StartsWith($directoryPrefix, $comparison)
}

function Resolve-PhysicalPath {
    param([string]$Path)
    $full = [System.IO.Path]::GetFullPath($Path)

    # Resolve the final component up front when the caller supplied an existing
    # link. This explicit fast path also covers providers that expose the link
    # only on the final DirectoryInfo/FileInfo object during a WhatIf export.
    if (Test-Path -LiteralPath $full) {
        $finalItem = Get-Item -LiteralPath $full -Force
        if ($finalItem.LinkType) {
            $finalTarget = $finalItem.ResolveLinkTarget($true)
            if (-not $finalTarget) { throw "Cannot resolve target link" }
            $full = [System.IO.Path]::GetFullPath($finalTarget.FullName)
        }
    }

    $root = [System.IO.Path]::GetPathRoot($full)
    $current = $root
    $relative = $full.Substring($root.Length)
    $segments = $relative -split '[\\/]'
    foreach ($segment in $segments) {
        if ([string]::IsNullOrEmpty($segment)) { continue }
        $next = Join-Path $current $segment
        if (Test-Path -LiteralPath $next) {
            $item = Get-Item -LiteralPath $next -Force
            if ($item.LinkType) {
                $resolved = $item.ResolveLinkTarget($true)
                if (-not $resolved) { throw "Cannot resolve target link: $next" }
                $current = $resolved.FullName
                continue
            }
        }
        $current = $next
    }
    return [System.IO.Path]::GetFullPath($current)
}

function Resolve-SafeTargetPath {
    param([string]$Root, [string]$Relative, [string]$Purpose)
    if ([System.IO.Path]::IsPathRooted($Relative)) {
        throw "$Purpose path must be target-relative"
    }
    $candidate = [System.IO.Path]::GetFullPath((Join-Path $Root $Relative))
    $physicalRoot = Resolve-PhysicalPath $Root
    $physicalCandidate = Resolve-PhysicalPath $candidate
    if (-not (Test-IsWithinDirectory $physicalCandidate $physicalRoot)) {
        throw "$Purpose path resolves outside the export target"
    }
    return $candidate
}

function ConvertFrom-DotEnvValue {
    param([AllowNull()][string]$ValueText)
    if ($null -eq $ValueText) { return '' }
    $value = $ValueText.Trim()
    if ($value.Length -ge 2 -and ($value[0] -eq '"' -or $value[0] -eq "'")) {
        $quote = $value[0]
        $result = New-Object System.Text.StringBuilder
        $escaped = $false
        for ($i = 1; $i -lt $value.Length; $i++) {
            $char = $value[$i]
            if ($escaped) {
                [void]$result.Append($char)
                $escaped = $false
            } elseif ($char -eq '\') {
                $escaped = $true
            } elseif ($char -eq $quote) {
                return $result.ToString()
            } else {
                [void]$result.Append($char)
            }
        }
        return $result.ToString()
    }
    # dotenv treats a # after whitespace as an inline comment for an unquoted value.
    return ($value -replace '\s+#.*$', '').Trim()
}

function ConvertFrom-DotEnvRawValue {
    param([AllowNull()][string]$ValueText)
    if ($null -eq $ValueText) { return '' }
    $value = $ValueText.Trim()
    if ($value.Length -ge 2 -and ($value[0] -eq '"' -or $value[0] -eq "'")) {
        $quote = $value[0]
        $result = New-Object System.Text.StringBuilder
        $escaped = $false
        for ($i = 1; $i -lt $value.Length; $i++) {
            $char = $value[$i]
            if ($escaped) {
                [void]$result.Append('\')
                [void]$result.Append($char)
                $escaped = $false
            } elseif ($char -eq '\') {
                $escaped = $true
            } elseif ($char -eq $quote) {
                return $result.ToString()
            } else {
                [void]$result.Append($char)
            }
        }
        if ($escaped) { [void]$result.Append('\') }
        return $result.ToString()
    }
    return ($value -replace '\s+#.*$', '').Trim()
}

function New-RedactedLeakHit {
    param([ValidateSet('path', 'content')][string]$Kind,
          [ValidateSet('literal', 'word')][string]$MatchType)
    # Never echo the matched token or path: either can itself be the credential. The manifest
    # remains the local debugging source; terminal and CI transcripts stay safe to share.
    return "exported $Kind contains configured private $MatchType (details withheld)"
}

function Get-DecodedTextCandidates {
    param([string]$Path)
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $seen = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($encoding in @(
        [System.Text.Encoding]::UTF8,
        [System.Text.Encoding]::Unicode,
        [System.Text.Encoding]::BigEndianUnicode,
        [System.Text.Encoding]::UTF32,
        [System.Text.UTF32Encoding]::new($true, $true)
    )) {
        $text = $encoding.GetString($bytes)
        if ($seen.Add($text)) { Write-Output $text }
    }
}

if ($SelfTestLeakMatcher) {
    $probeRoot = Join-Path ([System.IO.Path]::GetTempPath()) 'teaching-export-probe'
    $probeGit = Join-Path $probeRoot '.git'
    $redactedProbe = New-RedactedLeakHit -Kind content -MatchType literal
    $cases = @(
        @('real .git child is skipped', (Test-IsWithinDirectory (Join-Path $probeGit 'config') $probeGit), $true),
        @('.githooks is scanned', (Test-IsWithinDirectory (Join-Path $probeRoot '.githooks/hook.ps1') $probeGit), $false),
        @('.gitignore is scanned', (Test-IsWithinDirectory (Join-Path $probeRoot '.gitignore') $probeGit), $false),
        @('case-distinct sibling obeys the host filesystem',
          (Test-IsWithinDirectory (Join-Path $probeRoot.ToUpperInvariant() 'private.txt') $probeRoot),
          ([System.IO.Path]::DirectorySeparatorChar -eq '\')),
        @('bracket secret matches literally', (Test-LiteralContains 'prefix secret[abc]token123 suffix' 'secret[abc]token123'), $true),
        @('bracket secret is not a wildcard', (Test-LiteralContains 'prefix secretatoken123 suffix' 'secret[abc]token123'), $false),
        @('unquoted dotenv comment is stripped', (ConvertFrom-DotEnvValue 'secretvalue123 # production'), 'secretvalue123'),
        @('quoted dotenv hash is preserved', (ConvertFrom-DotEnvValue '"secret#value123" # production'), 'secret#value123'),
        @('escaped dotenv quote is not a terminator', (ConvertFrom-DotEnvValue '"prefix\"secretvalue123"'), 'prefix"secretvalue123'),
        @('private prefix after underscore matches', ('EVAL_IGOR_TEMP' -match '(?<![A-Za-z0-9])IGOR'), $true),
        @('private prefix inside ordinary word does not match', ('RIGOR' -match '(?<![A-Za-z0-9])IGOR'), $false),
        @('leak report redacts the secret', (Test-LiteralContains $redactedProbe 'secretvalue123'), $false)
    )
    $failed = @($cases | Where-Object { $_[1] -ne $_[2] })
    if ($failed.Count -gt 0) {
        $failed | ForEach-Object { Write-Error "Leak matcher self-test failed: $($_[0])" }
        throw "Leak matcher self-test failed ($($failed.Count)/$($cases.Count))"
    }
    Write-Host "LEAK MATCHER SELF-TEST VALID ($($cases.Count)/$($cases.Count))"
    return
}

# --- load -------------------------------------------------------------------------------

if (-not (Test-Path -LiteralPath $Manifest)) { throw "Manifest not found: $Manifest" }
$manifestDir = Split-Path -Parent (Resolve-Path -LiteralPath $Manifest)
$m = Get-Content -LiteralPath $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json

$sourceRoot = Resolve-Path -LiteralPath (Join-Path $manifestDir $m.source)
if (-not (Test-Path -LiteralPath $sourceRoot)) { throw "Source not found: $sourceRoot" }

$targetRoot = Resolve-PhysicalPath $Target
$sourcePhysical = Resolve-PhysicalPath $sourceRoot.Path
$sourceSegments = $sourcePhysical -split '[\\/]'
if ($sourceSegments -contains '.git') {
    throw "Source .git cannot be exported; choose the repository working tree as the source"
}
if (Test-IsWithinDirectory $targetRoot $sourcePhysical) {
    throw "Target must be outside the source tree to prevent recursive self-copy: $Target"
}

if (-not $WhatIf -and (Test-Path -LiteralPath $Target)) {
    $existing = @(Get-ChildItem -LiteralPath $Target -Force)
    if ($existing.Count -gt 0) {
        throw "Target must be new or empty (found $($existing.Count) item(s)): $Target"
    }
}

Write-Host ""
Write-Host "=== teaching-edition export: $($m.name) ===" -ForegroundColor Cyan
Write-Host "source : [resolved from manifest; path withheld]"
Write-Host "target : [path withheld]$(if ($WhatIf) { '   [WhatIf - nothing will be written]' })"
Write-Host ""

# Optional manifest keys. Set-StrictMode turns a missing property into a hard error, so every
# optional list goes through here - a manifest should not have to spell out the keys it does
# not use.
function Get-ManifestList {
    param($Obj, [string]$Name)
    if ($Obj -and ($Obj.PSObject.Properties.Name -contains $Name)) { return @($Obj.$Name) }
    return @()
}

# --- exclusion matching -----------------------------------------------------------------

# Path segments that are never copied, wherever they appear in the tree.
$excludeDirs = Get-ManifestList $m "excludeAnywhere"
# Repo-relative prefixes that are never copied.
$excludePaths = Get-ManifestList $m "exclude" | ForEach-Object { $_.TrimEnd('/', '\') }

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
        throw "Required include path missing in source: $inc"
    }

    $items = if (Test-Path -LiteralPath $src -PathType Leaf) {
        @(Get-Item -LiteralPath $src -Force)
    } else {
        Get-ChildItem -LiteralPath $src -Recurse -File -Force
    }

    foreach ($item in $items) {
        $rel = $item.FullName.Substring($sourceRoot.Path.Length).TrimStart('\', '/')
        $hit = Test-Excluded -Rel $rel
        if ($hit) { $excluded.Add("$rel   [$hit]"); continue }

        $relSlash = $rel -replace '\\', '/'
        if ($relSlash -eq '.git' -or $relSlash.StartsWith('.git/')) {
            throw "Source .git cannot be exported; add .git to excludeAnywhere"
        }

        if (-not (Test-IsWithinDirectory (Resolve-PhysicalPath $item.FullName) $sourcePhysical)) {
            throw "Required include resolves outside the source tree: $inc"
        }

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

# Export-only line transforms remove source-owner catalog rows whose underlying assets are
# intentionally excluded from a fresh shell. They are path-scoped so a token in ordinary prose is
# never deleted globally.
$lineTransformCount = 0
if (-not $WhatIf) {
    foreach ($rule in (Get-ManifestList $m "lineTransforms")) {
        $dest = Resolve-SafeTargetPath $Target ([string]$rule.path) 'Line-transform'
        if (-not (Test-Path -LiteralPath $dest -PathType Leaf)) {
            throw "Line-transform target missing: $($rule.path)"
        }
        $replacement = if ($rule.PSObject.Properties.Name -contains 'replacement') {
            [string]$rule.replacement
        } else { '' }
        $lines = [System.IO.File]::ReadAllLines($dest)
        $changed = $false
        $output = New-Object System.Collections.Generic.List[string]
        foreach ($line in $lines) {
            if ($line.Contains([string]$rule.contains)) {
                $changed = $true
                $lineTransformCount++
                if ($replacement.Length -gt 0) { $output.Add($replacement) }
            } else {
                $output.Add($line)
            }
        }
        if (-not $changed) {
            throw "Line-transform anchor missing in $($rule.path): $($rule.contains)"
        }
        [System.IO.File]::WriteAllLines(
            $dest,
            $output,
            (New-Object System.Text.UTF8Encoding($false))
        )
    }
}

# --- structure-only folders -------------------------------------------------------------
# "Drop all the files, keep the structures." A newcomer needs to SEE where things go -
# _artifacts/, _bmad-output/ and friends are part of how the system is taught - but none of
# the content belongs to them. So the directory tree is recreated and every file is dropped.
# Each folder gets a .gitkeep, or git will not track an empty directory and the structure
# silently disappears on clone - which would defeat the whole point.

$structureDirs = 0
if (-not $WhatIf) {
    foreach ($rel in (Get-ManifestList $m "keepStructure")) {
        $src = Join-Path $sourceRoot $rel
        if (-not (Test-Path -LiteralPath $src)) { continue }
        $dirs = @(Get-Item -LiteralPath $src) + @(Get-ChildItem -LiteralPath $src -Recurse -Directory -Force)
        foreach ($d in $dirs) {
            $r = $d.FullName.Substring($sourceRoot.Path.Length).TrimStart('\', '/')
            $dest = Resolve-SafeTargetPath $Target $r 'Structure'
            if (-not (Test-Path -LiteralPath $dest)) {
                New-Item -ItemType Directory -Path $dest -Force | Out-Null
            }
            Set-Content -LiteralPath (Join-Path $dest '.gitkeep') -Value '' -NoNewline -Encoding UTF8
            $structureDirs++
        }
    }
    # Top-level only: the folder exists, nothing inside it (its real subfolders are named
    # after the owner's projects, so recreating them would leak the names).
    foreach ($rel in (Get-ManifestList $m "emptyDirs")) {
        $dest = Resolve-SafeTargetPath $Target ([string]$rel) 'Empty-directory'
        if (-not (Test-Path -LiteralPath $dest)) {
            New-Item -ItemType Directory -Path $dest -Force | Out-Null
        }
        Set-Content -LiteralPath (Join-Path $dest '.gitkeep') -Value '' -NoNewline -Encoding UTF8
        $structureDirs++
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
              '.sh', '.js', '.ts', '.html', '.css', '.xml', '.patch', '.jsonl', '.gitignore', '.gitattributes',
              '.env.example', '.editorconfig', '.roomodes')
$subCount = 0
$subFiles = 0

$subList = @(Get-ManifestList $m "substitutions")
if (-not $WhatIf -and $subList.Count -gt 0) {
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    foreach ($file in Get-ChildItem -LiteralPath $Target -Recurse -File -Force) {
        $relTextPath = $file.FullName.Substring(([System.IO.Path]::GetFullPath($Target)).Length).TrimStart('\', '/') -replace '\\', '/'
        $isExtensionlessGate = $relTextPath.StartsWith('.githooks/') -or
            $relTextPath.StartsWith('.agents/scripts/git-hooks/')
        if ($TEXT_EXT -notcontains $file.Extension.ToLower() -and
            $TEXT_EXT -notcontains $file.Name.ToLower() -and
            -not $isExtensionlessGate) { continue }
        $text = [System.IO.File]::ReadAllText($file.FullName)
        $orig = $text
        foreach ($s in $subList) {
            # Entries with no "from" are inline `_note` comments documenting the rows below
            # them - JSON has no comment syntax and this table needs its reasoning attached.
            if ($s.PSObject.Properties.Name -notcontains 'from') { continue }
            # "word": true matches whole words only. Required for short names that are substrings
            # of ordinary words - a plain replace of "Mac" corrupts "Machine", and "Igor" hides
            # inside "Rigor". Without this the choice is a corrupted export or a missed name.
            $isWord = ($s.PSObject.Properties.Name -contains 'word') -and $s.word
            if ($isWord) {
                $pattern = '(?<![A-Za-z0-9])' + [regex]::Escape($s.from)
                $n = ([regex]::Matches($text, $pattern)).Count
                if ($n -gt 0) {
                    $text = [regex]::Replace($text, $pattern, $s.to)
                    $subCount += $n
                }
            }
            elseif ($text.Contains($s.from)) {
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
foreach ($t in (Get-ManifestList $m "transforms")) {
    $replacement = Join-Path $manifestDir $t.replaceWith
    if (-not (Test-Path -LiteralPath $replacement)) {
        throw "Transform replacement missing: $($t.replaceWith) (for $($t.path))"
    }
    $transformed.Add("$($t.path)  <-  $($t.replaceWith)")
    if ($WhatIf) { continue }

    $dest = Resolve-SafeTargetPath $Target ([string]$t.path) 'Transform'
    $destDir = Split-Path -Parent $dest
    if (-not (Test-Path -LiteralPath $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    Copy-Item -LiteralPath $replacement -Destination $dest -Force
}

# --- site map -----------------------------------------------------------------------------
# The exported tree is NOT the source tree - folders were dropped, emptied, and renamed. A
# repo-map copied across would describe a repo that does not exist, which is worse than none
# because it is the file a newcomer trusts to find things. Regenerate it against the export.
# Runs BEFORE the leak scan on purpose, so the regenerated map is scanned like everything else.

$pythonCommand = $null
$mapPath = Join-Path $Target 'docs/repo-map.md'
if (-not $WhatIf -and (Test-Path -LiteralPath $mapPath)) {
    $gen = Join-Path $sourceRoot '.agents/scripts/generate_repo_map.py'
    if (Test-Path -LiteralPath $gen) {
        foreach ($candidate in @('python3', 'python', 'py')) {
            $resolved = Get-Command $candidate -ErrorAction SilentlyContinue
            if ($resolved) { $pythonCommand = $resolved.Source; break }
        }
        if (-not $pythonCommand) { throw "Python not found (tried python3, python, py)" }
        Write-Host "-- site map --" -ForegroundColor Yellow
        & $pythonCommand $gen --root $Target --output $mapPath 2>&1 | Select-Object -Last 2 |
            ForEach-Object { Write-Host "   $_" }
        if ($LASTEXITCODE -ne 0) { throw "repo-map generation failed (rc=$LASTEXITCODE)" }
    } else {
        throw "generate_repo_map.py not found: $gen"
    }
}

# Main's live SOP links to the generated doc graph. The source graph describes files deliberately
# omitted from a teaching shell, so copy neither source artifact; rebuild both against the exported
# `.agents/` + `docs/` tree before privacy and link validation.
$generateDocGraph = $false
if ($m.PSObject.Properties.Name -contains 'generateDocGraph') {
    $generateDocGraph = [bool]$m.generateDocGraph
}
if (-not $WhatIf -and $generateDocGraph) {
    if (-not $pythonCommand) {
        foreach ($candidate in @('python3', 'python', 'py')) {
            $resolved = Get-Command $candidate -ErrorAction SilentlyContinue
            if ($resolved) { $pythonCommand = $resolved.Source; break }
        }
    }
    if (-not $pythonCommand) { throw "Python not found (tried python3, python, py)" }
    $docGen = Join-Path $Target '.agents/scripts/generate_doc_graph.py'
    if (-not (Test-Path -LiteralPath $docGen)) {
        throw "generate_doc_graph.py not found: $docGen"
    }
    $docGraphPath = Join-Path $Target 'docs/doc-graph.md'
    $docGraphJsonPath = Join-Path $Target 'docs/doc-graph.json'
    Write-Host "-- doc graph --" -ForegroundColor Yellow
    & $pythonCommand $docGen --lobby $Target --output $docGraphPath --json $docGraphJsonPath 2>&1 |
        Select-Object -Last 3 | ForEach-Object { Write-Host "   $_" }
    if ($LASTEXITCODE -ne 0) { throw "doc-graph generation failed (rc=$LASTEXITCODE)" }
}

# --- report -----------------------------------------------------------------------------

Write-Host "copied      : $($copied.Count) files"
Write-Host "excluded    : $($excluded.Count) files"
Write-Host "structure   : $structureDirs empty folder(s) kept"
Write-Host "substituted : $subCount token(s) across $subFiles file(s)"
Write-Host "line-pruned : $lineTransformCount source-only catalog row(s)"
Write-Host "transformed : $($transformed.Count) files"
Write-Host ""
Write-Host "-- transforms --" -ForegroundColor Yellow
$transformed | ForEach-Object { Write-Host "   $_" }
Write-Host ""

# --- leak scan (never optional) ---------------------------------------------------------

Write-Host ""
Write-Host "-- leak scan --" -ForegroundColor Yellow

$needles = @(Get-ManifestList $m.leakScan "literals")

# Short names that are substrings of ordinary words need whole-word matching, or the scan
# cries wolf ("Igor" inside "Rigor") - and a scanner that cries wolf gets muted, which is
# the same outcome as having no scanner.
$wordNeedles = @(Get-ManifestList $m.leakScan "wordLiterals")
$wholeWordNeedles = @(Get-ManifestList $m.leakScan "wholeWordLiterals")

# Every VALUE from the live .env, so a key that was pasted into a doc is caught even
# though the .env itself was excluded.
$envPath = Join-Path $sourceRoot '.env'
if (Test-Path -LiteralPath $envPath) {
    foreach ($line in Get-Content -LiteralPath $envPath) {
        if ($line -match '^\s*[#;]') { continue }
        if ($line -notmatch '=') { continue }
        $parts = $line -split '=', 2
        $keyName = $parts[0].Trim()
        $valueText = $parts[1]
        $secretNamed = $keyName -match '(?i)(^|[_-])(SECRET|TOKEN|PASSWORD|PASS|API[_-]?KEY|PRIVATE[_-]?KEY|CREDENTIAL)([_-]|$)'
        $values = @(
            (ConvertFrom-DotEnvValue $valueText),
            (ConvertFrom-DotEnvRawValue $valueText)
        ) | Select-Object -Unique
        foreach ($val in $values) {
            # Ordinary short values (true, local, test) are too noisy to scan globally, but a
            # secret-named key is an explicit declaration. Values under four characters cannot be
            # matched globally without turning ordinary text into false leaks, so fail immediately
            # instead of silently dropping them or weakening the privacy boundary.
            if ($secretNamed -and $val.Length -gt 0 -and $val.Length -lt 4) {
                throw "Secret-named environment value is too short for safe leak matching"
            }
            if (($secretNamed -and $val.Length -ge 4) -or $val.Length -ge 12) {
                $needles += $val
            }
        }
    }
}

$scanRoot = if ($WhatIf) { $null } else { [System.IO.Path]::GetFullPath($Target) }
$hits = @()
$scannedGitRepo = $false
if ($scanRoot -and (Test-Path -LiteralPath $scanRoot)) {
    # Every file the export WROTE is scanned - there is no exemption list, because the first
    # version of this script had one and the exemption was the leak.
    #
    # The single thing skipped is the DESTINATION repo's own .git/. It is not export output:
    # nothing inside it is ever committed, it IS the repository. Its reflog also necessarily
    # records the committer identity of whoever ran the export, which no manifest can scrub,
    # so leaving it in makes the scan permanently red - and a scan that is always red gets
    # muted, which is the same as having no scan. Its HISTORY is a real but separate concern
    # with a separate remedy; it is reported below rather than silently dropped.
    $gitDir = Join-Path ([System.IO.Path]::GetFullPath($scanRoot)) '.git'
    $scannedGitRepo = Test-Path -LiteralPath $gitDir

    foreach ($file in Get-ChildItem -LiteralPath $scanRoot -Recurse -File -Force) {
        if (Test-IsWithinDirectory $file.FullName $gitDir) { continue }
        $rel = $file.FullName.Substring($scanRoot.Length).TrimStart('\', '/')

        # PATHS are scanned, not only contents. The substitution pass rewrites what is INSIDE
        # a file and never touches its NAME, so a file called security_team_<client>.md ships
        # a client name in plain sight while its scrubbed contents sail straight through a
        # content-only scan. That is not hypothetical - it is exactly how three such files got
        # past this guard and into a pushed repo.
        $relSlash = $rel -replace '\\', '/'
        foreach ($n in $needles) {
            if (Test-LiteralContains $relSlash $n) {
                $hits += New-RedactedLeakHit -Kind path -MatchType literal
            }
        }
        foreach ($n in $wordNeedles) {
            if ($relSlash -match ('(?<![A-Za-z0-9])' + [regex]::Escape($n))) {
                $hits += New-RedactedLeakHit -Kind path -MatchType word
            }
        }
        foreach ($n in $wholeWordNeedles) {
            if ($relSlash -cmatch ('(?<![A-Za-z0-9])' + [regex]::Escape($n) + '(?![A-Za-z0-9])')) {
                $hits += New-RedactedLeakHit -Kind path -MatchType word
            }
        }

        foreach ($text in (Get-DecodedTextCandidates $file.FullName)) {
            if (-not $text) { continue }
            foreach ($n in $needles) {
                if (Test-LiteralContains $text $n) {
                    $hits += New-RedactedLeakHit -Kind content -MatchType literal
                }
            }
            foreach ($n in $wordNeedles) {
                if ($text -match ('(?<![A-Za-z0-9])' + [regex]::Escape($n))) {
                    $hits += New-RedactedLeakHit -Kind content -MatchType word
                }
            }
        }
        # Jira keys are short enough that decoding UTF-8 bytes as every other supported
        # encoding can manufacture a coincidental three-letter match. They are operational
        # text, so check the actual UTF-8 view once; the longer privacy needles above still
        # receive the multi-encoding scan needed for UTF-16/32 secrets.
        $utf8Text = [System.Text.Encoding]::UTF8.GetString([System.IO.File]::ReadAllBytes($file.FullName))
        foreach ($n in $wholeWordNeedles) {
            if ($utf8Text -cmatch ('(?<![A-Za-z0-9])' + [regex]::Escape($n) + '(?![A-Za-z0-9])')) {
                $hits += New-RedactedLeakHit -Kind content -MatchType word
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
    Write-Host "   clean - $($needles.Count) needles, 0 hits (contents AND paths)" -ForegroundColor Green
}

# --- product contract (never optional) ----------------------------------------------------

if (-not $WhatIf) {
    if (-not $pythonCommand) {
        foreach ($candidate in @('python3', 'python', 'py')) {
            $resolved = Get-Command $candidate -ErrorAction SilentlyContinue
            if ($resolved) { $pythonCommand = $resolved.Source; break }
        }
    }
    if (-not $pythonCommand) { throw "Python not found (tried python3, python, py)" }
    $validator = Join-Path $sourceRoot '.agents/scripts/validate_teaching_edition.py'
    if (-not (Test-Path -LiteralPath $validator)) { throw "Teaching validator not found: $validator" }
    Write-Host ""
    Write-Host "-- teaching-shell contract --" -ForegroundColor Yellow
    & $pythonCommand $validator $scanRoot
    if ($LASTEXITCODE -ne 0) { throw "teaching-shell validation failed (rc=$LASTEXITCODE)" }
}

if (-not $WhatIf -and $scannedGitRepo) {
    Write-Host ""
    Write-Host "   note: the target is an existing git repo. This scan covers the WORKING TREE." -ForegroundColor DarkYellow
    Write-Host "   Earlier commits are not scanned and a force-push does not erase them - an" -ForegroundColor DarkYellow
    Write-Host "   unreachable commit stays fetchable by SHA until the host garbage-collects." -ForegroundColor DarkYellow
    Write-Host "   If a previous export leaked, recreating the repo is the only certain fix." -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "done." -ForegroundColor Cyan
