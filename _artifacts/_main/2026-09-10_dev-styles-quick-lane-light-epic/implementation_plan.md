---
IsArtifact: true
ArtifactMetadata:
  title: SCC-441 - two development styles, two toggles (the quick lane and the light epic)
  type: implementation_plan
  date: 2026-09-10
---

# SCC-441 - two development styles, two independent toggles

**Ticket:** SCC-441 (Task, parent of SCC-442..446; blocks AVCH-152) · **Branch:** `chore/SCC-441-dev-styles-quick-lane-light-epic`
**Repo:** `Sudo_Hatter_Command` (the lobby) · **Date:** 2026-09-10 · **review-runtime:** none (design record and lane map; the code moves in the child lanes)

## Bottom line

Two development styles exist and the toolkit only shapes one of them. A project not yet in
production, and a project taking small features straight to `main`, both pay the full ceremony
today: red tests, self-audit, a review verdict with a roster gate, receipts, and a four-check CI
run with about sixteen minutes of Playwright on every frontend landing. Measured on AVCH-149
(2026-09-10): the ceremony, not the tests, cost half the day.

The agreed answer (operator, 2026-09-10) is **two toggles that never depend on each other**:

| Toggle | What it selects | Where it is read |
|---|---|---|
| **The lane you call** | `quick-dev` (TDD kept, ceremony cut) or the full story lane | the command name |
| **The epic you are on** | `FULL` (four checks per landing) / `LIGHT` (two fast checks, E2E once) / `TRUNK` (no epic) | the epic branch name, by git query, never prose |

Everything else stays exactly as it is. In particular: **TDD stays in every lane.** Nothing here
turns off tests. The light epic defers the two long E2E jobs to the end of the epic; the quick
lane drops the self-audit and the review verdict unless the operator asks for them.

## Toggle 1 - the quick lane, defined once for both levels

Same five steps in the lobby (`/smh-quick-dev`) and in a project (`/cicd-quick-dev`):

| Step | What happens | Who moves it |
|---|---|---|
| 1. Scope check | `scope_check.py` on the planned file set against the critical-surfaces list (auth, billing, security rules, FAA-facing answers, CI). Overlap = the agent **stops**, states what overlaps and why it matters. | Only the operator's word overrides. No agent override exists. |
| 2. Plan | `implementation_plan.md`, then the literal `approved`. `/smh-self-audit` or `/cicd-self-audit` runs **only if asked**. | operator |
| 3. RED then GREEN | the same TDD as the full lane: the assertion seen red, then made green | agent |
| 4. Walkthrough | `walkthrough.md`, then the literal `approved`. `/smh-code-review` or `/cicd-code-review` runs **only if asked**. No `Verdict:` stamp unless a review actually ran (the stamp pulls in the roster gate). | operator |
| 5. Close | the normal close-out door. The eject tripwire re-runs the scope check on the **real diff**; an overlap the operator has not overridden ejects to the full lane. | agent |

What the quick lane is for: a UI fix, a document or file update, anything non-critical. What it is
not for: the surfaces on the list. The line is a file, not a feeling.

## Toggle 2 - the epic mode, read from the branch name

| Mode | Branch | Landing a story | Checks per landing | E2E |
|---|---|---|---|---|
| **FULL** | `epic/<KEY>-<N>-<slug>` | PR into the epic | Backend (Python), Frontend (Node.js), Backend E2E, Frontend E2E | every landing |
| **LIGHT** | `epic/<KEY>-light-epic-<N>-<slug>` | PR into the epic | Backend (Python), Frontend (Node.js) | once at `/cicd-push-e2e`, or on demand via `/cicd-e2e` |
| **TRUNK** | no `origin/epic/*` | PR into `main`, operator merges | the four checks on `main`'s ruleset | at the PR |

The `-quickdev` direct-push mode is **retired**. It was never cut, nothing in code reads its
suffix, and the epic ruleset would refuse the push it describes. A landing is always a PR into the
epic; the direct-push arm in `/cicd-close-story-merge-tree` Step 3 is deleted.

**Why the mode is the third token and not a prefix.** The `epic/` prefix is load-bearing: 26 globs
across scripts and hooks, the GitHub ruleset on `refs/heads/epic/**`, the workflow trigger on
`epic/**`, and `task_preflight.py`'s `EPIC_REF_RE`, which requires the Jira key immediately after
the prefix. `epic-light/` would have had to move all of it. `-light-epic-` after the key moves
nothing and is a single `contains()` in CI and a single glob in the ruleset. Agreed 2026-09-10.

**The mode is chosen once, at kickoff, by the operator.** `/cicd-create-epic-sprint` asks FULL or
LIGHT and cuts the name. No door ever prompts to cut a light epic mid-flight; `/cicd-quick-dev`
never suggests it. Every `cicd-` door prints the mode line first, from the git query, so an agent
always knows which epic it is on from command output and never from belief.

## The rails that never toggle

| Rail | Holds in every lane and every mode |
|---|---|
| Worktree per lane | every commit-producing lane has its own tree |
| Key on the branch | `chore/<KEY>-<slug>` or `claude/<KEY>-<slug>`; the hook refuses the rest |
| Explicit paths | never `git add -A` / `.` / `-u` |
| `main` is the operator's | reached only by a PR the operator merges |
| Plan then `approved` | in the quick lane too |
| The walkthrough | never skipped |

