# Research & Architecture Spec: Universal Tools & MCP Connections

**Ticket:** SCC-395 — Universal MCP folder for all Agents  
**Author:** Antigravity / Gemini  
**Date:** 2026-09-04  
**Status:** Research & Proposed Architecture  

---

## 1. Executive Summary & Problem Statement

In the Sudo_Hatter_Command ecosystem, agents operate across five distinct platforms:
1. **Claude Code** (CLI / IDE)
2. **Zoo Code / Roo-Code** (VS Code extension with Wonderland modes)
3. **OpenCode** (CLI)
4. **Antigravity** (Gemini IDE / extension)
5. **Codex** (CLI / IDE)

Each of these platforms interacts with external services, software, and APIs—including Jira, GitHub, Sentry, Firebase, Playwright, Keyway, and Markdown Feedback (`md-feedback`).

### The Current Friction:
- **Configuration Fragmentation:**
  - Claude Code reads `.mcp.json` at the repo root, plus plugins in `.claude/settings.json`. Currently, `.mcp.json` has a hardcoded macOS path (`/Users/sudohatter/...`), causing errors in Linux/WSL environments (`/home/dlohn/...`).
  - Zoo Code in VS Code reads `mcp_settings.json` from VS Code's `globalStorage`. Currently, this file is empty (`{"mcpServers": {}}`) across both Windows and WSL.
  - OpenCode expects an `"mcp"` stanza inside `opencode.json`. It completely ignores `.opencode/mcp.json`. Because `opencode.json` lacks an `"mcp"` key, OpenCode receives zero MCP servers.
  - Antigravity and Codex rely primarily on skills and native tool calls, without an automated MCP server synchronization pipeline.
- **The CLI vs. MCP Ambiguity:**
  - Several core tools are designed as **CLI-first** (e.g. `acli` for Jira, `gh` for GitHub, `keyway` for secrets). They run directly in the shell, use the OS credential store, and consume zero MCP tool schema tokens.
  - Other tools require **MCP** (e.g., `md-feedback` is required to manipulate user memos without corrupting markdown tracking hashes).
  - Other tools are **hybrid** (e.g. Sentry has `sentry-cli` for headless scripts and Sentry MCP for interactive debugging; Playwright has CLI and MCP).
  - Agents currently have no single directory or decision matrix telling them:
    1. What external software connections exist.
    2. Which access mode (CLI or MCP) to use.
    3. How to verify authentication and health.

---

## 2. Proposed Architecture: The Universal Tool Hub

To eliminate manual per-platform configuration and prevent tool drift across machines, we adopt the same pattern proven by `families.json` and `permission_render.py` (SCC-378):

```
                        .agents/tools/connections.json
                          (Single Source of Truth)
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
   AUTOMATIC SYNC            SKILL DIRECTORY            INTENT HOOK
   `tool_sync.py`            `tool-connections`         `rule-trigger.py`
  (Runs in smh-sync-agents)   (Readable by all agents)  (Injected on prompt)
           │                         │                         │
 ┌─────────┴─────────┐       Every LLM learns:         "connect to Sentry"
 │ • root .mcp.json  │       • Available APIs          → Immediately injects
 │ • opencode.json   │       • MCP vs CLI choice       pointer to the
 │ • Zoo mcp_settings│       • Auth & test commands    connection skill
 └───────────────────┘
```

### Component A: Master Registry (`.agents/tools/connections.json`)

A centralized JSON definition describing every external tool and service in the ecosystem.

