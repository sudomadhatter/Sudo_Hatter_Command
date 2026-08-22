---
IsArtifact: true
ArtifactMetadata:
  title: "Task list — mobile & desktop rule parity (todo item 4)"
  type: task_list
  date: 2026-06-27
  todo_item: 4
---

# Task list (final)

## Investigation
- [x] Confirm it's NOT a mirror issue — `mobile-mode.md` + `git-policy.md` already byte-identical across master/AGY/Fresh (item 3)
- [x] Confirm no `desktop-mode.md` exists — desktop = implicit default in `git-policy.md` + `artifacts-always-first.md` (by design)
- [x] Map the real divergence: AGENTS.md lane-wiring (AGY ✅ reference · main ⚠️ partial · Fresh ❌ missing); trigger `CLAUDE_CODE_REMOTE=true` scattered, not owned by the rule

## Execution
- [x] Step 1 — `mobile-mode.md`: canonicalize `CLAUDE_CODE_REMOTE=true` trigger + lane boundary as single source; align Override 1 to `claude/*` push + PR→`main_debug`
- [x] Step 2 — `main` AGENTS.md: §3 names the trigger; §6 `GIT — desktop default` label + web/mobile pointer + branch-model note
- [x] Step 3 — Fresh AGENTS.md: §4 web/mobile load pointer + §8 `DESKTOP DEFAULT` label + branch-model note (was missing entirely)
- [x] Step 4 — project template AGENTS.md: same pointer + desktop-default label (new clones born wired)
- [x] Step 5 — re-vendor `mobile-mode.md` to both projects; verify md5 identical + trigger present where it was absent

## Verified
- [x] `mobile-mode.md` md5 `5e64f4f…` identical across all 3
- [x] `CLAUDE_CODE_REMOTE`: rule 4 · main 2 · Fresh 2 · template 2 · AGY 2 (was 0 in rule/main/Fresh/template)
- [x] `desktop default` label: main/Fresh/template/AGY all 2
- [x] git status shows ONLY item-4 files in all 3 repos; all on `main_debug`

## Pending (Daniel)
- [ ] Run the 3 surgical commits (walkthrough → Your Actions) on `main_debug`
- [ ] (AGY commit includes the authorized `todo_list.md` cross-out of items 2-3)

## Out of scope → later
- [ ] Rename project folders to match git repos (todo item 5 — next)
- [ ] `Ingestion_pipeline_AvCh` migration (old layout)
