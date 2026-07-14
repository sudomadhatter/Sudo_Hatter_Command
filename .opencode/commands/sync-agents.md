---
description: Sync the master .agents toolkit into every command surface — local tool dirs (lobby or a project) AND the opencode + Antigravity + Codex global caches. One command, four platforms.
---

# /sync-agents

Push the master `.agents/` toolkit into every place a command/skill can resolve. The canonical invocable set
is `.agents/commands/` and it mirrors to **all four platforms** (Claude, opencode, Antigravity/Gemini, Codex).
**Authorship stays single-source — always edit `.agents/`, never the copies.**

What it touches:
- **Local tool dirs** — `.claude/{commands,skills}`, `.opencode/{commands,agent}`.
- **Machine-global caches** (on a LOBBY sync) — `~/.config/opencode/commands`,
  `~/.gemini/antigravity/global_workflows`, and **`~/.codex/prompts`**, so opencode + Antigravity + Codex see
  the same command set Claude does.
- **Codex skills mirror** (on a LOBBY sync) — the 56 `bmad-*` skills from `.claude/skills` are mirrored to
  **`~/.codex/skills`**. Codex reads `AGENTS.md` and `.agents/skills/` natively (so rules + our own skills need
  no work), but BMAD installs its skills to `.claude/skills`, which Codex doesn't read — this mirror closes that
  gap so BMAD is reachable from Codex via `/skills`. (`~/.codex/prompts` is Codex's `/commands` equivalent,
  invoked `/prompts:<name>`; OpenAI marks custom prompts deprecated-in-favor-of-skills but they work today.)
- **Project target** — also vendors master's `.agents/` into the repo so it's clone-safe. The vendor is
  **additive**: a project's `.agents/` is a **hybrid** (master toolkit **plus** project-owned `rules/`,
  `skills/`, and `bmad/` that master lacks/owns-per-project), so it is **never** mirror/purged wholesale — the
  only deletion is the narrow stale-`workflows/`-command-ghost prune. **`bmad/` is excluded from the vendor
  entirely** — its `project_name` is per-project identity and BMAD self-installs per repo, so master never
  overwrites it. (A project sync does NOT touch the global caches; globals reflect the lobby's canonical set.)

**Platform reach.** A command may declare `platforms: [claude, opencode, antigravity, codex]` in its frontmatter.
**Absent = universal** (all four). The sync copies a command only to the platforms it lists — e.g.
`/autopilot_claude` (claude-only) never lands in the opencode/gemini/codex surfaces, and the `_AP` headless
commands (`[claude, opencode]`) never reach the Antigravity or Codex menus. Global caches are **mirror-exact**
(stale ghosts purged) except `bmad-*` (BMAD's own global install is preserved).

Argument (`$ARGUMENTS`): optional target path. No argument = sync the home-base lobby (root) + globals.

Run (PowerShell):

```
& ".agents/scripts/sync-agents.ps1" -Target "$ARGUMENTS"
```

(If `$ARGUMENTS` is empty, run `& ".agents/scripts/sync-agents.ps1"` with no `-Target`.)

Switches: `-GlobalsOnly` (refresh only the machine-global caches — opencode + Antigravity + Codex prompts + the
Codex bmad-* skills mirror — what `/slash_command_updating` delegates to) ·
`-NoGlobals` (local tool dirs only) · `-WhatIf` / `-DryRun` (preview every copy/delete action without touching disk).

After it runs, report the per-surface counts it prints (`.claude/commands`, `.opencode/commands`, opencode
global, antigravity global, **codex prompts, codex skills**, and — for a project — the vendored `.agents/`). On a
globals refresh, remind Daniel to **restart opencode** so the global commands are picked up in other projects.

> **First-machine note:** `-WhatIf` reports a global cache as **SKIPPED** when its dir doesn't exist yet (it
> can't verify writability without creating it) — expected on a brand-new machine for any of the caches,
> including `~/.codex/prompts`. A real run creates the dir first, then copies. The Codex **skills** mirror
> previews correctly under `-WhatIf` regardless.

### Preview mode
```powershell
& ".agents/scripts/sync-agents.ps1" -WhatIf
```
Use `-WhatIf` (or `-DryRun`) before a real sync to see which commands would be copied or purged on each surface,
which workflow mirrors would be regenerated, and which directories would be created. No files are changed.
