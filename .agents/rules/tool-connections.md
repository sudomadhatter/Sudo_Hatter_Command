---
name: tool-connections
description: "Universal connection matrix and tool invocation guide for all agents (Claude, Codex, Antigravity, OpenCode, Zoo). Covers MCP and CLI connection dispatch, credential propagation via Keyway (.env), zero hardcoded secrets, and live health checks for gcloud, jira (acli), github (gh), firebase, keyway, sentry, playwright, and md-feedback."
trigger: model_decision
triggers: [mcp, tool, tools, connections, integration, gcloud, google cloud, sentry, firebase, playwright, keyway, acli]
---

# Universal Tool & MCP Connections

> **Single source of truth for agent tools, MCP servers, and CLI utilities across all platforms.**
> Authored centrally in [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json) and rendered automatically to every agent environment.

---

## 🏛️ 1. Single Source of Authorship

All tool and MCP server configurations originate in [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json), validated against [`.agents/tools/connections.schema.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.schema.json).

**Downstream config files are generated mirrors, never sources:**
- **Claude Code:** Root `.mcp.json`
- **OpenCode:** `opencode.json` (`"mcp"` stanza, preserving root keys)
- **Zoo Code:** `mcp_settings.json` in VS Code `globalStorage/zoocodeorganization.zoo-code/settings/`
- **Antigravity:** `~/.gemini/config/mcp_config.json`

⛔ **Never edit downstream configs by hand.** Edit [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json) and run `python3 .agents/scripts/tool_sync.py --apply` or `/smh-sync-agents`.

---

## ⚖️ 2. The Dispatch Decision Rule: CLI vs. MCP

Not every tool belongs in MCP. Mixing execution modes creates confusion; use the matrix in [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json):

1. **CLI-First (`cli-only`):** `jira` (`acli`), `github` (`gh`), `gcloud`, `firebase`, `keyway`.
   - Shell commands provide exact exit codes, deterministic stdout/stderr, full scripting capability, and zero token overhead when idle.
   - If an agent says "I have no Jira/GitHub integration because there is no MCP server", that is false: the CLI is the integration.
2. **MCP-First (`mcp-only` or `hybrid` with `preferred: "mcp"`):** `md-feedback`, `sentry`, `playwright`.
   - Interactive context enrichment, structured inspection of UI or remote errors, and bidirectional document annotation require MCP server protocols.
3. **Hybrid Fallback:**
   - If Sentry MCP or Playwright MCP fails or is unavailable in a remote subagent, fall back immediately to the CLI equivalent (`sentry-cli info` or `npx vitest run`).

---

## 🔐 3. Credential Propagation via Keyway (Zero Hardcoded Secrets)

Credentials NEVER live in git repositories, commit logs, or plaintext platform configs.

- **Storage:** Stored in the team's encrypted Keyway cloud vault (`development` environment).
- **Distribution:** Fetched via `keyway pull -e development` to `.env`.
- **Worktree Isolation:** Automatically symlinked into worktrees by [`.agents/scripts/link-worktree-assets.py`](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/link-worktree-assets.py).
- **Dynamic Paths:** `{REPO_ROOT}` token in [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json) is dynamically expanded to the active checkout path by `tool_sync.py`.

---

## 🩺 4. Health Checks

| Tool | Health Check Command | Keyway Environment Keys |
|---|---|---|
| **Configs** | `python3 .agents/scripts/tool_sync.py --check` | — |
| **Keyway** | `keyway doctor` | GitHub OAuth Vault |
| **GCloud** | `gcloud auth list` | `GCP_PROJECT`, `GOOGLE_APPLICATION_CREDENTIALS` |
| **Jira** | `acli jira auth status` | OS Keyring / mode-600 auth |
| **GitHub** | `gh auth status` | `GITHUB_PAT_CLASSIC`, `GITHUB_REPO` |
| **Firebase** | `firebase projects:list` | `NEXT_PUBLIC_FIREBASE_PROJECT_ID` |
| **Sentry** | `sentry-cli info` | `SENTRY_AUTH_TOKEN` |
