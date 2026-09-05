---
name: command-center-sudo-skills
description: "The /sudo-* dev flow is now skill-launchers in the lobby that target a child project via active-project.txt; this surface only registers SKILLS as typeable slash, not commands."
metadata: 
  probe: "test -e .agents/active-project.txt"
  node_type: memory
  type: project
  originSessionId: 5421655a-fc6c-40ca-966a-d7eaa2b44a08
---

The lobby (Sudo_Hatter_Command) is a **command center** that drives the sudo dev flow against a CHILD project under `Projects/` (10+ projects, all cloned from fresh-workspace, each carries its own full `_bmad/` engine).

**Why `/sudo-*` did nothing while `/bmad-dev-story` worked:** the Antigravity/VSCode-Claude surface only registers user-typeable `/slash` from `.claude/skills/<name>/SKILL.md`, NOT from `.claude/commands/`. bmad-* were skills; sudo-* were only commands. See [[antigravity-uses-workflows-not-commands]].

**The fix (2026-06-28):**
- 6 interactive sudo commands (`boot-sprint-memory`, `write-story-tests`, `dev-story-tests`, `self-audit`, `code-review`, `update-sprint-memory`) now exist as thin **skill launchers** in `.agents/skills/sudo-*/SKILL.md` that just say "read `.agents/commands/sudo-<name>.md` and run it" — single canonical body, no drift.
- Those 6 command files got `platforms: [opencode, antigravity]` (claude dropped) so sync purges them from `.claude/commands` — avoids a name collision with the new skills. The `_AP` autopilot twins stay claude commands.
- Each canonical command body gained a **Step 0 — Resolve the target project**: leading `$ARGUMENTS` project name → `.agents/active-project.txt` pointer → ask Daniel; then binds every `{project-root}` / bare path / nested bmad-* skill under `Projects/<child>`. A "Self" branch (`_bmad/bmm/config.yaml` present + no `Projects/` subfolder → `PROJECT_ROOT=.`) keeps it correct when a child is opened directly.
- `.agents/active-project.txt` holds the active child (seeded `AGY_AVIATIONCHAT`). Daniel switches focus by telling the agent or running `/sudo-boot-sprint-memory <project>`.

Edit the master `.agents/` then run `sync-agents.ps1` to propagate (see [[toolkit-sync-covers-agents-not-docs]]). No command is ever too big for a surface: every Antigravity door is a thin launcher and so is every Claude/Codex skill door (SCC-370, see [[antigravity-uses-workflows-not-commands]]).
