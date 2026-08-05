---
name: sudo-update-scrum-board-five-zones
description: /sudo-update-scrum-board (ex /update-personal-sprint-map) rebuilds sprint_scrum_board_map.md as a five-zone board; parallel lanes are gated on GROUNDED stories — write stories first to unlock lanes.
metadata: 
  node_type: memory
  type: project
  originSessionId: b80fc075-1753-4842-9946-7a790b19dc98
  modified: 2026-08-03T00:26:00.860Z
---

**Renamed 2026-08-02** (operator-directed redesign): command `/update-personal-sprint-map` →
`/sudo-update-scrum-board`; board doc `sprint-dependency-map.md` → `sprint_scrum_board_map.md`
(all projects: AGY, Fresh, NEXgen). Old names purged everywhere by the sync manifest — if either
old name resolves, the surface is stale; re-run `/sync-agents`.

**Five zones, fixed order, ~150-line cap:** 🎯 Right now (≤8 lines, merged at-a-glance+do-next,
no unique data — pointers only) → 🧵 **Parallel Approved Stories** → 🛠 Work queue (ONE table:
🟢 ready → 🔴 blocked → 📋 pipeline, a command per row) → 👤 Your actions (operator-owed,
close-conditions stapled to the triggering action) → 📚 Reference (done epics collapse to one NAMED
line; settled rulings stay).

**Display rule (operator-driven, 2026-08-02): show the ANSWER, never the math.** The 🧵 zone prints
an approved list (membership = safe beside every other member) + a one-verdict-per-ticket table:
🟢 approved · 🔒 after `<ticket>` · ⏳ waiting on `<in-flight story>` · 📝 no story. Pairwise
notation ("✅ vs C+D"), lane letters, and "not yet checked" are BANNED — the operator found the
lane-letter matrix confusing; verdicts the reader must assemble by joining rows defeat the board.

**The team-lane rule (operator runs 2–4 teams):** a parallel verdict requires both touch-sets, which
exist only for GROUNDED stories (branch diff > implementation_plan > story-file Dev Notes surfaces).
Ungrounded = never lane-eligible; the board says "write the story first", never guesses. **The
operator's lever: to develop an epic in parallel, write all its stories first.** An in-flight lane
with unknown surfaces poisons every cross-verdict until its ① plan lands (21.8b, 2026-08-02).

**Why:** the old board buried the operator's actions under agent machinery and grew a journal; the
07-31 incident proved unverified "parallel" claims schedule real collisions (`check_cost_cap`).

**Freshness machinery (built 2026-08-02, v2 same day):** close-out (`/sudo-update-sprint-memory`) has
**Step 4.5** — the YAML flip and the full board rebuild land in the SAME commit. Safety net: AGY
`scripts/git-hooks/board-stale-stamp.sh` (post-commit + post-merge; machine-local install via
`install-hooks.ps1` — guide: lobby `_my_resources/migrations/git-hooks-board-stale-install.md`,
new-machine step 5). v2 flags **per-story drift**: diffs the YAML from the board's last-reconcile
commit, stamps a banner listing every changed key `old → new` AND an inline `⚠️` flag beside each
changed story's board mentions (markers `STALE-STAMP` / `YAML-DRIFT`); self-updating across commits;
comment-only YAML edits ignored. The rebuild treats the listed keys as its work-list and clears all
markers. Main-worktree guard; kill switch = `scripts/git-hooks/DISABLE`.

**OPERATOR RULING (Daniel, 2026-08-02): no background model ever updates this board.** A "cheap
Sonnet status refresher" was designed and REJECTED before build — a half-refreshed board looks
fresher than it is and dilutes the banner. The banner's job is to tell the operator to run
`/sudo-update-scrum-board` with a smart model; the system may be stale, never silently stale, and
never auto-written. Don't re-propose background refreshers.

**How to apply:** rebuild via the command, never freehand; keep zone order and the cap; never put
narrative/history on the board (git + memory hold it); parallel vocabulary only in 🧵 with dated
evidence. Related: [[sprint-dependency-map-recommends-stale-work]], [[parallel-lanes-fix-the-same-finding]],
[[agy-epic-keys-rot-silently]].
