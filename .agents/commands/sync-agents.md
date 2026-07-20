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
  only deletions are the narrow stale-`workflows/`-command-ghost prune and the manifest-scoped purge described
  below. **`bmad/` is excluded from the vendor
  entirely** — its `project_name` is per-project identity and BMAD self-installs per repo, so master never
  overwrites it. (A project sync does NOT touch the global caches; globals reflect the lobby's canonical set.)

**Retiring a deleted/renamed command (the sync manifest).** Each target carries a generated
`.agents/.sync-manifest.json` recording exactly what the last run wrote. The next run deletes what **it**
previously wrote and the master no longer owns, so **renaming or deleting a master command now cleans itself up
everywhere** — vendored `.agents/`, `.claude/commands`, `.opencode/commands`, and the globals. Before this
existed, retired commands lingered forever and (because a project's vendored `.agents/` is the *source* for that
project's menus) got re-published on every sync; that's how 8 ghosts from the 2026-07-14 restructure survived in
Fresh until 2026-07-20. Files the sync never wrote — project-authored commands like `/autopilot_glm`, project
`rules/`, BMAD's own installs — are absent from the manifest and **cannot** be purged by it; a project sync
prints them as `project-owned file(s), left alone`. A missing or corrupt manifest fails safe: it purges nothing.
Don't hand-edit the manifest; it's regenerated every run. It is safe to commit (paths are repo-relative).

**Reconciling (`-Status` / `-Reconcile`).** The manifest can only retire what it recorded, so it can't see a
file retired *before* it existed or dropped in by hand. `-Status` gives a git-status-style read-only view of the
invocable surfaces (`.agents/{commands,workflows}`, `.claude/commands`, `.opencode/commands`):

- `M` — the copy differs from master. Either it was hand-edited (master wins; a sync overwrites it) or master
  moved ahead and this copy hasn't synced yet. Either way, a sync resolves it.
- `?` — **orphan**: present here, but master has no such command. Could be a project-authored command or a
  stale ghost — nothing can tell those apart automatically, which is what the keep-list is for.
- `own` — an orphan claimed by `.agents/project-own.txt`, kept forever.

`-Reconcile` resolves the `?`s, and **never guesses**. On a project with no `project-own.txt` it *stages* one
listing every orphan and deletes nothing. You review it and **delete a line to mark that file as a ghost**; the
next `-Reconcile` purges it from every surface. It's `git add` semantics: the list is the staging step, and a
second run is always required before anything is destroyed. `-Status` is read-only; `-Reconcile` honours
`-WhatIf`. `rules/` and `skills/` are deliberately out of scope — they're legitimately hybrid, so orphan
detection there would be noise and purging there would be destructive.

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
`-NoGlobals` (local tool dirs only) · `-Status` (read-only reconciliation report; writes nothing) ·
`-Reconcile` (resolve orphans via the staged keep-list) ·
`-WhatIf` / `-DryRun` (preview every copy/delete action without touching disk).

Check drift across everything with `& ".agents/scripts/sync-agents.ps1" -Maintained -Status`.

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
