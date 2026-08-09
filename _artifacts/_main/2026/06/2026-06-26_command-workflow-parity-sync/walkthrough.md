---
IsArtifact: true
ArtifactMetadata:
  title: Command/Workflow Parity Sync — Walkthrough
  type: walkthrough
  date: 2026-06-26
---

# Walkthrough — Command/Workflow Parity Sync

## What & why
Daniel flagged that the old `/1_ccps_boot-context` + `/1_ccps_update-active-context` commands still
lingered even though they'd been deleted. Diagnosis: they're **broken thin wrappers** pointing at a
non-existent `@.agent/workflows/1_ccps_*.md` (wrong path, absent file). **aviationchat** already migrated
to the self-contained `/boot-sprint-context` + `/update-sprint-context`; the **lobby** and **clean-bmad**
never got that migration. Mandate: clean-bmad = exact mirror of aviationchat (commands+workflows), lobby =
true superset, then sweep all projects + run `/1_update-maps` for the three core workspaces.

## What I did (step by step)

1. **clean-bmad commands → match aviationchat.** Added `1_update-maps`, `autopilot_claude`,
   `autopilot_opencode`, `boot-sprint-context`, `update-sprint-context`; deleted `1_ccps_boot-context`,
   `1_ccps_update-active-context`, `sm`. Result: 32 commands, **empty diff vs aviationchat**.
2. **clean-bmad workflows → full backfill.** Copied 27 missing workflow files + overwrote `INDEX.md`
   from aviationchat. Result: 29 files, **empty diff vs aviationchat**.
3. **Lobby superset.** Added the 4 aviationchat commands, deleted the broken ccps pair, kept `sm`.
   Lobby now contains every aviationchat command (superset) + `sm`.
4. **Mirror propagation.** `robocopy /MIR` from each workspace's own `.agents/commands` master →
   its `.claude/commands` + `.opencode/commands`. This pushed the new files AND auto-purged stale ones
   (the ccps pair, `sm`, and clean-bmad's ghost `1_live-user-QA-bugs.md`). It also re-synced two
   already-stale lobby mirror files (`1_self-audit-stress-test{,_AP}.md`) back to master. NOTE: I did
   **not** use `/sync-agents` — for a project it vendors the *lobby* master first, which would have
   wrongly re-added `sm` to clean-bmad. Each workspace's own master is authoritative here.
5. **INDEX + docs.** Propagated aviationchat's canonical command `INDEX.md` to lobby + clean-bmad and
   re-synced into mirrors. Fixed two live stale refs: `opus-reviewer.md` (`/1_ccps_update-active-context`
   → `/update-sprint-context`) in lobby + clean-bmad (master + `.opencode/agent` mirror), and the
   `_docs/workspace-standard.md` retire-list (dropped deleted ccps cmd, renamed `autopilot`→
   `autopilot_claude`). Regenerated `_docs/doc-graph.{md,json}` → ccps now 0.
6. **All-projects sweep.** Core 3 clean. **jetChat-AGY** still carries the old ccps command files but
   it's UNCONVERTED (old `.agent/` singular format) — flagged for a separate conversion pass, not touched.
   ingestion / B&L / NEXGen / openCode: clean.
7. **`/1_update-maps` ×3.** Lobby: linter clean (0), no edits. aviationChat: AUTO block was stale
   (pre-existing) → regenerated, now clean. clean-bmad: regenerated (+2 lines, the pre-existing
   `open_tasks/todo_list.md`), drift check clean. Command/workflow changes live under `.agents/` (a
   dot-folder the folder-level maps don't enumerate), so the maps were correctly unaffected by them.

## Verification (actual output)
- `comm -3` clean-bmad vs aviationchat commands → **IDENTICAL**; workflows → **IDENTICAL**.
- lobby is superset of aviationchat commands → **YES**; lobby-only extra = `sm` (intended).
- mirrors == masters for lobby + clean-bmad (`.claude` + `.opencode`) → **empty diffs**.
- ghost/old check across all mirrors → no ccps, no `1_live-user-QA-bugs`, no clean-bmad `sm`.
- `check_maps.py` lobby → **exit 0, all clean**. aviationChat after regen → **clean**.
  clean-bmad drift check → **no nag**.
- live `1_ccps` refs remaining = only `_artifacts/` history + `.agents/.gitnexus/` index artifact
  (gitignored, regenerates) — **zero in live docs/commands/agents**.

## Addendum (post-sweep, Daniel-approved)
A late background scan caught a mirror-only ghost the targeted checks missed. Resolved per Daniel's calls:
- **`autopilot_mobile.md` — PROMOTED + fixed.** It was a real ~100-line mobile/cloud autopilot command
  living only in aviationchat's `.claude/commands` (not master), referencing the dead
  `/1_ccps_update-active-context`. Promoted to aviationchat's `.agents` master, fixed the ref →
  `/update-sprint-context`, and distributed to **clean-bmad + lobby** masters (Daniel: "add it to
  clean-bmad too"). Added an "Autopilot (cloud/mobile)" INDEX row in all three.
- **`sm` INDEX line — DROPPED** from aviationchat + clean-bmad command INDEXes (they list `sm` but have no
  `sm.md`). Lobby keeps it (lobby has the file).
- **aviationchat mirrors — RE-SYNCED.** `/MIR` brought its stale `.claude`/`.opencode` in line with master
  (added 5 missing commands + autopilot_mobile + updated INDEX). ~34 files now match master both ways.
- Final parity re-verified: autopilot_mobile in all 9 locations; all master↔mirror diffs = 0; clean-bmad
  still IDENTICAL to aviationchat; `sm` only in lobby; zero `1_ccps` in any live command mirror.

## Known follow-ups / flags
- **jetChat-AGY** still has the broken ccps commands (unconverted `.agent/` format) — DEFERRED to its
  `.agents/` conversion pass (Daniel did not select it for cleanup now).
- After committing, re-anchor the maps baseline in each repo that has `check_maps.py`:
  `python scripts/check_maps.py --set-anchor` (aviationChat; lobby uses `.agents/scripts/check_maps.py`).

## Your Actions
Three separate repos — review and commit each (I did NOT commit/push, per git-policy):

```bash
# 1) Lobby (home base)
cd "c:/Sudo_Hatter_Command" && git add -A && \
  git commit -m "feat: migrate ccps→sprint-context, add autopilot cmds; lobby command superset"

# 2) aviationChat (map regen + autopilot_mobile promotion + mirror re-sync + INDEX)
cd "c:/Sudo_Hatter_Command/Projects/aviationChat-AGY" && git add -A && \
  git commit -m "chore: promote autopilot_mobile, drop stale sm INDEX line, re-sync command mirrors, refresh repo-map"

# 3) clean-bmad (exact mirror of aviationchat command/workflow set)
cd "c:/Sudo_Hatter_Command/Projects/clean-bmad-workspace" && git add -A && \
  git commit -m "feat: mirror aviationchat command+workflow set (ccps→sprint-context, full workflow backfill)"
```

After committing the lobby + aviationChat:
```bash
cd "c:/Sudo_Hatter_Command" && python .agents/scripts/check_maps.py --set-anchor
cd "c:/Sudo_Hatter_Command/Projects/aviationChat-AGY" && python scripts/check_maps.py --set-anchor
```
