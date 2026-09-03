# Implementation Plan — SCC-383: story lane checks the epic branch against main

**Ticket:** SCC-383 · **Branch:** `chore/SCC-383-epic-sync-check` · **Date:** 2026-09-03
**Lane:** `lane_qualify.py` → `TASK` ("this changes the development system")
**Approval:** Mr. Hatter, 2026-09-03 — *"approved lets clean this up so we are not blocking all the
teams"*, answering the Lane 2 ask in
[the AviationChat plan](https://github.com/sudomadhatter/AGY_AVIATIONCHAT/blob/epic/AVCH-100-epic-24-agent-quality/_artifacts/epic_24/epic-sync-and-merge-guard/implementation_plan.md).

## 1. Goal and background context

The story lane keeps a story worktree current with its epic branch. **Nothing keeps the epic branch
current with `main`.** Step 0.6 of `/cicd-dev-story-tests` merges `origin/epic/<KEY>-<slug>` down into
the story tree; the tier above it has no step at all, so an epic branch drifts and every story cut
from it inherits a stale base.

This is not cosmetic. AviationChat's `main` carries the ruleset *"main write gate (AVCH-111)"* with
`strict_required_status_checks_policy: true`, which means **a branch behind `main` cannot merge** —
the epic's own PR is refused at the end of the epic.

Measured on Epic 24 today: the epic branch was **9 commits behind `main`**, and both in-flight story
branches (AVCH-103, AVCH-108) were **105 behind the epic**, cut from a base that predated the 24.6
rebuild of every greeting surface AVCH-108 depends on.

## 2. Proposed changes

**(a) [cicd-dev-story-tests.md](../../../.agents/commands/cicd-dev-story-tests.md) Step 0.6** — a new
item 1 ahead of the existing "absorb the EPIC branch" (which becomes item 2; the list renumbers
2→3, 3→4), and the step heading gains the new check:

```bash
cd "$PROJECT_ROOT" && git fetch origin && git rev-list --count origin/epic/<JIRA-KEY>-<slug>..origin/main
```

`0` → carry on. Anything else → **STOP and report the count.**

**It stops rather than syncing, deliberately.** Merging `main` into the epic branch is a write to the
epic branch, which takes Mr. Hatter's sign-off (`git-policy` write gate), and it is an epic-wide
action that must not happen silently inside one story's lane.

**(b) [workflows_testing_SOP.md](../../../docs/_scc_sops_prds/workflows_testing_SOP.md)** — same
commit, per `sop-currency` (this changes what the operator sees when starting a story). Two edits: a
new paragraph opening the ② section, and the command-atlas node for Step 0.6 gains
`STOP if the epic is behind main`.

## 3. Open questions

None. Scope is fixed by the approved Lane 2 description.

## 4. Verification plan

| # | Check | Command | Pass |
|---|---|---|---|
| 1 | Lobby enforcement suite | `python3 .agents/scripts/tests/run_all.py` | exit 0 |
| 2 | Step 0.6 renumbering intact | `grep -n "^1\.\|^2\.\|^3\.\|^4\." .agents/commands/cicd-dev-story-tests.md` | 1–4 in order, no duplicates |
| 3 | SOP carries the change | `grep -c "STOP if the epic is behind main" docs/_scc_sops_prds/workflows_testing_SOP.md` | ≥1 |
| 4 | sop-currency gate | the commit itself | accepted without `[sop-ok]` |

## 5. Risk and rollback

Documentation and procedure only — no script, no hook, no executable path. The change adds a stop to
a command; worst case is an extra halt the operator waves through. Rollback is `git revert` of the
single commit.
