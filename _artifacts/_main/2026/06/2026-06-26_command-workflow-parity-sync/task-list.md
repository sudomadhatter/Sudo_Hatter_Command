---
IsArtifact: true
ArtifactMetadata:
  title: Command/Workflow Parity Sync — Task List
  type: task_list
  date: 2026-06-26
---

# Task List — Command/Workflow Parity Sync

- [x] Phase 1 — clean-bmad commands: +5 from aviationchat, −ccps pair, −sm (→ identical to aviationchat)
- [x] Phase 2 — clean-bmad workflows: backfill 27 files + INDEX (→ identical to aviationchat)
- [x] Phase 3 — Lobby superset: +4 commands, −broken ccps pair, kept sm
- [x] Phase 4 — Propagate masters to `.claude`/`.opencode` mirrors (robocopy /MIR; ghosts purged)
- [x] Phase 5 — Canonical command INDEX → lobby+clean-bmad+mirrors; fixed opus-reviewer + workspace-standard refs; regenerated doc-graph
- [x] Phase 6 — Verify core parity (clean-bmad ≡ aviationchat; lobby superset; mirrors == masters)
- [x] Phase 7 — Swept all 7 projects + lobby (core 3 clean; jetChat flagged unconverted; rest clean)
- [x] Phase 8 — `/1_update-maps` ×3: lobby clean(0); aviationChat regenerated; clean-bmad regenerated
- [x] Phase 9 — Walkthrough + task-list written; per-repo git commands handed off
- [x] Addendum A — Promote `autopilot_mobile` to all 3 masters + fix dead ccps ref → `/update-sprint-context`
- [x] Addendum B — INDEX: dropped stale `sm` line (av+cb), added "Autopilot (cloud/mobile)" row (all 3)
- [x] Addendum C — Re-synced all 3 workspace command mirrors (incl. aviationchat's 5 missing commands)
- [x] Addendum D — Re-verified full parity; regenerated doc-graph (+autopilot_mobile, 0 ccps)
- [ ] DEFERRED — jetChat-AGY ccps cleanup (unconverted `.agent/` format; revisit at its conversion pass)
