---
description: Synchronize VS Code configurations (extensions, User settings.json, and keybindings.json) between this PC's two VS Code installs - the Windows-native one and the Ubuntu/WSL one - with automatic cross-platform shortcut translation.
platforms: [opencode, antigravity, claude, codex]
---

# /smh-sync-vscode — VS Code Environment Sync

> **Rules in force for this command:**
> - `.agents/rules/git-policy.md` — explicit paths only (never `git add -A`/`.`/`-u`), never push `main`, never force-push
> - `.agents/rules/sop-currency.md` — **if this run changes how the operator invokes this command, update `docs/_scc_sops_prds/workflows_testing_SOP.md` §3 in the same commit**
> - `.agents/rules/constitution.md` — never commit secrets, API keys, or credentials to git

Synchronizes day-to-day VS Code editor setups between the two VS Code installs on this PC: the
Windows-native one and the one on the Ubuntu side inside WSL2. Same mechanism as before; the two
endpoints became two sides of one PC when SCC-376 put the working environment in WSL2.

| What | How it travels | Storage Location |
|---|---|---|
| **Workspace Settings** | Git (automatic) | `.vscode/settings.json` (Zoo permissions, worktrees, auto-approvals) |
| **Editor Bundle** | Git via this command | `docs/migrations/vscode_sync/` (extensions, user settings, keybindings) |
| **API Keys & Models** | 1-Click Private Export | Zoo Code SQLite database (`state.vscdb`) — **never in git** |

---

## Usage

### 1. Check Drift (`status`)
Compare current local VS Code state against the repository bundle:
```bash
python3 .agents/scripts/vscode_sync.py status
# Windows side:
python .agents\scripts\vscode_sync.py status
```

### 2. Export to Repo (`export`)
Run on the side where you just updated extensions or settings (e.g. the Ubuntu side):
```bash
python3 .agents/scripts/vscode_sync.py export
# Windows side:
python .agents\scripts\vscode_sync.py export
```
This updates:
- `docs/migrations/vscode_sync/extensions.txt` (and `antigravity-extension-ids.txt`)
- `docs/migrations/vscode_sync/settings.json`
- `docs/migrations/vscode_sync/keybindings.json`

Stage with explicit paths and commit under the active task or standing push ticket:
```bash
git add docs/migrations/vscode_sync/ docs/migrations/antigravity_extensions/antigravity-extension-ids.txt
git commit -m "chore(SCC-186): update VS Code sync bundle [sop-ok]"
```

### 3. Import to Local VS Code (`import`)
Run on the destination side (e.g. the Windows side):
```bash
python3 .agents/scripts/vscode_sync.py import
# Windows side:
python .agents\scripts\vscode_sync.py import
```
This:
- Backs up existing local user settings and keybindings (`.pre-sync.bak`).
- Installs any missing extensions via `code --install-extension`.
- Applies the user settings.
- Applies keybindings with automatic modifier translation (`cmd` ↔ `ctrl`).

---

## ⛔ Private API Keys & Provider Profiles

Zoo Code's custom models and API keys (such as Command Code Sol) live in VS Code's internal database (`state.vscdb`) and **cannot be committed to git**.

To sync provider settings:
1. On the source side: Open **Zoo Code → Settings (Gear Icon) → Export** (saves JSON).
2. Transfer the JSON securely (or copy text) to the destination side.
3. On the destination side: Open **Zoo Code → Settings → Import** (select JSON).
4. Delete the transferred export file when done.
