# VS Code Extension Migration + Zoo Code Transition — Mac and Windows PC

Use this guide to consolidate day-to-day agent work in **VS Code** on either machine, carrying the
extension set across with the portable IDs manifest, and to complete the **Roo Code → Zoo Code**
transition on each machine. Antigravity IDE is demoted (its "Always Proceed still prompts every
command" bug is upstream and unfixable from our side); Roo Code was archived upstream and is frozen
at v3.54.

The reliable migration unit is a small text manifest containing one extension ID per line. Do
**not** copy an editor's `extensions.json` or its extension folders between operating systems:
those contain machine-specific paths and platform packages such as Windows x64 or macOS ARM64.

This procedure migrates **editor extensions**. It does not migrate extension logins, credentials,
MCP servers, or external tools such as Python, PowerShell, language servers, and compilers.

## Part 0 — BEFORE uninstalling Roo Code or Antigravity (each machine, once)

1. Open the **Roo Code settings panel → Export**. The export file **carries API keys** — keep it
   private, **never commit it**, and delete it after the import.
2. Install **Zoo Code** (`ZooCodeOrganization.zoo-code`) in VS Code, then **Import** that file in
   Zoo Code's settings panel. Zoo is the coordinated community continuation of Roo (biweekly
   releases) and deliberately keeps the `.roo/*` paths and settings structure.
3. Zoo's **auto-approve master toggle + tiles are per-machine extension state** — enable them once
   on each machine. The command allowlists themselves travel via git
   (`zoo-code.allowedCommands` / `zoo-code.deniedCommands` in the tracked `.vscode/settings.json`).

## What will travel

The manifest looks like this:

```text
anthropic.claude-code
github.vscode-github-actions
meta.pyrefly
ms-python.python
openai.chatgpt
```

These `publisher.extension` IDs are portable. VS Code uses each ID to download the package
appropriate for the destination operating system.

The manifest contains no credentials. It is safe to store in this private repository. Still
inspect it before committing: it should contain extension IDs only.

The manifest lives at:

```text
docs/migrations/antigravity_extensions/antigravity-extension-ids.txt
```

(The folder keeps its historical name; the IDs inside are editor-agnostic `publisher.extension`
strings, exported originally from Antigravity and equally valid for VS Code.)

## Part 1 — Locate the `code` command

**Mac** — if `code --version` fails in Terminal, either run VS Code's
**⇧⌘P → "Shell Command: Install 'code' command in PATH"**, or use the bundle path directly:

```bash
CODE="/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
"$CODE" --version
```

**Windows PC** — the installer puts `code` on PATH by default:

```powershell
code --version
```

If it is not recognized, re-run the VS Code installer and tick **Add to PATH**.

## Part 2 — Export / refresh the inventory on the source machine

From the `Sudo_Hatter_Command` repository root on the machine whose extension set is current:

**Windows (PowerShell):**

```powershell
$ManifestDirectory = Join-Path (Get-Location) "docs\migrations\antigravity_extensions"
$Manifest = Join-Path $ManifestDirectory "antigravity-extension-ids.txt"

New-Item -ItemType Directory -Force -Path $ManifestDirectory | Out-Null

$ExtensionIds = code --list-extensions |
    Where-Object { $_ -match '^[A-Za-z0-9][A-Za-z0-9._-]*\.[A-Za-z0-9][A-Za-z0-9._-]*$' } |
    Sort-Object -Unique

if (-not $ExtensionIds) {
    throw "No extension IDs were exported. Stop and check the code command before continuing."
}

$Utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllLines($Manifest, [string[]]$ExtensionIds, $Utf8WithoutBom)

Write-Host "Exported $($ExtensionIds.Count) extension IDs to:"
Write-Host $Manifest
Get-Content $Manifest
```

**Mac (Terminal):**

```bash
MANIFEST="docs/migrations/antigravity_extensions/antigravity-extension-ids.txt"
code --list-extensions | sort -u > "$MANIFEST"
cat "$MANIFEST"
```

Export **without versions**. A version-pinned list can force an old release or one that has no
compatible package for the destination OS.

Inspect before committing: every nonblank line must resemble `publisher.extension`. Stop if the
file contains filesystem paths, JSON, tokens, passwords, command errors, or log output. Stage only
the manifest (never `git add .` / `-A` / `-u`), commit on the active task branch, and push.

## Part 3 — Compare the manifest with the destination machine

On the destination machine, from the repository root (Mac shown; on the PC use `code` directly and
`docs\migrations\...` paths):

```bash
CODE="$(command -v code || echo "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code")"
MANIFEST="docs/migrations/antigravity_extensions/antigravity-extension-ids.txt"

test -f "$MANIFEST" || { echo "Extension manifest not found at $MANIFEST"; exit 1; }

tr -d '\r' < "$MANIFEST" |
  sed '/^[[:space:]]*$/d' |
  sort -u > /tmp/vscode-source-extension-ids.txt

"$CODE" --list-extensions |
  sed '/^[[:space:]]*$/d' |
  sort -u > /tmp/vscode-local-extension-ids.txt

comm -23 \
  /tmp/vscode-source-extension-ids.txt \
  /tmp/vscode-local-extension-ids.txt \
  > /tmp/vscode-missing-here.txt

echo "Extensions in the manifest but missing on this machine:"
cat /tmp/vscode-missing-here.txt
```

