# Universal MCP & Tool Connections Research Spec — 2026-09-04

Ticket: [SCC-395](https://sudo-command.atlassian.net/browse/SCC-395) · Branch: `chore/SCC-395-universal-tools-mcp` · Date: 2026-09-04

## Task Checklist

- [x] Researched MCP & CLI tool fragmentation across Claude Code, Zoo Code, OpenCode, Antigravity, and Codex
- [x] Formulated hybrid architecture (master `connections.json` + `tool_sync.py` + `tool-connections` skill + `rule-trigger.py` hook)
- [x] Documented architecture & spec in `universal-tools-research.md`
- [x] Formatted and applied fast-read ticket description outline via `jira_ticket.py describe` to SCC-395 on the live Jira board
- [x] Posted reference comment on Jira workitem SCC-395 linking in-tree research artifacts

## What changed

- `_artifacts/_main/2026-09-04_scc-395-universal-tools-mcp/tickets/SCC-395.md`: Version-controlled fast-read Jira outline source.
- `_artifacts/_main/2026-09-04_scc-395-universal-tools-mcp/universal-tools-research.md`: Full architectural research spec, JSON schema, and multi-platform sync design.
- `_artifacts/_main/2026-09-04_scc-395-universal-tools-mcp/task.yaml`: Task manifest.
- `_artifacts/_main/INDEX.md`: Appended index row for this artifact directory.

## Evidence

- `python3 .agents/scripts/lane_qualify.py` returned `LIGHT`.
- `jira_ticket.py describe --key SCC-395` updated live Jira description successfully.
- `acli jira workitem comment create --key SCC-395` added reference comment successfully.

## Your Actions

No immediate action required; implementation will proceed under SCC-395 when scheduled.
