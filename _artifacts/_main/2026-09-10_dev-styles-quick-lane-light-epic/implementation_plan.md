---
IsArtifact: true
ArtifactMetadata:
  title: SCC-441 - two development styles, two toggles (the quick lane and the light epic)
  type: implementation_plan
  date: 2026-09-10
---

# SCC-441 - two development styles, two independent toggles

**Ticket:** SCC-441 (Task, parent of SCC-442..446; blocks AVCH-152) · **Branch:** `chore/SCC-441-dev-styles-quick-lane-light-epic`
**Repo:** `Sudo_Hatter_Command` (the lobby) · **Date:** 2026-09-10 · **review-runtime:** fan-out (one lane, five parts, riders `SCC-442..446`)

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

## One lane, five parts, in build order

Consolidated on the operator's ruling (2026-09-10: "consolidate them instead of parallel"). The
labeller had measured five solo waves, so per-subtask lanes bought three extra close-outs and no
parallelism. One worktree, one branch keyed by the parent, one plan approval, one gate, one
close-out; each part's commits lead with its own subtask key so every child's dev panel shows its
work and a part reverts as a unit (`work-consolidation` rule 2).

| Part | Key | What it builds | Its detailed plan and audit |
|---|---|---|---|
| A | SCC-442 | Rules: FULL / LIGHT / TRUNK, the quick lane, the rails | [parts/SCC-442.md](parts/SCC-442.md) |
| B | SCC-443 | Scope check: critical-surfaces.md, scope_check.py | [parts/SCC-443.md](parts/SCC-443.md) |
| C | SCC-444 | /cicd-quick-dev rebuilt | [parts/SCC-444.md](parts/SCC-444.md) |
| D | SCC-445 | Lobby lanes renamed | [parts/SCC-445.md](parts/SCC-445.md) |
| E | SCC-446 | Epic doors: epic_mode.py, kickoff, Step 0 lines, two arms | [parts/SCC-446.md](parts/SCC-446.md) |
| F | SCC-441 | The close-out docs: TEA guide § 6.0, SOP § 6, the new-project follow-up line | this file, § Part F |

The order is the build order and the dependency order: the law (A) before the script (B) before
the three door parts (C, D, E). Each part file carries its own acceptance table, edits, port
section and self-audit; this file carries the combined change set the review's drift check reads.

AVCH-152 stays its own lane in AviationChat and lands after this lane; Part F lands after
AVCH-152, in a closure lane cut under this same branch name off `origin/main`.

## How the lane runs

- **Build:** Parts A → E inside this one tree, each as the full Task cycle (today's
  `/smh-quick-dev`, which Part D renames `/smh-dev-task-tests`): the assertion seen RED, then
  GREEN, each part's commits keyed `SCC-44N …`. The SOP moves with each part's commit
  (`sop-currency`). No CI runs on a lobby lane; the gate is the local suite and the
  `main-write-gate` check on the PR.
- **Gate:** once, at the tip, through the receipt writer; `run_all.py`, `workflow_lint.py
  --toolkit-only`, `check_maps.py --depth3-only --strict`, `check_links.py`.
- **Review:** one `/smh-code-review` on the whole diff; its drift check reconciles against the
  combined block below.
- **Landing:** `landing_mode: partial` with `riders: [SCC-442, SCC-443, SCC-444, SCC-445,
  SCC-446]` in `task.yaml`. The five riders flip at close-out; **the parent stays open** for
  AVCH-152 and Part F.
- **Part F (the closure lane):** after AVCH-152 lands, a lane under this same branch name off
  `origin/main` writes the three lobby docs edits that describe the finished state (TEA guide
  § 6.0 LIGHT row and the two epic rulesets, SOP § 6, one follow-up line in
  `smh-new-project.md`), the parent's walkthrough, and closes SCC-441.

## Acceptance

| # | Statement | Check |
|---|---|---|
| A | Part A's acceptance table (six rows) is green | [parts/SCC-442.md](parts/SCC-442.md) § Acceptance |
| B | Part B's acceptance table (six rows) is green | [parts/SCC-443.md](parts/SCC-443.md) § Acceptance |
| C | Part C's acceptance table (eight rows) is green | [parts/SCC-444.md](parts/SCC-444.md) § Acceptance |
| D | Part D's acceptance table (six rows) is green | [parts/SCC-445.md](parts/SCC-445.md) § Acceptance |
| E | Part E's acceptance table (seven rows) is green | [parts/SCC-446.md](parts/SCC-446.md) § Acceptance |
| G | Every commit on the lane leads with the key of the part it builds; `task_preflight.py` finds each rider named in a commit subject | `git log --format=%s origin/main..HEAD` |
| H | One gate at the tip green; one review; the five riders flip and the parent stays open | the close-out door's report |
| F | The closure lane: the three docs edits, the walkthrough, the parent Done after AVCH-152 | the closure lane's walkthrough |

