---
title: Task list snapshot — artifacts policy finish (work-from-cwd)
type: task-list
date: 2026-06-25
---

# Final TodoWrite snapshot

- [x] **WS-A** — `_artifacts/README.md` (the structure how-to), rewritten to **work-from-cwd**
- [x] **WS-B** — Reconciled the remaining stale `_artifacts/<workspace>/` refs to work-from-cwd:
  `AGENTS.md` §3, `_docs/workspace-standard.md` Part-1 (L58/71/84) + appendix, master `.agents/rules/artifacts-always-first.md`
- [x] **WS-D** — Refreshed home-base `_docs/repo-map.md` (`--mode content`); drift check verified clean
  (hook + curated header were already wired by the merge)
- [x] **Memory** — Renamed `artifacts-live-with-the-work` → `artifacts-go-where-you-work-from`; old deleted; `MEMORY.md` repointed
- [x] **WS-E** — Verified (drift clean, stale-ref sweep) + hand off (this `walkthrough.md`, `task-list.md`,
  `_home` `active-context.md`, `INDEX.md` row)
- [x] **WS-C** — **DROPPED** — work-from-cwd makes clean-bmad's home-base bucket correct (no migration; clean-bmad untouched)

## Not done by the agent (by design)
- [ ] **Commit + push** the home-base policy work — git-policy (command in `walkthrough.md`).

## Deferred (separate pass)
- [ ] `/sync-agents` propagation of the updated `artifacts-always-first.md` to each project's vendored copies.
