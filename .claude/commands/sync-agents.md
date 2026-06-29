---
description: Sync the master .agents toolkit into every command surface — local tool dirs (lobby or a project) AND the opencode + Antigravity global caches. One command, three platforms.
---

# /sync-agents

Push the master `.agents/` toolkit into every place a command/skill can resolve. The canonical invocable set
is `.agents/commands/` and it mirrors to **all three platforms** (Claude, opencode, Antigravity/Gemini).
**Authorship stays single-source — always edit `.agents/`, never the copies.**

What it touches:
- **Local tool dirs** — `.claude/{commands,skills}`, `.opencode/{commands,agent}`.
- **Machine-global caches** (on a LOBBY sync) — `~/.config/opencode/commands` and
  `~/.gemini/antigravity/global_workflows`, so opencode + Antigravity see the same set Claude does.
- **Project target** — also vendors master's `.agents/` into the repo so it's clone-safe. The vendor is
  **additive**: a project's `.agents/` is a **hybrid** (master toolkit **plus** project-owned `rules/`,
  `skills/`, and `bmad/` that master lacks/owns-per-project), so it is **never** mirror/purged wholesale — the
  only deletion is the narrow stale-`workflows/`-command-ghost prune. **`bmad/` is excluded from the vendor
  entirely** — its `project_name` is per-project identity and BMAD self-installs per repo, so master never
  overwrites it. (A project sync does NOT touch the global caches; globals reflect the lobby's canonical set.)

**Platform reach.** A command may declare `platforms: [claude, opencode, antigravity]` in its frontmatter.
**Absent = universal** (all three). The sync copies a command only to the platforms it lists — e.g.
`/autopilot_claude` (claude-only) never lands in the opencode/gemini surfaces. Global caches are
**mirror-exact** (stale ghosts purged) except `bmad-*` (BMAD's own global install is preserved).

Argument (`$ARGUMENTS`): optional target path. No argument = sync the home-base lobby (root) + globals.

Run (PowerShell):

```
& ".agents/scripts/sync-agents.ps1" -Target "$ARGUMENTS"
```

(If `$ARGUMENTS` is empty, run `& ".agents/scripts/sync-agents.ps1"` with no `-Target`.)

Switches: `-GlobalsOnly` (refresh only the two global caches — what `/slash_command_updating` delegates to) ·
`-NoGlobals` (local tool dirs only) · `-WhatIf` / `-DryRun` (preview every copy/delete action without touching disk).

After it runs, report the per-surface counts it prints (`.claude/commands`, `.opencode/commands`, opencode
global, antigravity global, and — for a project — the vendored `.agents/`). On a globals refresh, remind Daniel
to **restart opencode** so the global commands are picked up in other projects.

### Preview mode
```powershell
& ".agents/scripts/sync-agents.ps1" -WhatIf
```
Use `-WhatIf` (or `-DryRun`) before a real sync to see which commands would be copied or purged on each surface,
which workflow mirrors would be regenerated, and which directories would be created. No files are changed.
