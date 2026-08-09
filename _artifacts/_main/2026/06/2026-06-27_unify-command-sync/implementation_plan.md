---
IsArtifact: true
ArtifactMetadata:
  title: "Implementation plan — unify command sync; mirror opencode + gemini to claude's standard"
  type: implementation_plan
  date: 2026-06-27
  todo_item: 2
---

# Plan — one command master, one sync, three platforms in step

**Todo item 2:** *"make sure that the opencode and gemini workflows also mirror more closely the way
claude handles this."* Daniel's steer: use discretion, do **(1) fix source + (2) unify into one sync**,
**handle the platform-specific commands too**, keep it **streamlined and clean**, reflect the structure's goals.

## The problem (evidence)
- Canonical invocable set = `.agents/commands/` (**36**). Claude + opencode project-local dirs already mirror it.
- **gemini** is fed by `/slash_command_updating` from the WRONG dir — `.agents/workflows/` (**4 reference docs**),
  not `.agents/commands/`. Result: gemini global cache holds **14 stale** entries — **3 dead ghosts**
  (`1_ccps_boot-context`, `1_ccps_update-active-context`, `1_looping-dev-cycle`) + **~25 commands missing**.
- **opencode global** cache (`~/.config/opencode/commands/`) = **empty (0)**.
- Two overlapping sync commands (`/sync-agents` + `/slash_command_updating`) = the "not clean" part.

## The standard I'll codify

1. **One command master.** `.agents/commands/` is the single canonical `/slash` set. Antigravity calls its
   units "workflows," but our source is always `commands/` — this name-match is what caused the bug.
2. **One sync command — `/sync-agents` feeds every surface:**
   - Lobby project-local (existing, additive): `.claude/commands`, `.claude/skills`, `.opencode/commands`, `.opencode/agent`
   - **Globals (lobby only, NEW, mirror-exact):** `~/.config/opencode/commands`, `~/.gemini/antigravity/global_workflows`
   - Project target (existing): vendor `.agents/` + project-local dirs; does NOT touch globals (globals = lobby's job).
3. **Platform reach tag (the "specific" handling).** Optional frontmatter `platforms: [...]` on a command
   declares its reach. **Absent = universal (all three).** Keys: `claude` · `opencode` · `antigravity`.
   Sync copies a command only to the platforms it lists.
   - `claude`-only (5): `autopilot_claude`, `autopilot_mobile`, `bmad-dev-story_AP`,
     `1_self-audit-stress-test_AP`, `bmad-code-review_AP` *(needs the `claude` CLI / are headless agent-to-agent)*
   - `opencode`-only (1): `autopilot_opencode` *(opencode-native stub)*
   - Everything else (**30**) = universal. (`merge_main_debug`, `sync-agents`, `new-project` stay universal —
     useful via `gh`/PowerShell on any platform; each platform has its own git-write gate.)
4. **Ghost purge with preserve.** Global mirror deletes anything not in the eligible set **except `bmad-*`**
   (BMAD's own global install — never ours to purge). Purges the 3 dead gemini ghosts.
5. **commands vs workflows clarified.** `.agents/workflows/` stays **in-repo reference process-docs** (read via
   routing tables), NOT pushed to any command cache. Only `.agents/commands/` mirrors out.

## Files I'll change (all gated on this approval)

| File | Change |
|---|---|
| `.agents/scripts/sync-agents.ps1` | Add global refresh (opencode + antigravity) sourced from `.agents/commands/`; per-file copy honoring `platforms:`; ghost-purge w/ `bmad-*` preserve; new switches `-GlobalsOnly` / `-NoGlobals`. Preserve all existing project-local + vendor behavior. |
| `.agents/commands/sync-agents.md` | Document: one command, all surfaces; globals on lobby sync; the `platforms:` tag. |
| `.agents/commands/slash_command_updating.md` | Slim to a thin alias → `sync-agents.ps1 -GlobalsOnly` (keeps the name + opencode-restart reminder; one engine underneath). |
| 6 command files (listed in §3) | Add one `platforms:` frontmatter line each. |
| `.agents/commands/INDEX.md` | Note the unified sync + the `platforms:` convention. |
| `_docs/workspace-standard.md` | Short new subsection: "Command sync & platform reach" (the canonical standard). |
| `AGENTS.md` | §4 "Lobby tool dirs" row + §8 one-liners → point at the unified sync. |

Then **run `/sync-agents`** (lobby) to apply — propagates the tagged commands into `.claude/`+`.opencode/`
project-local copies AND refreshes both global caches.

## Verify / apply (I'll paste real output)
- opencode global: **0 → ~31** (universal + opencode-only); gemini global: ghosts purged, **→ ~30** (universal),
  `bmad-*` preserved.
- Platform filter proof: `autopilot_claude` absent from gemini + opencode globals; `autopilot_opencode` only in opencode.
- Claude project-local unchanged at 36 (reference).

## Scope guards
- **Globals are machine-local, outside the repo** — running the sync purges the 3 gemini ghosts (dead files,
  regenerable). Not a git change.
- **No project re-vendor here** (consolidating project `.agents/` copies = item 3). This item touches the lobby
  master + the lobby's own tool dirs + the global caches only.
- Git: surgical explicit-path commands handed to you at close; I never commit.

## Out of scope (flag → item 3)
- Re-vendoring `.agents/` into the two projects; legacy `scripts/` dedupe; stray `file_structure_rules/` copy.
