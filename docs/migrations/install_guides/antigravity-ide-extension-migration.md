# Antigravity IDE Extension Migration — Windows PC to Mac

Use this guide when the Windows PC has the complete Antigravity IDE extension set and the Mac is missing some of those extensions.

The reliable migration unit is a small text manifest containing one extension ID per line. Do **not** copy Antigravity's `extensions.json` or its extension folders between operating systems: those contain machine-specific paths and platform packages such as Windows x64 or macOS ARM64.

This procedure migrates **Antigravity IDE editor extensions**. It does not migrate Antigravity agent plugins, Gemini skills, MCP servers, extension logins, credentials, or external tools such as Python, PowerShell, language servers, and compilers.

## What will travel

The manifest looks like this:

```text
anthropic.claude-code
github.vscode-github-actions
meta.pyrefly
ms-python.python
openai.chatgpt
```

These `publisher.extension` IDs are portable. Antigravity IDE uses each ID to download the package appropriate for the destination operating system.

The manifest contains no credentials. It is safe to attach to a private conversation or store in this private repository. Still inspect it before uploading: it should contain extension IDs only.

## Part 1 — Export the inventory on the Windows PC

Open **PowerShell** in the Windows copy of `Sudo_Hatter_Command`.

### 1. Locate Antigravity IDE's command

Try the normal command first:

```powershell
agy-ide --help
```

If that works, set:

```powershell
$AgyIde = (Get-Command agy-ide).Source
```

If PowerShell says `agy-ide` is not recognized, locate the installed command with:

```powershell
$Candidates = @(
    "$env:LOCALAPPDATA\Programs\Antigravity IDE\bin\antigravity-ide.cmd",
    "$env:ProgramFiles\Antigravity IDE\bin\antigravity-ide.cmd"
)

$AgyIde = $Candidates |
    Where-Object { Test-Path $_ } |
    Select-Object -First 1

if (-not $AgyIde) {
    throw "Antigravity IDE command not found. Re-run the Antigravity IDE installer and enable the agy-ide command-line tool."
}

& $AgyIde --help
```

Do not substitute `agy`. In current Antigravity releases, `agy` is the separate agent CLI; `agy-ide` controls the editor and its extensions.

### 2. Export portable extension IDs

From the `Sudo_Hatter_Command` repository root, run:

```powershell
$ManifestDirectory = Join-Path (Get-Location) "docs\migrations\antigravity_extensions"
$Manifest = Join-Path $ManifestDirectory "antigravity-extension-ids.txt"

New-Item -ItemType Directory -Force -Path $ManifestDirectory | Out-Null

$ExtensionIds = & $AgyIde --list-extensions |
    Where-Object { $_ -match '^[A-Za-z0-9][A-Za-z0-9._-]*\.[A-Za-z0-9][A-Za-z0-9._-]*$' } |
    Sort-Object -Unique

if (-not $ExtensionIds) {
    throw "No extension IDs were exported. Stop and check the Antigravity IDE command before uploading anything."
}

$Utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($Manifest, [string[]]$ExtensionIds, $Utf8WithoutBom)

Write-Host "Exported $($ExtensionIds.Count) extension IDs to:"
Write-Host $Manifest
Get-Content $Manifest
```

The resulting file is:

```text
docs/migrations/antigravity_extensions/antigravity-extension-ids.txt
```

Export **without versions** for a Windows-to-Mac migration. A version-pinned list can force an old release or one that has no compatible Mac package.

### 3. Inspect before uploading

```powershell
Get-Content $Manifest
```

Every nonblank line must resemble `publisher.extension`. Stop if the file contains filesystem paths, JSON, tokens, passwords, command errors, or log output.

## Part 2 — Upload the manifest

There are two safe routes. Use the repository route for a durable inventory that travels during normal PC/Mac switching. Use the direct-upload route for a one-time transfer.

### Route A — Shared Git repository (recommended)

The repository's Jira and branch gates still apply. Use the active SCC task branch for this migration; do not invent or type a placeholder ticket key.

Stage only the manifest:

```powershell
git status --short -- docs/migrations/antigravity_extensions/antigravity-extension-ids.txt
git add -- docs/migrations/antigravity_extensions/antigravity-extension-ids.txt
git diff --cached --stat
git diff --cached -- docs/migrations/antigravity_extensions/antigravity-extension-ids.txt
```

Confirm that the staged diff contains only extension IDs. Then commit and push through the normal task-lane workflow. Do not use `git add .`, `git add -A`, or `git add -u`; those commands can sweep another lane's work into the commit.

On the Mac, pull or resume the repository normally. The manifest will then be available at the same repository-relative path.

### Route B — Direct file upload

Because the manifest contains IDs only, it can be transferred as an ordinary text file:

1. Attach `antigravity-extension-ids.txt` to the private conversation you will open on the Mac; or
2. Upload it to your private Google Drive and download it on the Mac; or
3. Copy it with a USB drive.

Do not transfer the entire Windows `.antigravity-ide\extensions` directory. Native Windows extension packages cannot simply be reused on Apple Silicon.

After downloading on the Mac, note the file's actual path. The commands below assume the Git route. If using a direct upload, replace the manifest path with the downloaded file's path.

