# Implementation Plan — AviationChat develops from `main` ("trunk mode"), no epic branch

**Date:** 2026-09-06 · **Operator direction (verbatim):** *"I want to go ahead and push the branch we
were working on to main the epic 24 branch. we will now develope the rest of this with cicd from main
no more branch. so lets make this happen and update all the sprints and documents with this
information."*

**Status:** DRAFT — awaiting the operator's `approved`. The ship of Epic 24 (Part A) runs under the
`/cicd-push-e2e` door on the operator's direct ask and is NOT gated by this plan; Parts B and C edit
project files and are.

## Part A — Ship Epic 24 to `main` (running now, under the door)

Not plan-gated. Recorded here so the sequence reads in one place.

1. Sync lane `claude/AVCH-100-absorb-main-2`, cut from PR #85's tip (`961c985c`, the 24.5 close-out
   docs commit), merges `origin/main @ bd010dd9` (11 commits: AVCH-128/130/131). One conflict, the
   artifact ledger; resolved keeping both sides' rows. Zero product-file conflicts.
2. Gate on the merged tree: backend suite (CI flags) · frontend production build · `/cicd-e2e` ·
   `main_write_gate.py --mode pr` · enforcement suite `run_all.py`.
3. Bookkeeping on the lane (pending tense): ledger row, active-context, board `Last synced` stamp,
   ship walkthrough at `Projects/AGY_AVIATIONCHAT/_artifacts/epic_24/epic-24-ship-to-main/`.
4. PR 1: `claude/AVCH-100-absorb-main-2` → `epic/AVCH-100-epic-24-agent-quality` (the epic ruleset
   refuses a direct push; this is the only road). Supersedes PR #85 (same commit is on it).
5. PR 2: `epic/AVCH-100-epic-24-agent-quality` → `main`. Becomes mergeable the moment PR 1 merges
   (strict up-to-date policy). **Do not press "Update branch" on PR 2** — the epic ruleset refuses it.
6. After the operator's two clicks: `/cicd-push-e2e --after-merge AVCH-100` — verify, watch the
   deploy, verify live, PRD reconcile line, prune the epic branch, comment on AVCH-100.

