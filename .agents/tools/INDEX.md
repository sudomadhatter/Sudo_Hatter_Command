# tools — INDEX

The master registry for external tools, cloud CLIs, and Model Context Protocol (MCP) servers (SCC-432).
Like `.agents/permissions/families.json` for terminal commands, `.agents/tools/connections.json` is the
**single source of authorship** for software tools and connections across all five agent platforms
(Claude Code, Zoo Code, OpenCode, Antigravity, and Codex).

## Files in this directory

| File | Purpose |
|---|---|
| `connections.json` | The canonical registry of tools, access modes (`cli-only`, `mcp-only`, `hybrid`), auth mechanisms, and MCP configurations. |
| `connections.schema.json` | JSON Schema validating the structure of `connections.json`. |

## Generators & Tooling

- `.agents/scripts/tool_sync.py`: Reads `connections.json`, resolves paths dynamically via `{REPO_ROOT}`, and renders:
  - Root `.mcp.json` (Claude Code)
  - `opencode.json` `"mcp"` stanza (OpenCode)
  - VS Code globalStorage `mcp_settings.json` (Zoo Code in VS Code)
  - `~/.gemini/config/mcp_config.json` (Antigravity)
- Hook `.agents/hooks/rule-trigger.py`: Injects pointers to `.agents/skills/tool-connections/SKILL.md` when prompt mentions tools or APIs.
- `/smh-sync-agents` (`sync-agents.ps1`): Automatically executes `tool_sync.py` to keep all platforms synchronized.