The `tr -d '\r'` step removes Windows carriage returns. Without it, a Mac can misread every
Windows line as a different extension ID.

## Part 4 — Install only the missing extensions

Review the missing list first, and **skip Antigravity-only IDs** — anything published for the
Antigravity/Gemini agent surface that has no VS Code counterpart. Then:

```bash
while IFS= read -r extension_id; do
  if [ -n "$extension_id" ]; then
    echo "Installing $extension_id"
    "$CODE" --install-extension "$extension_id" || \
      echo "FAILED: $extension_id"
  fi
done < /tmp/vscode-missing-here.txt
```

VS Code may ask you to trust a publisher. Review the publisher rather than approving blindly.
Restart VS Code after installation.

The workspace already recommends the core set in `.vscode/extensions.json`
(`anthropic.claude-code`, `ZooCodeOrganization.zoo-code`, …) — VS Code offers those on first open
even with an empty manifest.

## Part 5 — Verify the result

```bash
"$CODE" --list-extensions |
  sed '/^[[:space:]]*$/d' |
  sort -u > /tmp/vscode-local-extension-ids-after.txt

echo "Manifest extensions still missing here:"
comm -23 \
  /tmp/vscode-source-extension-ids.txt \
  /tmp/vscode-local-extension-ids-after.txt
```

No output after the heading means all portable IDs were installed. Also inspect the Extensions
panel — some extensions need a fresh login, a workspace reload, or an external dependency before
they become functional.

## Part 6 — Per-machine transition checklist (run once on each machine)

1. **Roo export → Zoo import** done BEFORE uninstalling Roo (Part 0). Delete the export file after
   import — it carries API keys.
2. **Zoo auto-approve** master toggle + tiles enabled (per-machine state; allowlists arrive via
   git).
3. **Claude Code: nothing to migrate.** The `~/.claude` store is IDE-agnostic on each machine —
   installing the `anthropic.claude-code` extension in VS Code picks up existing sessions,
   transcripts, and settings.
4. **Do NOT carry the Antigravity `git.path` shim into VS Code user settings.** It existed only to
   fix Antigravity's SCM repo list and unstacks the multi-repo view here.
5. **PC only:** confirm `git config --global core.hooksPath .githooks` is set — a fresh clone has
   **no gates at all** without it — and remember the interpreter split: **PC = `python`,
   Mac = `python3`**.
6. **Port the user-level settings from Antigravity** (per machine — user settings never travel via
   git). Antigravity's copy lives at
   `~/Library/Application Support/Antigravity IDE/User/settings.json` (Mac) /
   `%APPDATA%\Antigravity IDE\User\settings.json` (PC); VS Code's at the same path under `Code`.
   Carry over: `editor.minimap.enabled: false`, `git.confirmSync: false`,
   `scm.alwaysShowRepositories: true`, `scm.compactFolders: false`,
   `githubPullRequests.notifications`, `workbench.editor.closeOnFileDelete: true`,
   `window.customTitleBarVisibility`, `markdown-preview-enhanced.previewColorScheme`,
   `google.cloud.project`. **Do NOT carry:** `git.path` (the `git-flat-scm` shim — Antigravity SCM
   fix only), any `antigravity.*` key, any `roo-cline.*` key (retired namespace; the `zoo-code.*`
   allowlists live in the tracked workspace `.vscode/settings.json`). Also port the `cmd+alt+r`
   Source Control show-all-repos keybinding from Antigravity's `keybindings.json`; repoint
   `cmd+o cmd+o` from `roo-cline.openInNewTab` to `zoo-code.openInNewTab`.
7. Uninstall Roo Code and (when ready) Antigravity IDE.

## Expected exceptions

An extension can remain missing for legitimate reasons:

- The publisher does not provide a package for this OS/architecture.
- It is application-scoped, organization-managed, or no longer published.
- It was installed from a private `.vsix` file that the new machine cannot access.
- Its ID changed, the extension was retired, or it is Antigravity-only (skip those).

Do not solve those cases by copying an extension directory between machines. Record each failed ID
and install an official release or `.vsix` from the publisher.

## What this does not migrate

Reinstall these separately when required:

- Extension account sessions and OAuth logins
- API keys, tokens, and credentials (the Roo→Zoo export in Part 0 is the one sanctioned carrier,
  and it never enters git)
- Python, Node.js, Java, PowerShell, Ruby, Go, or other runtimes
- Language servers, compilers, debuggers, and command-line tools
- Agent rules, commands, skills, and MCP configuration (those are the toolkit's surfaces —
  `/smh-sync-agents` publishes them)

## Troubleshooting

### `code` is not recognized

Mac: install the shell command from the Command Palette, or use the application-bundle path in
Part 1. PC: re-run the VS Code installer and tick **Add to PATH**.

### Every extension appears missing

Re-run the normalization command in Part 3 — this usually means the Windows carriage returns were
not removed or the wrong local inventory was compared.

### One extension fails while the rest install

Keep going. The loop reports `FAILED: publisher.extension` and continues. Investigate only the
failed IDs afterward.

### The list includes extensions you do not want on both machines

Remove those IDs from the manifest before committing, or maintain a smaller cross-machine baseline.
The export is an inventory, not an obligation to install every OS-specific tool everywhere.

## Authoritative references

- [VS Code command-line extension management](https://code.visualstudio.com/docs/configure/command-line)
  documents the `--list-extensions`, `--show-versions`, and `--install-extension` interface.