```json
{
  "$schema": "./connections.schema.json",
  "connections": {
    "md-feedback": {
      "name": "MD Feedback Reviewer",
      "category": "document-review",
      "mode": "mcp-only",
      "preferred": "mcp",
      "description": "Reads user memo annotations on markdown files. Mandatory for resolving user feedback.",
      "mcp": {
        "command": "npx",
        "args": ["-y", "md-feedback", "--workspace={REPO_ROOT}"]
      },
      "platforms": ["claude", "zoo", "opencode", "antigravity"]
    },
    "jira": {
      "name": "Jira Issue Tracker",
      "category": "issue-tracking",
      "mode": "cli-only",
      "preferred": "cli",
      "description": "Board management, ticket reading, transitions, and minting.",
      "cli": {
        "binary": "acli",
        "check": "acli jira auth status",
        "rule": ".agents/rules/jira.md"
      },
      "auth": "OS Keyring (Keychain / Credential Manager)"
    },
    "sentry": {
      "name": "Sentry Error Monitoring",
      "category": "observability",
      "mode": "hybrid",
      "preferred": "mcp",
      "description": "Triage runtime errors and incidents in production/staging.",
      "mcp": {
        "command": "npx",
        "args": ["-y", "@sentry/mcp-server"],
        "env": {
          "SENTRY_ORG": "aviationchat"
        }
      },
      "cli": {
        "binary": "sentry-cli",
        "check": "sentry-cli info"
      },
      "auth": "Keyway vault / SENTRY_AUTH_TOKEN"
    },
    "playwright": {
      "name": "Playwright Browser Testing",
      "category": "browser-testing",
      "mode": "hybrid",
      "preferred": "mcp",
      "description": "Headless and visual browser automation, inspection, and E2E verification.",
      "mcp": {
        "command": "npx",
        "args": ["-y", "@playwright/mcp@latest", "--caps", "vision,pdf,devtools"]
      },
      "cli": {
        "binary": "npx vitest run",
        "skill": ".agents/skills/playwright-frontend-check/SKILL.md"
      }
    },
    "keyway": {
      "name": "Keyway Secrets Management",
      "category": "secrets",
      "mode": "cli-only",
      "preferred": "cli",
      "description": "Pull, push, and in-memory execution of environment variables without writing secrets to disk.",
      "cli": {
        "binary": "keyway",
        "check": "keyway doctor",
        "skill": ".agents/skills/keyway-secrets/SKILL.md"
      },
      "auth": "GitHub OAuth / OS Keyring"
    },
    "github": {
      "name": "GitHub CLI",
      "category": "version-control",
      "mode": "cli-only",
      "preferred": "cli",
      "description": "PR creation, review checks, CI run status, and release management.",
      "cli": {
        "binary": "gh",
        "check": "gh auth status"
      },
      "auth": "gh auth login / OS Keyring"
    },
    "firebase": {
      "name": "Firebase CLI",
      "category": "cloud-hosting",
      "mode": "cli-only",
      "preferred": "cli",
      "description": "Deployments, Firestore emulation, security rules, and cloud functions.",
      "cli": {
        "binary": "firebase",
        "check": "firebase projects:list"
      },
      "auth": "firebase login"
    }
  }
}
```

### Component B: Synchronization Engine (`.agents/scripts/tool_sync.py`)

The sync script generates and updates platform files from `connections.json`:
1. **Dynamic Path Resolution:** Replaces `{REPO_ROOT}` with the actual absolute path on the running host, fixing the cross-platform Mac vs. Linux path divergence.
2. **Root `.mcp.json`:** Updates the `mcpServers` object read by Claude Code.
3. **OpenCode `opencode.json`:** Inserts or updates the `"mcp"` block in `opencode.json` so OpenCode actively connects to declared servers.
4. **Zoo Code `mcp_settings.json`:** Resolves the active VS Code user storage directory (`~/.vscode-server/data/User/globalStorage/zoocodeorganization.zoo-code/settings/mcp_settings.json` on Linux/WSL or `AppData/Roaming` on Windows) and populates `mcpServers`.
5. **Integration with `/smh-sync-agents`:** Added to `sync-agents.ps1` so that running `/smh-sync-agents` refreshes skills, commands, and tool connections in one pass.

### Component C: Universal Agent Skill (`.agents/skills/tool-connections/SKILL.md`)

A centralized skill directory explaining:
- Full matrix of available connections.
- Access protocol: when to use CLI commands vs. MCP tools.
- Health checks: standard commands to verify connectivity (`acli jira auth status`, `keyway doctor`, `gh auth status`).
- How to add a new connection.

### Component D: Intent-Triggered Hook (`.agents/hooks/rule-trigger.py`)

In `rule-trigger.py`, we register intent keywords:
```python
# In connections / tool rule frontmatter:
triggers: [api, mcp, connect, connection, integration, external tool, database, sentry, firebase, playwright, keyway, jira]
```
When an operator or task mentions connecting to software or an external API, the hook outputs a lightweight 2-line pointer:
`See .agents/skills/tool-connections/SKILL.md for available MCP & CLI tools and health checks.`

---

## 3. Implementation Steps & Validation (When Scheduled)

1. **Step 1: Authorship:**
   - Author `.agents/tools/connections.json` with initial core set (`md-feedback`, `jira`, `sentry`, `playwright`, `keyway`, `github`, `firebase`).
2. **Step 2: Sync Script & Automation:**
   - Author `.agents/scripts/tool_sync.py` with `--check`, `--status`, and `--apply` flags.
   - Wire into `sync-agents.ps1`.
3. **Step 3: Universal Skill & Hook:**
   - Author `.agents/skills/tool-connections/SKILL.md`.
   - Register triggers in `rule-trigger.py`.
4. **Step 4: Test Suite & Parity Guard:**
   - Add automated test in `tests/test_command_surfaces.py` asserting all platform MCP files match `connections.json` without drift.

---

## 4. References & Linked Documentation

- [SCC-395 Jira Subtask](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/jira.md)
- [Jira Operations Rule](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/jira.md)
- [Claude Settings & Permissions](file:///home/dlohn/Sudo_Hatter_Command/.claude/settings.json)
- [OpenCode Configuration](file:///home/dlohn/Sudo_Hatter_Command/opencode.json)
- [Rule Trigger Hook](file:///home/dlohn/Sudo_Hatter_Command/.agents/hooks/rule-trigger.py)