## Not in this lane

The skeleton port (`Projects/sudo-project-skeleton`) is AVCH-152's last Plan row and is committed
in that repo under the SCC-441 key, which is the only key its hook accepts. SCC-438 (three lobby
commands wait on `main-write-gate` alone) stays where it is.

## Declared Change Set

The union of the five parts' declared sets (11 NEW, 105 EDIT, 4 DELETE, one bullet per
path, the parts that touch it named), plus this lane's own record. Generated from the part files
by the same parser the drift check uses; a bullet's row is the part whose acceptance table it
serves.

- NEW `.agents/commands/smh-dev-task-tests.md` - part D → Part D
- NEW `.agents/critical-surfaces.json` - part B → Part B
- NEW `.agents/rules/critical-surfaces.md` - part B → Part B
- NEW `.agents/scripts/epic_mode.py` - part E → Part E
- NEW `.agents/scripts/scope_check.py` - part B → Part B
- NEW `.agents/scripts/tests/test_epic_mode.py` - part E → Part E
- NEW `.agents/scripts/tests/test_scope_check.py` - part B → Part B
- NEW `.agents/skills/smh-dev-task-tests/SKILL.md` - part D → Part D
- NEW `.claude/skills/smh-dev-task-tests/SKILL.md` - part D → Part D
- NEW `.opencode/commands/smh-dev-task-tests.md` - part D → Part D
- NEW `.roo/commands/smh-dev-task-tests.md` - part D → Part D
- DELETE `.agents/commands/smh-quick-fix.md` - part D → Part D
- DELETE `.agents/skills/smh-quick-fix/SKILL.md` - part D → Part D
- DELETE `.claude/skills/smh-quick-fix/SKILL.md` - part D → Part D
- DELETE `.opencode/commands/smh-quick-fix.md` - part D → Part D
- EDIT `.agents/.sync-manifest.json` - part D → Part D
- EDIT `.agents/commands/INDEX.md` - part C, D, E → Part C
- EDIT `.agents/commands/cicd-autopilot-claude.md` - part C → Part C
- EDIT `.agents/commands/cicd-boot-sprint-memory.md` - part E → Part E
- EDIT `.agents/commands/cicd-clean-code-audit.md` - part E → Part E
- EDIT `.agents/commands/cicd-close-story-merge-tree.md` - part E → Part E
- EDIT `.agents/commands/cicd-code-review.md` - part E → Part E
- EDIT `.agents/commands/cicd-create-epic-sprint.md` - part E → Part E
- EDIT `.agents/commands/cicd-dev-story-tests.md` - part D, E → Part D
- EDIT `.agents/commands/cicd-e2e.md` - part E → Part E
- EDIT `.agents/commands/cicd-merge-epic-workingtrees.md` - part E → Part E
- EDIT `.agents/commands/cicd-prune-worktree.md` - part E → Part E
- EDIT `.agents/commands/cicd-push-e2e.md` - part E → Part E
- EDIT `.agents/commands/cicd-quick-dev.md` - part C, D, E → Part C
- EDIT `.agents/commands/cicd-resume.md` - part E → Part E
- EDIT `.agents/commands/cicd-write-story-tests.md` - part E → Part E
- EDIT `.agents/commands/smh-close-task-merge-tree.md` - part D → Part D
- EDIT `.agents/commands/smh-code-review.md` - part D → Part D
- EDIT `.agents/commands/smh-designer.md` - part D → Part D
- EDIT `.agents/commands/smh-label-tasks.md` - part D → Part D
- EDIT `.agents/commands/smh-llm-approvals.md` - part D → Part D
- EDIT `.agents/commands/smh-merge-multiple-workingtrees.md` - part D → Part D
- EDIT `.agents/commands/smh-non-crit-pr-push.md` - part D → Part D
- EDIT `.agents/commands/smh-plan-task.md` - part D → Part D
- EDIT `.agents/commands/smh-quick-dev.md` - part D → Part D
- EDIT `.agents/commands/smh-self-audit.md` - part D → Part D
- EDIT `.agents/commands/smh-team-cheshire-cat.md` - part D → Part D
- EDIT `.agents/commands/smh-team-queen-of-hearts.md` - part D → Part D
- EDIT `.agents/rules/000-PLAN-FIRST-GATE.md` - part D → Part D
- EDIT `.agents/rules/INDEX.md` - part A, B → Part A
- EDIT `.agents/rules/artifacts-always-first.md` - part D → Part D
- EDIT `.agents/rules/constitution.md` - part A → Part A
- EDIT `.agents/rules/git-policy.md` - part A → Part A
- EDIT `.agents/rules/jira.md` - part D → Part D
- EDIT `.agents/rules/living-template-sync.md` - part A → Part A
- EDIT `.agents/rules/work-consolidation.md` - part D → Part D
- EDIT `.agents/rules/worktree-per-story.md` - part A → Part A
- EDIT `.agents/rules/zoo-team.md` - part C, D → Part C
- EDIT `.agents/scripts/INDEX.md` - part B, D, E → Part B
- EDIT `.agents/scripts/closeout_preflight.py` - part C → Part C
- EDIT `.agents/scripts/git-hooks/post-commit-jira-start.sh` - part D → Part D
- EDIT `.agents/scripts/jira_feed.py` - part D → Part D
- EDIT `.agents/scripts/lane_qualify.py` - part D → Part D
- EDIT `.agents/scripts/main_write_gate.py` - part D → Part D
- EDIT `.agents/scripts/mutation_sweep.py` - part D → Part D
- EDIT `.agents/scripts/task_preflight.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_boot_epic_branch_read.py` - part E → Part E
- EDIT `.agents/scripts/tests/test_closeout_preflight.py` - part C, D → Part C
- EDIT `.agents/scripts/tests/test_command_surfaces.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_declared_change_set.py` - part C, D → Part C
- EDIT `.agents/scripts/tests/test_directive_quote.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_doc_examples_parse.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_jira_feed.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_jira_start_hook.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_lane_qualify.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_main_write_gate_ci.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_maps_hooks.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_mutation_sweep.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_refresh_maps.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_repo_template.py` - part D → Part D
- EDIT `.agents/scripts/tests/test_review_engine.py` - part C, D → Part C
- EDIT `.agents/scripts/tests/test_trunk_mode.py` - part A, E → Part A
- EDIT `.agents/scripts/tests/test_twin_parity.py` - part D, E → Part D
- EDIT `.agents/skills/cicd-close-story-merge-tree/SKILL.md` - part E → Part E
- EDIT `.agents/skills/cicd-create-epic-sprint/SKILL.md` - part E → Part E
- EDIT `.agents/skills/cicd-quick-dev/SKILL.md` - part C → Part C
- EDIT `.agents/skills/smh-quick-dev/SKILL.md` - part D → Part D
- EDIT `.claude/skills/cicd-close-story-merge-tree/SKILL.md` - part E → Part E
- EDIT `.claude/skills/cicd-create-epic-sprint/SKILL.md` - part E → Part E
- EDIT `.claude/skills/cicd-quick-dev/SKILL.md` - part C → Part C
- EDIT `.claude/skills/smh-quick-dev/SKILL.md` - part D → Part D
- EDIT `.opencode/commands/cicd-boot-sprint-memory.md` - part E → Part E
- EDIT `.opencode/commands/cicd-clean-code-audit.md` - part E → Part E
- EDIT `.opencode/commands/cicd-close-story-merge-tree.md` - part E → Part E
- EDIT `.opencode/commands/cicd-code-review.md` - part E → Part E
- EDIT `.opencode/commands/cicd-create-epic-sprint.md` - part E → Part E
- EDIT `.opencode/commands/cicd-dev-story-tests.md` - part D, E → Part D
- EDIT `.opencode/commands/cicd-e2e.md` - part E → Part E
- EDIT `.opencode/commands/cicd-merge-epic-workingtrees.md` - part E → Part E
- EDIT `.opencode/commands/cicd-prune-worktree.md` - part E → Part E
- EDIT `.opencode/commands/cicd-push-e2e.md` - part E → Part E
- EDIT `.opencode/commands/cicd-quick-dev.md` - part C, D, E → Part C
- EDIT `.opencode/commands/cicd-resume.md` - part E → Part E
- EDIT `.opencode/commands/cicd-write-story-tests.md` - part E → Part E
- EDIT `.opencode/commands/smh-close-task-merge-tree.md` - part D → Part D
- EDIT `.opencode/commands/smh-code-review.md` - part D → Part D
- EDIT `.opencode/commands/smh-designer.md` - part D → Part D
- EDIT `.opencode/commands/smh-label-tasks.md` - part D → Part D
- EDIT `.opencode/commands/smh-llm-approvals.md` - part D → Part D
- EDIT `.opencode/commands/smh-merge-multiple-workingtrees.md` - part D → Part D
- EDIT `.opencode/commands/smh-non-crit-pr-push.md` - part D → Part D
- EDIT `.opencode/commands/smh-plan-task.md` - part D → Part D
- EDIT `.opencode/commands/smh-quick-dev.md` - part D → Part D
- EDIT `.opencode/commands/smh-self-audit.md` - part D → Part D
- EDIT `.roo/commands/cicd-quick-dev.md` - part C → Part C
- EDIT `.roo/commands/smh-quick-dev.md` - part D → Part D
- EDIT `.roo/rules/constitution.md` - part A → Part A
- EDIT `.roo/rules/zoo-team.md` - part D → Part D
- EDIT `AGENTS.md` - part A, C, D → Part A
- EDIT `_bmad/custom/bmad-quick-dev.toml` - part C → Part C
- EDIT `docs/_scc_sops_prds/autopilot_SOP.md` - part C → Part C
- EDIT `docs/_scc_sops_prds/frontend_UI_design_guide.md` - part D → Part D
- EDIT `docs/_scc_sops_prds/operator_workflows_quickref.md` - part C, D → Part C
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` - part A, B, C, D, E → Part A
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` - part A, B, C, D, E → Part A
- EDIT `docs/doc-graph.json` - HOOK-GENERATED, never hand-merged, regenerated by the refresh-maps hook on the docs edits above → Part A
- EDIT `docs/doc-graph.md` - HOOK-GENERATED, never hand-merged, regenerated by the refresh-maps hook on the docs edits above → Part A
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/implementation_plan.md` - this plan → Part A
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/task.yaml` - the manifest with the five riders → Part A
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/parts/SCC-442.md` - Part A's plan → Part A
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/parts/SCC-443.md` - Part B's plan → Part B
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/parts/SCC-444.md` - Part C's plan → Part C
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/parts/SCC-445.md` - Part D's plan → Part D
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/parts/SCC-446.md` - Part E's plan → Part E
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-441.md` - the parent's outline → Part A
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-442.md` - outline → Part A
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-443.md` - outline → Part B
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-444.md` - outline → Part C
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-445.md` - outline → Part D
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/SCC-446.md` - outline → Part E
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/tickets/AVCH-152.md` - outline → Part A
- NEW `_artifacts/_main/2026-09-10_dev-styles-quick-lane-light-epic/walkthrough.md` - the closing record, one for the lane → H
- EDIT `_artifacts/_main/INDEX.md` - the depth-3 row → H
- EDIT `docs/_scc_sops_prds/tea_testing_guide.md` - Part F, the closure lane → F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP.md` - Part F, the closure lane (the parts above edit other sections of the same file) → F
- EDIT `docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` - Part F, the closure lane → F
- EDIT `.agents/commands/smh-new-project.md` - Part F, the closure lane → F

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

**Amended 2026-09-10, same day:** four close-out edits added to the change set (the TEA guide § 6.0,
the SOP § 6 and its changelog row, one follow-up line in `smh-new-project.md`). They are written
only after every child and AVCH-152 have landed, so the level at close-out is LEDGER+BLAST (a
command file and the SOP, same commit per `sop-currency`); Lens 2 re-runs then against the landed
`main`. The verdict stands: every added path exists on disk today, none is deployable, and each
maps to row E.

**Consolidated 2026-09-10 (operator).** The five part audits stand as written in `parts/`; each
was LEDGER+BLAST with verdict GO. Inside one lane their sibling landing-order findings (the
law/door window until the doors land, the shared SOP, the twin line in the rebuilt door) are
moot: every part lands in one PR. The five side worktrees and branches were retired after their
plans were copied here; `git worktree list` shows this tree and the lobby only. The batch clause of
`000-PLAN-FIRST-GATE` applies: one recorded approval covers this plan and its five part files.

Audit verdict: GO

**Batch approval (2026-09-10):** "Approved. Let’s start on the first task" — covers the plans listed in `/smh-plan-task SCC-441` Step 5: SCC-442, SCC-443, SCC-444, SCC-445, SCC-446 (this consolidated plan and its five part files) — recorded at 9bb61f00
