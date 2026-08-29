---
name: zoo-code-replaces-roo-code
description: "Operator switched Roo Code -> Zoo Code and Antigravity IDE -> VS Code (2026-08-29); Zoo keeps .roo/* paths, settings namespace is zoo-code.*, not yet in sync-agents (SCC-349)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 7819434c-21de-47ca-a4e3-8d39fabdbc3a
  modified: 2026-08-29T15:33:01.817Z
---

Roo Code was archived upstream 2026-05-15 (frozen at v3.54.0; its auto-approve bugs will never be
fixed). The operator switched to **Zoo Code** (`ZooCodeOrganization.zoo-code`), the coordinated
community fork (biweekly releases, v3.81 as of 2026-08-29), and moved daily driving from the
Antigravity IDE to **VS Code** — Antigravity's "Always Proceed still prompts every command" bug is
upstream and unfixable from our side.

Facts that bite:
- Zoo deliberately **keeps the `.roo/*` paths** (`.roomodes`, `.roo/commands/`, `.roo/rules-{slug}/`) — do not invent `.zoo/` dirs.
- VS Code settings namespace renamed: `roo-cline.*` -> **`zoo-code.*`** (`zoo-code.allowedCommands` / `deniedCommands`, tracked in `.vscode/settings.json` for Mac+PC parity).
- Zoo reads AGENTS.md natively (`zoo-code.useAgentRules`) — house law applies with no sync.
- Zoo is **NOT in sync-agents yet** — platform list is hardcoded to four; adding `zoo` as platform 5 is SCC-349 (under SCC-346, the approval-fix parent).
- Zoo auto-approve toggles are per-machine extension state; the export/import file carries API keys — never commit it.
- deepagents (langchain) was assessed and parked: NO-GO for IDE integration.

See [[two-machines-mac-and-pc]], [[codex-is-fourth-platform]], [[antigravity-uses-workflows-not-commands]].
