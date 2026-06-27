---
IsArtifact: true
ArtifactMetadata:
  title: "Walkthrough — one command master, one sync, three platforms in step"
  type: walkthrough
  date: 2026-06-27
  todo_item: 2
---

# Walkthrough — opencode + gemini now mirror claude's command standard

## The divergence I found
The canonical invocable set is **`.agents/commands/` (36)**. Claude and opencode project-local dirs already
mirrored it — but **gemini was fed from the wrong directory**: `/slash_command_updating` sourced
`.agents/workflows/` (4 *reference* docs), not `.agents/commands/`. Result:
- gemini global cache (`~/.gemini/antigravity/global_workflows`) = **14 stale**: 3 dead ghosts
  (`1_ccps_boot-context`, `1_ccps_update-active-context`, `1_looping-dev-cycle`) + **~25 commands missing**;
- opencode global cache (`~/.config/opencode/commands`) = **empty**;
- two overlapping sync commands (`/sync-agents` + `/slash_command_updating`) = the "not clean" part.

Root cause: Antigravity calls its invocable units "workflows," so someone wired its feed to `.agents/workflows/`
by name. Our canonical source is always `.agents/commands/`.

## The standard I codified (approved scope: fix-source + unify + platform-specific)
1. **One master** — `.agents/commands/` is the single canonical `/slash` set.
2. **One sync** — `/sync-agents` (engine `sync-agents.ps1`) now feeds **every** surface: `.claude/{commands,skills}`,
   `.opencode/{commands,agent}`, **and** both machine-global caches on a lobby sync. `/slash_command_updating`
   became a thin alias → `sync-agents.ps1 -GlobalsOnly` (keeps the name + opencode-restart reminder; one engine).
3. **Platform reach tag** — optional frontmatter `platforms: [claude, opencode, antigravity]`. **Absent = universal.**
   Tagged: `autopilot_claude`, `autopilot_mobile`, `bmad-dev-story_AP`, `1_self-audit-stress-test_AP`,
   `bmad-code-review_AP` → `[claude]`; `autopilot_opencode` → `[opencode]`. The command self-declares its reach.
4. **Ghost purge, preserve FOREIGN `bmad-*`** — global caches mirror-exact, but a `bmad-*` file the master
   doesn't own is left alone (BMAD installs its own global agents/workflows).
5. **`.agents/workflows/` clarified** — in-repo reference process-docs; never pushed to a command cache.

## Files changed
- `.agents/scripts/sync-agents.ps1` — platform-filtered per-file command copy; per-surface purge policy
  (local: purge only master-managed-but-ineligible; global: mirror-exact, preserve foreign `bmad-*`); folded-in
  global-cache refresh with **resilient per-cache guards**; `-GlobalsOnly` / `-NoGlobals` switches.
- `.agents/commands/sync-agents.md` — documents the unified one-command-all-surfaces behavior.
- `.agents/commands/slash_command_updating.md` — slimmed to the globals-only alias.
- `.agents/commands/INDEX.md` — sync line + `platforms:` convention.
- 6 command files — one `platforms:` line each.
- `_docs/workspace-standard.md` — new Part-2 subsection "Command sync & platform reach — one master, three platforms".
- `AGENTS.md` — §4 tool-dirs row + §8 portability one-liners.
- Synced copies under `.claude/commands/`, `.opencode/commands/`, `.claude/skills/INDEX.md` (see note below).

## Test output (actual)
```
sync-agents: .claude\commands   -> 35 cmds
sync-agents: .opencode\commands -> 31 cmds
WARNING: SKIPPED opencode global cache '...\.config\opencode\commands' - path not writable (broken junction...)
sync-agents: antigravity global -> 30 cmds  (...\.gemini\antigravity\global_workflows)
```
Before → after, and filter proof:
```
.claude/commands   36 -> 35   (drops autopilot_opencode; keeps autopilot_claude + the _AP)
.opencode/commands 36 -> 31   (drops the 5 claude-only; keeps autopilot_opencode)
gemini global      14 -> 30   (3 ghosts purged; analyst/architect/dev/new-project/merge_main_debug/... now present)
gemini global: none of the 6 platform-tagged commands present  (correct)
our universal bmad-help / bmad-master present on every surface  (correct)
actual dir file-counts == eligible counts (no lingering files)  (purge verified)
```

## What fought back (caught by testing — fixed)
- **Broken junction.** `~/.config/opencode/commands` is a **junction → `…\scratch\OpenCode`, whose target is
  missing** — that's why opencode's global cache was empty all along, and why my first run's `New-Item`
  silently no-oped then crashed at Copy-Item. Fix: each global cache is now guarded independently
  (`New-Item` + a `Test-Path` post-check) and **skips with a warning** instead of crashing the run — one bad
  path can't block the other cache or the (already-done) local sync. **I did NOT touch your junction** (your
  env setup, your call — see Your Actions).
- **Over-broad `^bmad-` preserve.** My first purge preserved ANYTHING starting `bmad-`, so our own claude-only
  `bmad-dev-story_AP` / `bmad-code-review_AP` lingered in `.opencode/commands`. Fix: check "is this one of OUR
  master commands?" **before** the foreign-bmad preserve, so our commands follow eligibility and only *foreign*
  `bmad-*` (BMAD's own install) is preserved. Re-verified: `.opencode/commands` settled at exactly 31.

## Note on `.claude/skills/INDEX.md` (untracked)
`.agents/skills/INDEX.md` is tracked but its `.claude/` mirror was missing from git; the skills robocopy in this
run restored it. It's a faithful copy of the master — included in the commit to complete the mirror.

## Your Actions

**1 — Commit (home base; surgical, explicit paths; pre-existing/not-mine changes excluded):**
```bash
git add \
  .agents/scripts/sync-agents.ps1 \
  .agents/commands/sync-agents.md .agents/commands/slash_command_updating.md .agents/commands/INDEX.md \
  .agents/commands/autopilot_claude.md .agents/commands/autopilot_mobile.md .agents/commands/autopilot_opencode.md \
  .agents/commands/bmad-dev-story_AP.md .agents/commands/1_self-audit-stress-test_AP.md .agents/commands/bmad-code-review_AP.md \
  .claude/commands/ .opencode/commands/ .claude/skills/INDEX.md \
  AGENTS.md _docs/workspace-standard.md \
  _artifacts/_main/2026-06-27_unify-command-sync/ _artifacts/INDEX.md
git commit -m "feat(sync): one canonical command master mirrored to claude+opencode+gemini; platforms: tag; ghost-purge; resilient globals" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
# do NOT add: .claude/settings.json (pre-existing, not this work) or _artifacts/_main/2026-06-27_update-maps-fanout/ (separate)
```

**2 — Opencode junction — ✅ DONE (you authorized "fix 2").** Restored the missing junction *target*
`…\scratch\OpenCode` (kept your junction, did not replace it with a plain dir), confirmed it resolves +
is writable, then `/sync-agents -GlobalsOnly` populated **opencode global = 31 cmds** (autopilot_opencode
present; all 5 claude-only absent; universals present).

**3 — Restart opencode** so it picks up the refreshed global commands. *(You said you'll do this.)*

## Flagged for item 3 (not done here)
- Re-vendoring `.agents/` into the two projects (so they get the new sync engine + tagged commands) is a
  separate propagation pass — belongs with item 3 (fix clean-workspace mirroring).
