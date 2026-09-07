# Walkthrough — SCC-432: Universal Tool & MCP Connections for All Agents

> **Task:** SCC-432 (under Epic SCC-33)
> **Branch:** `chore/SCC-432-universal-tools-mcp`
> **Status:** Complete · All 82 test suites passing (82/82)

---

## 🎯 What Was Built

External tools and MCP connections were previously fragmented across five agent platforms (Claude Code, OpenCode, Zoo Code, Antigravity, and Codex). OpenCode ignored `.opencode/mcp.json` because it requires an `mcp` stanza in `opencode.json`; Zoo Code had empty MCP settings; Claude Code carried machine-specific hardcoded macOS paths in `.mcp.json`; and agents had no universal registry or clear dispatch decision rules for CLI vs. MCP tools.

Under **SCC-432**, we established a unified architecture:
1. **Single Source of Truth:** Centralized master registry in [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json) with strict validation against [`.agents/tools/connections.schema.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.schema.json).
2. **Universal Sync Engine:** Authored [`.agents/scripts/tool_sync.py`](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tool_sync.py) which renders all downstream configs automatically with dynamic `{REPO_ROOT}` token resolution and user-setting preservation:
   - **Claude Code:** Root [`.mcp.json`](file:///home/dlohn/Sudo_Hatter_Command/.mcp.json) and mirrors (`.claude/mcp.json`, `.opencode/mcp.json`)
   - **OpenCode:** [`opencode.json`](file:///home/dlohn/Sudo_Hatter_Command/opencode.json) (`"mcp"` stanza with local server definitions)
   - **Zoo Code:** `mcp_settings.json` in VS Code global storage
   - **Antigravity:** `~/.gemini/config/mcp_config.json`
3. **Integrated into `/smh-sync-agents`:** Updated [`.agents/scripts/sync-agents.ps1`](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/sync-agents.ps1) with `Invoke-ToolSync` (runs `--check` on `-Status` and `--apply` on main sync).
4. **Registered Google Cloud CLI (`gcloud`):** Added to the registry alongside `jira`, `github`, `firebase`, `keyway`, `sentry`, `playwright`, and `md-feedback`.
5. **Keyway `.env` Credential Flow:** Verified zero hardcoded credentials in git or connection configs. All secrets flow via Keyway cloud vault (`keyway pull -e development`) into `.env` and are symlinked into worktrees via [`.agents/scripts/link-worktree-assets.py`](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/link-worktree-assets.py).
6. **Universal Skill & Intent-Triggered Rule:** Authored master skill [`.agents/skills/tool-connections/SKILL.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/tool-connections/SKILL.md) and intent-triggered rule [`.agents/rules/tool-connections.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/tool-connections.md).
7. **Comprehensive Test Suite:** Authored [`.agents/scripts/tests/test_tool_sync.py`](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/test_tool_sync.py) covering schema validation, token replacement, config preservation, drift detection, and live checks (20/20 passing).

---

## 📋 Task Checklist

- [x] Create master connection registry [`.agents/tools/connections.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.json) with JSON schema [`.agents/tools/connections.schema.json`](file:///home/dlohn/Sudo_Hatter_Command/.agents/tools/connections.schema.json).
- [x] Build [`.agents/scripts/tool_sync.py`](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tool_sync.py) supporting Claude Code, OpenCode, Zoo Code, and Antigravity.
- [x] Integrate tool sync into [`.agents/scripts/sync-agents.ps1`](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/sync-agents.ps1) with `-Status` drift detection.
- [x] Register Google Cloud CLI (`gcloud`) in connection registry.
- [x] Author universal skill [`.agents/skills/tool-connections/SKILL.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/tool-connections/SKILL.md) and update [`.agents/skills/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/skills/INDEX.md).
- [x] Author intent rule [`.agents/rules/tool-connections.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/tool-connections.md) and update [`.agents/rules/INDEX.md`](file:///home/dlohn/Sudo_Hatter_Command/.agents/rules/INDEX.md).
- [x] Update SOP quick-reference [docs/_scc_sops_prds/workflows_testing_SOP.md](file:///home/dlohn/Sudo_Hatter_Command/docs/_scc_sops_prds/workflows_testing_SOP.md) (satisfying `sop-currency.md`).
- [x] Author test suite [`.agents/scripts/tests/test_tool_sync.py`](file:///home/dlohn/Sudo_Hatter_Command/.agents/scripts/tests/test_tool_sync.py) (20/20 passed).
- [x] Run full test suite `python3 .agents/scripts/tests/run_all.py` (82/82 passed).
- [x] Verify live tool health checks (`gcloud`, `acli`, `gh`, `firebase`, `keyway`).

---

## 🔍 Evidence

### 1. Tool Sync Status & Drift Verification
```
$ python3 .agents/scripts/tool_sync.py --status

=== Tool & Connection Status ===
Registry: /home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-432-universal-tools-mcp/.agents/tools/connections.json (8 connections registered)

Tool ID         Mode       Pref   CLI Binary   Binary Status   Auth / Keyway Env                  
-----------------------------------------------------------------------------------------------
firebase        cli-only   cli    firebase     INSTALLED       NEXT_PUBLIC_FIREBASE_PROJECT_ID,...
gcloud          cli-only   cli    gcloud       INSTALLED       GCP_PROJECT, GCP_PROJECT_ID, GOO...
github          cli-only   cli    gh           INSTALLED       GITHUB_PAT_CLASSIC, GITHUB_REPO    
jira            cli-only   cli    acli         INSTALLED       OS Keyring (Keychain / Credentia...
keyway          cli-only   cli    keyway       INSTALLED       GitHub OAuth / Keyway Organizati...
md-feedback     mcp-only   mcp    -            n/a             None (Local File Workspace)        
playwright      hybrid     mcp    npx vitest run INSTALLED       None (Local Browser Automation)    
sentry          hybrid     mcp    sentry-cli   MISSING         SENTRY_AUTH_TOKEN, SENTRY_WEBHOO...

Rendered Target Checks:
  Claude Code:  /home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-432-universal-tools-mcp/.mcp.json
  OpenCode:     /home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-432-universal-tools-mcp/opencode.json
  Zoo Code:     /home/dlohn/.vscode-server/data/User/globalStorage/zoocodeorganization.zoo-code/settings/mcp_settings.json (exists: True)
  Antigravity:  /home/dlohn/.gemini/config/mcp_config.json (exists: True)

tool_sync: ALL PLATFORM CONFIGS IN SYNC.
```

### 2. Sync Agents Status
```
$ pwsh .agents/scripts/sync-agents.ps1 -Status
sync-agents: master=/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-432-universal-tools-mcp/.agents
sync-agents: target=/home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-432-universal-tools-mcp (lobby=True)
sync-agents: STATUS /home/dlohn/Sudo_Hatter_Command/.claude/worktrees/scc-432-universal-tools-mcp (read-only)
  clean - every invocable file matches the master.
permission_render: in sync (zoo, claude, antigravity)
tool_sync: ALL PLATFORM CONFIGS IN SYNC.
```

### 3. Tool Health Checks
- **Google Cloud CLI (`gcloud auth list`):**
  ```
  ACTIVE  ACCOUNT
  *       firebase-adminsdk-fbsvc@aviationchat.iam.gserviceaccount.com
  ```
- **Jira CLI (`acli jira auth status`):**
  ```
  ✓ Authenticated
    Site: sudo-command.atlassian.net
    Email: sudomadhatter@gmail.com
  ```
- **Keyway Secrets (`keyway doctor`):**
  ```
  ✓ CLI version: 0.5.3 (latest)
  ✓ Authentication: Logged in as sudomadhatter
  ✓ GitHub repository: sudomadhatter/Sudo_Hatter_Command
  ✓ Environment file: Found: .env
  ```
- **GitHub CLI (`gh auth status`):**
  ```
  ✓ Logged in to github.com account sudomadhatter
  ```
- **Firebase CLI (`firebase projects:list`):**
  ```
  ✔ Preparing the list of your Firebase projects
  3 project(s) total (AviationChat, B-LWorldwide, NexGen Films).
  ```

---

## 📊 Suite Ledger

```
============================================================
82/82 files passed
```

Key individual suites verified:
- `test_tool_sync.py`: 20/20 passed
- `test_rule_frontmatter.py`: 30/30 passed
- `test_command_surfaces.py`: 329/329 passed
- `test_check_maps.py`: 37/37 passed
- `test_review_engine.py`: 868/868 passed

---

## 👤 Your Actions

No manual configuration or credential typing is required.
1. All tool configurations are in sync across Claude Code, OpenCode, Zoo Code, and Antigravity.
2. When switching machines or pulling a fresh repo clone, run:
   ```bash
   keyway pull -e development
   pwsh .agents/scripts/sync-agents.ps1
   ```
3. Next step: sign off on merging `chore/SCC-432-universal-tools-mcp` via `/smh-close-task-merge-tree`.