## The lanes

Per-subtask mode (one worktree and one branch per child), chosen because the operator wants
`/smh-label-tasks` to show what can actually run side by side, and because the children touch
distinct surfaces (law, a new script, one project door, the lobby doors, the epic doors). AVCH-152
is a separate repo and lands last.

| Order | Key | Branch | Plan | Lands |
|---|---|---|---|---|
| 1 | SCC-442 Rules | `chore/SCC-442-dev-style-rules` | `_artifacts/_main/2026-09-10_scc-442-dev-style-rules/implementation_plan.md` | first, alone: every door cites the law |
| 2 | SCC-443 Scope check | `chore/SCC-443-scope-check` | `_artifacts/_main/2026-09-10_scc-443-scope-check/implementation_plan.md` | second: both quick lanes call the script |
| 3 | SCC-444 `/cicd-quick-dev` | `chore/SCC-444-cicd-quick-dev` | `_artifacts/_main/2026-09-10_scc-444-cicd-quick-dev/implementation_plan.md` | after 442 and 443 |
| 3 | SCC-445 Lobby lanes | `chore/SCC-445-smh-lane-rename` | `_artifacts/_main/2026-09-10_scc-445-smh-lane-rename/implementation_plan.md` | after 442 and 443 |
| 3 | SCC-446 Epic doors | `chore/SCC-446-epic-mode-doors` | `_artifacts/_main/2026-09-10_scc-446-epic-mode-doors/implementation_plan.md` | after 442 |
| 4 | AVCH-152 Light epic CI + skeleton | `chore/AVCH-152-light-epic-ci` (AviationChat) | `Projects/AGY_AVIATIONCHAT/_artifacts/_main/2026-09-10_avch-152-light-epic-ci/implementation_plan.md` | last; the skeleton row is keyed SCC-441 in that repo |
| 5 | SCC-441 this lane | `chore/SCC-441-dev-styles-quick-lane-light-epic` | this file | parent closes LAST, with the walkthrough |

The order in the table is the declared dependency. The measured schedule is `/smh-label-tasks
SCC-441`'s output, which is run after every child plan is committed and pushed, and re-run after
each wave lands.

## What this lane itself changes

Nothing outside this folder. It is the design record every child cites, the seven ticket outlines
that were rendered onto the board, and at the end the parent's walkthrough. Every rule, door,
script, workflow and ruleset moves in its own child lane behind its own `approved`.

## Acceptance

| # | Statement | Check |
|---|---|---|
| A | The design record states both toggles, the five-step quick lane, the three epic modes, the name and its signature token, and the rails | this file, read |
| B | The seven outlines the board carries are in the tree beside the plan | `ls tickets/` shows SCC-441..446 and AVCH-152 |
| C | The parent's `task.yaml` grounds this lane for the close-out door | `task_key: SCC-441`, no riders |
| D | Each child ticket's Files row points at its own plan on its own branch | `acli jira workitem view <KEY>` shows the branch link |
| E | The parent closes last, after every child and AVCH-152 are Done | the close-out door's rider check |

## Not in this lane

The skeleton port (`Projects/sudo-project-skeleton`) is AVCH-152's last Plan row and is committed
in that repo under the SCC-441 key, which is the only key its hook accepts. SCC-438 (three lobby
commands wait on `main-write-gate` alone) stays where it is.

## Declared Change Set

- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/implementation_plan.md` - this design record → A
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/task.yaml` - the manifest → C
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-441.md` - the parent's outline → B
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-442.md` - outline → B
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-443.md` - outline → B
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-444.md` - outline → B
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-445.md` - outline → B
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-446.md` - outline → B
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/AVCH-152.md` - outline → B
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/walkthrough.md` - the closing record, written at close-out → E
- EDIT `_artifacts/_main/INDEX.md` - the depth-3 row → E

## Self-Audit (2026-09-10)

**Level:** LEDGER (every declared path is an artifact; no rule, gate, hook, script, door or deployable path). **Mode:** PRE-WORK.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every declared path exists or is a close-out artefact; the block parses; no deployable path; Scope Ledger NEW x acceptance
read:        _artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/ (ls: implementation_plan.md, task.yaml, tickets/ with 7 outlines)
             python3 .agents/scripts/declared_change_set.py parse <this plan>  -> present: true, 11 entries, 0 incomplete
             .agents/scripts/task_preflight.py:123 EPIC_REF_RE (the key-after-prefix constraint the naming section cites)
verdict:     clean
```

Scope Ledger: ten `NEW` artefacts, each mapped to a row (A, B, C, E); `walkthrough.md` is the
close-out record row E requires. No artefact lacks an acceptance row. Lane fit: every path is under
`_artifacts/`, so this lane ships through `/smh-close-task-merge-tree`; nothing deployable.

### Observations

- The `blob/main` links the outlines carry will not resolve until this lane lands; the ticket
  Files rows are re-pointed at the branch link in Step 3.5 of the plan-task door.

Audit verdict: GO
