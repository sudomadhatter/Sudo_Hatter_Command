# Task SCC-432: Universal MCP and Tool Connections Hub

## Problem Statement & Context

External tools, software connections, and cloud APIs (Jira, GitHub CLI, Sentry, Firebase, Google Cloud CLI, Playwright, MD Feedback, Keyway) are fragmented across five agent platforms (Claude Code, Zoo Code in VS Code, OpenCode, Antigravity, Codex) and two operating environments (macOS and PC WSL/Ubuntu):
1. **Machine & Path Divergence:** Root `.mcp.json` has a hardcoded macOS path (`/Users/sudohatter/Sudo_Hatter_Command`), breaking `md-feedback` on Linux/WSL (`/home/dlohn/Sudo_Hatter_Command`).
2. **Platform Configuration Mismatches:**
   - **OpenCode:** Ignores `.opencode/mcp.json` because its engine expects an `"mcp"` stanza directly in `opencode.json` using its own schema (`type: "local"`, `command: [cmd, ...args]`, `environment: {...}`).
   - **Zoo Code:** Reads `mcp_settings.json` in VS Code globalStorage (`~/.vscode-server/data/User/globalStorage/zoocodeorganization.zoo-code/settings/mcp_settings.json`), which is currently empty.
   - **Antigravity:** Reads `~/.gemini/config/mcp_config.json`, which is currently unconfigured.
   - **Claude Code:** Reads root `.mcp.json`, which currently has hardcoded user paths and only one server.
3. **CLI vs. MCP Confusion:** Agents lack a single decision matrix detailing which tools are CLI-only (`acli`, `gh`, `gcloud`, `keyway`, `firebase`), MCP-only (`md-feedback`), or hybrid (`sentry`, `playwright`).
4. **Credential Portability via Keyway:** Credentials and API keys must travel securely across machines and worktrees without being committed to git. Keyway (`keyway.sh`) serves as the central vault, synchronizing `.env` files that are automatically symlinked into agent worktrees via `link-worktree-assets.py`.
5. **No Automated Parity or Drift Checks:** No script exists in `/smh-sync-agents` or `run_all.py` to assert that all platforms have matching, valid tool definitions.

## User Review Required

> [!IMPORTANT]
> - **Google Cloud CLI (`gcloud`) Added:** Incorporated `gcloud` into the master connection registry, agent skills, and health checks for managing Cloud Run, GCP projects, storage, and ADC authentication.
> - **Keyway `.env` Credential Sharing:** All tool credentials (e.g. `SENTRY_AUTH_TOKEN`, `GCP_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`, `GEMINI_API_KEY`) travel across machines via Keyway cloud vault (`keyway pull -e development`) and propagate into isolated worktrees via `link-worktree-assets.py`. No credentials are committed to git or hardcoded into MCP configs.
> - **Cross-Machine Path Portability:** All configuration generators use `{REPO_ROOT}` token expansion to dynamically resolve paths to the host's actual repository root, eliminating Mac vs. Linux path breakage.

## Proposed Changes

We adopt the proven single-source-of-truth architecture modeled after `families.json` and `permission_render.py` (SCC-378).

Grouped by component:

---

### 1. Master Connection Registry & Schema

#### [NEW] [connections.json](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json)
Central declarative registry defining all external tools, software connections, and credential bindings:
- `md-feedback` (mcp-only, `npx -y md-feedback --workspace={REPO_ROOT}`)
- `jira` (cli-only, `acli`, auth: OS Keyring, rule: `.agents/rules/jira.md`)
- `github` (cli-only, `gh`, auth: `gh auth login` / OS Keyring)
- `gcloud` (cli-only, `gcloud`, auth: `gcloud auth login` / Application Default Credentials / Keyway `GOOGLE_APPLICATION_CREDENTIALS`)
- `firebase` (cli-only, `firebase`, auth: `firebase login`)
- `keyway` (cli-only, `keyway`, auth: GitHub OAuth / OS Keyring, skill: `.agents/skills/keyway-secrets/SKILL.md`)
- `sentry` (hybrid: `sentry-cli` for CLI, `@sentry/mcp-server` for MCP, auth: Keyway `SENTRY_AUTH_TOKEN`)
- `playwright` (hybrid: vitest runner for CLI, `@playwright/mcp@latest` for interactive MCP)

#### [NEW] [connections.schema.json](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.schema.json)
JSON schema defining valid tool connection entries, fields (`id`, `name`, `category`, `mode`, `preferred`, `cli`, `mcp`, `auth`, `env_keys`), and platform targets.

#### [NEW] [INDEX.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/INDEX.md)
Inventory and documentation of the `.agents/tools/` master directory.

---

### 2. Synchronization Engine