**Override recorded:** the 2026-09-03 ruling on the board ("do not merge until every story is done and
the operator's full test pass is green") is superseded by the operator's 2026-09-06 direction above.
24.8 and 24.9 stay `backlog` by design (not written until the TESTPILOT run feeds them) and continue
from `main`.

## Part B — The model, stated once

**`main` stays the only long-lived branch and stays live production. Nothing about that changes.**
What changes is where a story lands:

| | Before (epic mode) | After (trunk mode — AviationChat from 2026-09-06) |
|---|---|---|
| Story lane branches from | the epic branch | `origin/main` |
| Story lands on | the epic, by PR, four checks | **`main`, by PR, five checks** (four PR Quality Gate jobs + `main-write-gate`) |
| Who merges | the operator | the operator — unchanged |
| Deploy | once, when the epic ships | **every merge is a deploy** (Cloud Run + App Hosting) |
| E2E tier | CI on every PR + `/cicd-e2e` at ship | CI on every PR (Frontend E2E + Backend E2E jobs) — same coverage, no ship step |
| Board files | ride the epic | ride each lane's PR |
| `/cicd-push-e2e` | ships the epic | not used per story; stays for a future epic elsewhere |
| The switch | the branch name (`-quickdev` or not) | **no `origin/epic/AVCH-*` exists → trunk.** Mechanical, read from git refs like SCC-416's switch |

The ①②③ story ceremony (story file, tests first, review verdict) is unchanged.

### The one tradeoff that needs the operator's call

`main-write-gate` (the server check, AVCH-111) **refuses any `claude/*` source branch by design** —
its comment says "a story lane lands on its epic branch, never on main". Under trunk mode a story
lane must reach `main`. Two ways:

- **(A) Widen the gate — RECOMMENDED.** `.agents/scripts/main_write_gate.py::authorised_branch`
  admits `claude/AVCH-<n>-<slug>` alongside `epic/` and `chore/`; one test case added. Every story
  tool keeps working (worktree lookup by slug, park/resume, close-out preflight all match `claude/`).
- **(B) Name story lanes `chore/` in trunk mode.** No gate change, but the story doors, the
  close-out preflight and the "a `claude/*` on origin means parked" invariant all need patching, and
  the record loses the story/task distinction.

Going with (A) unless told otherwise.

## Part C — Files (two repos, two lanes, both after `approved`)

### C1 — AviationChat: `chore/AVCH-<new>-trunk-mode` off `main`, after PR 2 merges
The first lane to land under the new model, so it demonstrates it.

| File | Change |
|---|---|
| `_bmad-output/implementation-artifacts/sprint-status.yaml` | Epic 24 banner: replace the DO-NOT-MERGE, KEEP-CURRENT and LANDING RULE blocks with the trunk rule + the ship line (PR #, merge sha); rows `24-8`, `24-9` LANDING notes → "lane off `main`, PR into `main`, five checks green, operator merges = deploy" |
| `AGENTS.md` §8 GATES | WORKTREE GATE base = `main`; GIT gate: landing = PR into `main`; BRANCH MODEL paragraph → trunk |
| `.agents/rules/constitution.project.md` | Hard stop becomes: a lane lands on `main` ONLY through a PR the operator merges with all five checks green. AVCH-119 history kept as the why |
| `.agents/scripts/main_write_gate.py` + `.agents/scripts/tests/test_main_write_gate.py` | Tradeoff (A): admit `claude/AVCH-<n>-<slug>`; test pins it (and still refuses a keyless or foreign-key `claude/*`) |
| `_bmad-output/planning-artifacts/epics.md` (Epic 24 inventory) | one landing note: phase 1 shipped via PR #<N> @ <sha>; 24.8/24.9 continue from `main` |
| `_bmad-output/active-context/active-context.md` | Current Sprint Objective block |
| `_bmad-output/history/CHANGELOG.md` | one row |
| `.github/workflows/pr-check.yml`, `pr-check-skip.yml` | **no change** — already run on PRs into `main`; the `epic/**` entry stays (harmless, history) |
| Jira AVCH-100 | comment: phase 1 shipped, continues from `main`; stays In Progress until 24.8/24.9 close |

### C2 — Lobby: `chore/SCC-<new>-trunk-mode`, `/smh-quick-dev` → `/smh-code-review` → `/smh-close-task-merge-tree`

| File | Change |
|---|---|
| `.agents/rules/git-policy.md` | § The epic's mode: third mode **trunk** (no epic branch; the switch is "no `origin/epic/<KEY>-*`"); write-gate table `main` row; "board files live on the epic branch" → "on the lane, ride its PR" |
| `.agents/rules/worktree-per-story.md` | base column: `origin/main` in trunk mode; the "NEVER branch a story from `main`" hard stop gets the trunk exception |
| `.agents/commands/cicd-close-story-merge-tree.md` Step 3 | third arm: no epic → push the lane, `gh pr create --base main`, STOP; `--after-merge` finishes |
| `.agents/commands/cicd-create-epic-sprint.md` Step 1 | third answer: **trunk** — no branch cut; the kickoff records the mode on the board banner |
| `.agents/commands/cicd-dev-story-tests.md` Step 0.6 | item 1 (epic behind main) n/a in trunk; item 2 absorbs `origin/main` |
| `.agents/commands/cicd-push-e2e.md` | one paragraph: trunk mode has no epic to ship; the story door lands on `main` |
| `.agents/rules/constitution.md` + `AGENTS.md` (floor anchors) | the GIT hard-stop line names the trunk arm |
| `docs/_scc_sops_prds/workflows_testing_SOP.md` | §3 / §5 / §7 + changelog row (`sop_currency.py` gate) |
| `.agents/scripts/tests/test_jira_feed.py` and any door-parity test | keep green; `run_all.py` must pass |

### Acceptance (checkable)
- [ ] PR 2 merged; `git merge-base --is-ancestor epic/AVCH-100-epic-24-agent-quality origin/main` true; epic branch pruned local + remote
- [ ] Cloud Run revision serving 100% with `GIT_SHA` = merge sha; `/health` 200; `aviationchat.org` serves
- [ ] AviationChat: `grep -c "DO NOT MERGE THIS EPIC" sprint-status.yaml` = 0; banner names trunk mode; `main_write_gate.py --mode pr --branch claude/AVCH-999-x` passes the branch check; `run_all.py` green; C1 PR merged
- [ ] Lobby: `run_all.py` green; `sop_currency.py` green; `check_maps.py` clean; C2 PR merged
- [ ] AVCH-100 carries the ship comment; the plan's `## Your Actions` in each walkthrough is empty of decisions

## Your Actions (operator)
1. Merge PR 1 (sync into the epic), then PR 2 (epic into `main` = production deploy).
2. Reply `approved` to this plan (or name the tradeoff choice) — then C1 and C2 run and hand back two more PRs.
