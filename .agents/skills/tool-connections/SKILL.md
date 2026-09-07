---
name: tool-connections
description: Universal connection matrix and tool invocation guide for all agents (Claude, Codex, Antigravity, OpenCode, Zoo). Covers MCP and CLI connection dispatch, credential propagation via Keyway (.env), zero hardcoded secrets, and live health checks for gcloud, jira (acli), github (gh), firebase, keyway, sentry, playwright, and md-feedback.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Universal Tool & MCP Connections Guide

> **Single source of truth for agent tools, MCP servers, and CLI utilities across all platforms.**
> Authored centrally in [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json) and rendered automatically to every agent environment.

---

## 🎯 When to Use This Skill

- Understanding which tools and integrations are available across Claude Code, OpenCode, Zoo Code, and Antigravity.
- Deciding whether to invoke a tool via **CLI** or **MCP** (the dispatch decision rule).
- Diagnosing connection failures, missing credentials, or unauthenticated tool states.
- Verifying credential propagation from Keyway (`.env`) into git worktrees.
- Adding or registering a new CLI tool or MCP server across the system.

---

## 🏛️ 1. Architecture: Single Source of Authorship

All external tool connections and MCP servers originate in [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json), validated against [`.agents/tools/connections.schema.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.schema.json).

```
.agents/tools/connections.json (Single Source of Truth)
           │
           ▼
.agents/scripts/tool_sync.py (Renders & Injects)
           │
 ┌─────────┼──────────────────┬─────────────────┐
 ▼         ▼                  ▼                 ▼
Claude   OpenCode           Zoo Code          Antigravity
.mcp.json opencode.json    mcp_settings.json ~/.gemini/config/mcp_config.json
           ("mcp" stanza)   (globalStorage)
```

**Rule:** Never edit downstream platform configs directly (`.mcp.json`, `opencode.json`, `mcp_settings.json`, `mcp_config.json`). Always edit [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json) and run `python3 .agents/scripts/tool_sync.py --apply` or `/smh-sync-agents`.

---

## 📊 2. Connection Matrix & Decision Rules

| Connection Key | Name | Mode | Preferred | Primary Access / Check | Description |
|---|---|---|---|---|---|
| `md-feedback` | MD Feedback Reviewer | `mcp-only` | **MCP** | MCP tool `md-feedback` | User markdown annotations and review comments |
| `gcloud` | Google Cloud CLI | `cli-only` | **CLI** | `gcloud auth list` | Cloud Run, Storage, BigQuery, IAM |
| `jira` | Jira Issue Tracker | `cli-only` | **CLI** | `acli jira auth status` | Live sprint board, tickets, and transitions |
| `github` | GitHub CLI | `cli-only` | **CLI** | `gh auth status` | Pull requests, reviews, CI runs, releases |
| `firebase` | Firebase CLI | `cli-only` | **CLI** | `firebase projects:list` | Firestore, rules, functions, App Hosting |
| `keyway` | Keyway Secrets | `cli-only` | **CLI** | `keyway doctor` | Encrypted vault sharing & RAM-only secrets |
| `sentry` | Sentry Monitoring | `hybrid` | **MCP** | `@sentry/mcp-server` / `sentry-cli` | Error monitoring, issue triage, and alerts |
| `playwright` | Playwright Browser | `hybrid` | **MCP** | `@playwright/mcp` / `vitest` | Live browser automation & visual inspection |

### Dispatch Decision Rule: CLI vs. MCP

1. **CLI-First by Design:** If a tool is `cli-only` or operates on local state/terminal workflows (`jira`, `github`, `gcloud`, `firebase`, `keyway`), use the CLI binary directly through `run_command` / bash. The shell gives explicit exit codes, real-time output, and full terminal control.
2. **MCP-Preferred for Interactive Context:** If a tool is `mcp-only` or `hybrid` with `preferred: "mcp"` (`md-feedback`, `sentry`, `playwright`), use the native MCP tool when conversational inspection, real-time DOM traversal, or live API responses enrich agent context.
3. **Hybrid Fallback:** For `sentry` or `playwright`, if the MCP server is unreachable or disabled, fall back immediately to the CLI equivalent (`sentry-cli` or `npx vitest run`).

---

## 🔐 3. Credential Sharing via Keyway (Zero Hardcoded Secrets)

All credentials travel through the team's encrypted **Keyway cloud vault**. No passwords, API keys, or personal access tokens are committed to git or hardcoded into connection configs.

### How Credentials Travel:
1. **Cloud Vault to Machine:**
   ```bash
   keyway pull -e development
   ```
   This pulls the latest project credentials into `.env` at the root of the repository.
2. **Repository to Worktree:**
   When a git worktree is created, [`.agents/scripts/link-worktree-assets.py`](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/link-worktree-assets.py) symlinks `.env` from the repository root into the worktree root:
   ```bash
   python3 .agents/scripts/link-worktree-assets.py <worktree-path>
   ```
3. **Environment Injection into Tools:**
   - Tools and subshells automatically read `.env` keys.
   - Dynamic paths use the `{REPO_ROOT}` token in [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json), which `tool_sync.py` resolves to the absolute filesystem root of the current checkout.

### Required Environment Keys by Tool:
- **`gcloud`**: `GCP_PROJECT`, `GCP_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`
- **`github`**: `GITHUB_PAT_CLASSIC`, `GITHUB_REPO`
- **`firebase`**: `NEXT_PUBLIC_FIREBASE_PROJECT_ID`, `NEXT_PUBLIC_FIREBASE_API_KEY`
- **`sentry`**: `SENTRY_AUTH_TOKEN`, `SENTRY_WEBHOOK_SECRET`

---

## 🩺 4. Health Checks & Diagnostics

Run these quick commands to verify agent connection readiness:

```bash
# 1. Check Tool Connection Config Drift
python3 .agents/scripts/tool_sync.py --check

# 2. Keyway Secrets Vault
keyway doctor

# 3. Google Cloud CLI
gcloud auth list
gcloud config get-value project

# 4. Jira CLI (Atlassian CLI)
acli jira auth status

# 5. GitHub CLI
gh auth status

# 6. Firebase CLI
firebase projects:list

# 7. Sentry CLI
sentry-cli info
```

---

## 🛠️ 5. Adding a New Tool Connection

When introducing a new CLI tool or MCP server to the workspace:

1. **Update [`connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json):** Add the entry under `"connections"` with name, category, mode (`mcp-only` | `cli-only` | `hybrid`), preferred interface, description, and mcp/cli definitions.
2. **Validate & Apply:**
   ```bash
   python3 .agents/scripts/tool_sync.py --apply
   ```
3. **Propagate Mirrors:**
   ```bash
   pwsh .agents/scripts/sync-agents.ps1
   ```
4. **Commit Gate Compliance:** Ensure any secrets needed are added to Keyway (`keyway set KEY=VALUE -e development`), not committed to git.