#### [NEW] [tool_sync.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tool_sync.py)
Automated generator and validator:
- Reads `.agents/tools/connections.json`.
- Dynamically resolves `{REPO_ROOT}` to absolute workspace paths on the active OS (Mac or Linux/WSL).
- Injects environment variable references without baking secrets into config files.
- Renders:
  1. `.mcp.json` (root, for Claude Code): `{"mcpServers": { ... }}`
  2. `opencode.json` (root, for OpenCode): preserves existing keys and injects/updates `"mcp": { "<id>": { "type": "local", "command": [...], "environment": {...}, "enabled": true } }`.
  3. Zoo Code `mcp_settings.json` (VS Code globalStorage in WSL/Linux and Windows): populates `mcpServers`.
  4. Antigravity `mcp_config.json` (`~/.gemini/config/mcp_config.json`): populates `mcpServers`.
- Provides CLI flags:
  - `--check`: read-only drift check (exit 0 if all clean, exit 1 if drift detected).
  - `--status`: human-readable status table of platform tool configurations and health checks.
  - `--apply`: writes configurations to disk.
  - `--root <dir>`: workspace root override for tests and alternate repos.

#### [MODIFY] [sync-agents.ps1](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/sync-agents.ps1)
Integrate `Invoke-ToolSync`:
- Runs `tool_sync.py --check --root $HomeRoot` during `-Status`.
- Runs `tool_sync.py --root $HomeRoot` during regular sync (respecting `-WhatIf`).

---

### 3. Agent Knowledge, Rules, and Discovery

#### [NEW] [SKILL.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/tool-connections/SKILL.md)
Universal agent skill `tool-connections`:
- Matrix of available connections (`gcloud`, `jira`, `github`, `firebase`, `sentry`, `playwright`, `md-feedback`, `keyway`).
- Concrete guidance on when to choose CLI commands vs MCP calls.
- Keyway vault credential guide: how `.env` credentials travel across machines and how `link-worktree-assets.py` ensures worktrees inherit them.
- Standard health check cheat-sheet (`gcloud auth list`, `acli jira auth status`, `keyway doctor`, `gh auth status`, `firebase projects:list`).

#### [NEW] [tool-connections.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/tool-connections.md)
Agent rule with intent triggers:
```yaml
---
name: tool-connections
description: "Universal registry of external tools, cloud CLIs (gcloud, firebase, acli, gh), and MCP connections. Directs agents whether to use CLI or MCP, how credentials travel via Keyway, and how tools sync across platforms."
trigger: model_decision
triggers: [api, mcp, connect, connection, integration, external tool, gcloud, google cloud, sentry, firebase, playwright, keyway, jira]
---
```
When an operator prompt mentions tools or connections, `.agents/hooks/rule-trigger.py` injects a pointer to `tool-connections`.

#### [MODIFY] [.agents/rules/INDEX.md](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/INDEX.md)
Add `tool-connections.md` to the rule index.

---

### 4. Automated Parity & Drift Test Suite

#### [NEW] [test_tool_sync.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/test_tool_sync.py)
Automated unit and integration test suite:
- Validates `connections.json` against `connections.schema.json`.
- Tests rendering for Claude, OpenCode, Zoo Code, and Antigravity against isolated temporary directories.
- Tests that `{REPO_ROOT}` placeholder is resolved dynamically and never hardcoded.
- Tests `--check` exit codes (clean = 0, drifted = 1).
- Tests roundtrip preservation of other keys in `opencode.json`.

#### [MODIFY] [run_all.py](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/run_all.py)
Register `test_tool_sync.py` in the master test runner.

---

## Verification Plan

### Automated Tests
1. Run new test suite:
   ```bash
   python3 .agents/scripts/tests/test_tool_sync.py
   ```
2. Run full repo test battery:
   ```bash
   python3 .agents/scripts/tests/run_all.py
   ```
3. Verify drift check:
   ```bash
   python3 .agents/scripts/tool_sync.py --check
   ```
4. Verify `/smh-sync-agents` integration:
   ```bash
   pwsh .agents/scripts/sync-agents.ps1 -Status
   ```

### Manual Verification
1. Verify Keyway vault connectivity and `.env` presence (`keyway doctor`).
2. Verify `gcloud` CLI status (`gcloud version`, `gcloud auth list`).
3. Verify root `.mcp.json` contains valid JSON with local workspace paths.
4. Verify `opencode.json` contains valid `"mcp"` stanza without disrupting existing permissions or instructions.
5. Verify Zoo Code `mcp_settings.json` in VS Code globalStorage contains populated `mcpServers`.
6. Verify Antigravity `~/.gemini/config/mcp_config.json` contains valid `mcpServers`.
7. Verify `rule-trigger.py` outputs a pointer to `tool-connections` when tested against keywords (`gcloud`, `mcp`, `sentry`, `api`).
