# VS Code Sync Bundle

This directory contains portable VS Code environment configuration files synchronized across Mac and Windows PC using `/smh-sync-vscode` (`.agents/scripts/vscode_sync.py`).

## Files in this bundle

- `extensions.txt` — Plain list of installed `publisher.extension` IDs (31 standard extensions).
- `settings.json` — User settings (minimap, word wrap, themes, auto-fetch, jupyter, and Zoo permissions).
- `keybindings.json` — Portable keybindings (e.g. `cmd+alt+r` for SCM show-all repos, Zoo Code tab shortcut). Translated automatically to `ctrl` when imported on Windows.

## Usage

From the repository root on any machine:

```bash
# Check for differences
python3 .agents/scripts/vscode_sync.py status      # PC: python .agents\scripts\vscode_sync.py status

# Export from current machine to this bundle
python3 .agents/scripts/vscode_sync.py export

# Import from this bundle to local VS Code (installs extensions & applies settings)
python3 .agents/scripts/vscode_sync.py import
```

Or invoke the slash command `/smh-sync-vscode` from chat.

## Private Keys & Provider Profiles

API keys and custom LLM provider setups (e.g., Command Code in Zoo Code) live in VS Code's internal database (`state.vscdb`) and are **never** committed to git.
To migrate them:
1. On source machine: Open Zoo Code -> Gear icon -> **Export** (save JSON file).
2. On destination machine: Open Zoo Code -> Gear icon -> **Import** (select JSON file).
