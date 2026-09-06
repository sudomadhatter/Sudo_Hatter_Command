# SCC-426 — the hand-off said Epic 24 was pending; it shipped — walkthrough

**Ticket:** SCC-426 · **Lane:** `chore/SCC-426-handoff` off `origin/main` · **Date:** 2026-09-06

## Why

`_artifacts/_main/active-context.md` opened with *"EPIC 24 PHASE 1 IS GATED GREEN AND AWAITING THE
OPERATOR'S TWO MERGES"* and described trunk mode as a plan awaiting approval. Both were true when
written and false by the end of the session: Epic 24 merged at `77f0cfaa` and is live in production,
and trunk mode landed as SCC-423 (`41fb27a1`, record fix `10ecf899`) and closed.

The hand-off is the first thing the next session reads. Left alone it would have opened believing
production was still waiting on the operator — **the same shape as the AVCH-80 incident**, where the
ruling that mattered was invisible from where the agent was standing.

## What changed

One file, one block replaced. The new block records: the merge sha and gate numbers; that the deploy
was **verified rather than assumed** (revision `aviationchat-backend-00082-joc`, private smoke test on
its `sha-77f0cfa` tagged URL, promotion, then a direct probe of `/health` and the site); that the epic
branch and both lanes are pruned; that **AVCH-100 stays In Progress on purpose** because 24.8 and 24.9
are unwritten by the 2026-08-27 ruling and are now built from `main`; the trunk-mode summary with its
git-query switch and the two things that deliberately did not change; and the two open operator-owned
items, AVCH-136 (`www` NXDOMAIN) and SCC-424 (a CI-only flake in `test_repo_template.py`).

Three gate lessons from the ship are carried into the block, because they will recur on every future
epic→main PR: that PR is the first thing that ever lints most of an epic (99 changed files at once);
**editing a file is what pulls it into the changed-file gate**, so one type fix dragged in a file
carrying 6 ruff + 29 pyrefly errors and was reverted in favour of a call-site fix; and a vitest mock
keyed on a call counter failed only under CI load.

## Gates

| Gate | Result |
|---|---|
| `run_all.py` | 81/81 files passed (run this lane) |
| `task_preflight.py` | clear to close out and merge |

Docs-only: no code path is touched, so the enforcement suite is the whole floor.

## Your Actions

- [x] The merge itself — lands via this branch's PR.
