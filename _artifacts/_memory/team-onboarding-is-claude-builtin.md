---
name: team-onboarding-is-claude-builtin
description: "The /team-onboarding slash entry is a built-in Claude Code command, NOT a toolkit file — don't re-hunt or try to delete it"
metadata: 
  node_type: memory
  type: reference
  originSessionId: e1569d18-80f6-4d02-84df-7509e4461fd2
  modified: 2026-07-21T21:22:05.294Z
---

`/team-onboarding` (description: "help teammates ramp on Claude Code with help from your usage") is a
**built-in Claude Code CLI command**, compiled into the binary — not a file in `.agents/commands`,
`.claude/commands`, `.claude/skills`, any project tool dir, plugins, or `.claude.json`.

Confirmed 2026-07-21 by exhaustive sweep: lobby (2,843 files) + all 7 projects (20,070 files) + all
global caches + plugin catalog — ZERO matches by filename or content. It shows only in Claude Code (not
opencode/Codex/Antigravity) because it's Claude's own feature.

**Why it matters:** it is NOT a dead/skeleton command from the Gemini team's slash edits, despite looking
like one. Built-ins can't be deleted via file removal or `/sync-agents` — only (maybe) hidden via a Claude
Code setting. Don't waste a search on it again. The toolkit command surface is otherwise clean (manifest
purge holding — see [[sync-leaves-local-command-ghosts]]).