## Part 3 — Compare the PC inventory with this Mac

Open Terminal on the Mac and move to the `Sudo_Hatter_Command` repository root.

This Mac's dependable Antigravity IDE command is inside the application bundle:

```bash
AGY_IDE="/Applications/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide"
MANIFEST="docs/migrations/antigravity_extensions/antigravity-extension-ids.txt"

test -x "$AGY_IDE" || { echo "Antigravity IDE command not found at $AGY_IDE"; exit 1; }
test -f "$MANIFEST" || { echo "Extension manifest not found at $MANIFEST"; exit 1; }
```

The application-bundle path is intentional. The `agy-ide` shortcut on this Mac currently points to an old installer-volume location, while the command above has been verified against the installed application.

Normalize the Windows text file, capture the Mac inventory, and calculate the difference:

```bash
tr -d '\r' < "$MANIFEST" |
  sed '/^[[:space:]]*$/d' |
  sort -u > /tmp/antigravity-pc-extension-ids.txt

"$AGY_IDE" --list-extensions |
  sed '/^[[:space:]]*$/d' |
  sort -u > /tmp/antigravity-mac-extension-ids.txt

comm -23 \
  /tmp/antigravity-pc-extension-ids.txt \
  /tmp/antigravity-mac-extension-ids.txt \
  > /tmp/antigravity-missing-on-mac.txt

echo "Extensions present on the PC but missing on this Mac:"
cat /tmp/antigravity-missing-on-mac.txt
```

The `tr -d '\r'` step removes Windows carriage returns. Without it, the Mac can misread every Windows line as a different extension ID.

If the missing list is empty, the machines already have the same extension IDs and nothing should be installed.

## Part 4 — Install only the missing extensions

First review the missing list:

```bash
cat /tmp/antigravity-missing-on-mac.txt
```

Then install each missing ID:

```bash
while IFS= read -r extension_id; do
  if [ -n "$extension_id" ]; then
    echo "Installing $extension_id"
    "$AGY_IDE" --install-extension "$extension_id" || \
      echo "FAILED: $extension_id"
  fi
done < /tmp/antigravity-missing-on-mac.txt
```

Antigravity may ask you to trust a publisher. Review the publisher rather than approving blindly.

Restart Antigravity IDE after installation.

## Part 5 — Verify the result

Rebuild the Mac inventory and check the difference again:

```bash
"$AGY_IDE" --list-extensions |
  sed '/^[[:space:]]*$/d' |
  sort -u > /tmp/antigravity-mac-extension-ids-after.txt

echo "PC extensions still missing on the Mac:"
comm -23 \
  /tmp/antigravity-pc-extension-ids.txt \
  /tmp/antigravity-mac-extension-ids-after.txt
```

No output after the heading means all portable IDs were installed.

Also inspect the IDE's Extensions panel. Some extensions require a fresh login, a workspace reload, or an external dependency before they become functional.

## Expected exceptions

An extension can remain missing for legitimate reasons:

- It is unavailable from Antigravity IDE's configured extension gallery.
- The publisher does not provide a macOS ARM64 package.
- It is application-scoped, organization-managed, or no longer published.
- It was installed from a private `.vsix` file that the new machine cannot access.
- Its ID changed or the extension was retired.

Do not solve those cases by copying the Windows extension directory. Record each failed ID and install an official Mac-compatible release or `.vsix` from the publisher.

## What this does not migrate

Reinstall these separately when required:

- Extension account sessions and OAuth logins
- API keys, tokens, and credentials
- Extension-specific machine state not covered by settings sync
- Python, Node.js, Java, PowerShell, Ruby, Go, or other runtimes
- Language servers, compilers, debuggers, and command-line tools
- Antigravity agent plugins, rules, workflows, skills, and MCP configuration

Those are different migration surfaces. Keep secrets in the established secrets migration process rather than adding them to the extension manifest.

## Troubleshooting

### `agy-ide` is not recognized on Windows

Re-run the Antigravity IDE installer and enable its command-line tool, or use the direct `antigravity-ide.cmd` discovery block in Part 1.

### The Mac reports the manifest is missing

Confirm the upload completed. For the Git route, pull or resume the repository and run:

```bash
ls -l docs/migrations/antigravity_extensions/antigravity-extension-ids.txt
```

For a direct upload, change `MANIFEST` to the downloaded file's real path.

### Every extension appears missing

Re-run the normalization command in Part 3. This usually means the Windows carriage returns were not removed or the wrong local inventory was compared.

### One extension fails while the rest install

Keep going. The loop reports `FAILED: publisher.extension` and continues with the remaining extensions. Investigate only the failed IDs afterward.

### The list includes extensions you do not want on both machines

Remove those IDs from the manifest before uploading, or maintain a smaller cross-machine baseline file. The export is an inventory, not an obligation to install every OS-specific tool everywhere.

## Authoritative references

- [Google's Antigravity IDE onboarding](https://codelabs.developers.google.com/getting-started-agy-ide) documents extension setup and configuration of the `agy-ide` command-line tool.
- [VS Code command-line extension management](https://code.visualstudio.com/docs/configure/command-line) documents the `--list-extensions`, `--show-versions`, and `--install-extension` interface inherited by Antigravity IDE and verified against the installed Mac application.
