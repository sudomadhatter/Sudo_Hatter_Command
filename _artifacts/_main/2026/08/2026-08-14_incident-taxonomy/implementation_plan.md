# Implementation plan — SCC-149: incident branch-prefix taxonomy (merge-target-guard's dead carve-out + the remaining claude/*-equals-story-work consumers)

**Ticket:** [SCC-149](https://sudo-command.atlassian.net/browse/SCC-149) · **Branch:** `chore/SCC-149-incident-taxonomy` (worktree `.claude/worktrees/incident-taxonomy`, cut from main @ `44a12c1`)
**Origin:** SCC-148's review (compound findings 2 and 5). One root cause: hand-maintained copies of
the branch-lane taxonomy disagreeing about what an incident branch looks like. The real shape is
**only** `claude/incident-<short-id-lower>` (`cicd-mobile-error-team.md:47` writes nothing else), and
it **matches the `claude/*` glob** — so every surface that says "any `claude/*` = story work" or
"`incident-*` is outside the model" is wrong in a way that fires during an incident.

## Ground truth measured before planning (2026-08-14, in this worktree)

1. **`merge-target-guard.sh`** — `classify()` (lines 146–154) has **no incident arm**;
   `claude/incident-x` matches `claude/*)` → `story` → `judge "main:story"` → `refuse` → the
   story-lane refusal ("a claude/* story lane merges into ITS epic/* branch") on an emergency local
   hotfix merge to main. The comment at lines 50–53 claims `incident-*` is "explicitly outside the
   branch model" — dead text; no code implements it, and the real prefix never reaches it.
2. **SOP row** — ticket says line 1304; it now sits at **`workflows_testing_SOP.md:1311`** (drifted
   when SCC-147's SOP edits landed). Same wording: "(`incident-*` is outside the branch model)".
3. **`test_git_hooks.py:489`** — **a surface the ticket missed**: case N's comment repeats the same
   false claim verbatim. The case itself is sound (its fixture is bare `incident-42`, which
   genuinely is unclassified); only the comment propagates the lie. Comment reword + the real shape
   gets its own case block.
4. **Cluster-2 consumers**, exact lines: `cicd-boot-sprint-memory.md:96–102` (a `claude/*` branch on
   origin → "point at `/cicd-resume`"), `cicd-merge-epic-workingtrees.md` Step 1 items 1–2
   (`git branch -a --list "*claude/*"` → every match is a lane to fix → merge → land → **prune**),
   `cicd-update-sprint-memory.md:237` (landing precondition "HEAD must be a **`claude/*`** branch").
5. **Acceptance-5 sweep baseline** (`grep -rnE '\`incident[-/]' .agents/commands .agents/rules
   .agents/scripts docs/` minus `claude/incident`): **3 defects** — guard:51, SOP:1311,
   test_git_hooks.py:489 — and 8 noise hits that are *not* branch-prefix claims (documented noise
   filter, pasted with the sweep): `incident:<short-id>` is a GitHub **issue label**
   (mobile-error-team:17), `incident-response.yml` is a **workflow filename** (mobile-error-team:234,
   mobile-mode:48), `incident-report.md` / `incident-triage.md` are **artifact filenames**
   (tea_deep_reference:613, sentry_error_response_team:176), test_task_preflight:306/343 are
   **historical comments about the old dead shape** (accurate as history), and git-policy:212 is the
   **protected sentence itself** (acceptance 6).
6. **Sibling lanes:** only `lens-budget` exists and SCC-147 is fully landed (`main..HEAD` empty,
   status clean) — no landing-order dependency.

## Design decision — what the guard does with an incident branch

`classify()` gains **`claude/incident-*) echo incident ;;` placed ABOVE `claude/*)`** — the
SCC-148 lesson applied to a `case` statement: first-match means **order is load-bearing**, and the
arm carries that comment. `judge()` gains **`incident:*|*:incident) echo unknown ;;` as its first
arm**: an incident lane is *positively classified* and then *deliberately unjudged* — it flows into
the existing declined-to-judge ALLOW path, which prints its note. The loop additionally records
`INCIDENT_SEEN` and the no-refusal branch appends one incident-specific line naming
`/cicd-mobile-error-team` as the owner, so the note is INCIDENT-correct, not just generic.
**Why allow-with-note and not a bespoke verdict row:** the guard's own charter (lines 55–59) — it
refuses only known-bad topologies, and a false red costs the gate. An emergency hotfix merge to
main during an incident is the *last* place to put a refusal. `destination()` is untouched —
incident never refuses, so it never needs a destination line.

## Steps — each acceptance item → the assertion that proves it

| # | Step | Assertion (RED first) |
|---|---|---|
| 1 | **RED**: new `INC` case block in `test_git_hooks.py` — real repo, real `core.hooksPath`, `lane(d, "claude/incident-abc123")`, `merge(d, "main", "claude/incident-abc123")`. Assert **(a)** `rc == 0 and moved` (ALLOWED); **(b)** `"MERGE REFUSED" not in out` and the story destination line `"story lane merges into ITS epic"` not in out; **(c)** positive: the output names the incident pipeline (`"/cicd-mobile-error-team" in out`) — a crash or silent skip cannot pass (b)+(c) together. **Both arms in one block:** **(d)** paired control in the same block — `claude/SCC-149-s` → main is still REFUSED (`rc != 0`, `"MERGE REFUSED" in out`) so the carve-out provably did not swallow the story arm (the TBL loop also covers this; the local pair makes the block self-contained). Run: RED on (a)(b)(c) — paste output, read which line raised | Acceptance 1 |
| 2 | **GREEN**: the guard — classify arm + judge arm + `INCIDENT_SEEN` note line; rewrite comment 50–53 to the real prefix and the real mechanism (positively classified, deliberately unjudged; bare unclassified names still get the generic note) | Acceptance 1, 2 |
| 3 | Same commit: SOP row **1311** — replace "(`incident-*` is outside the branch model)" with the real shape + "positively classified, deliberately unjudged" wording; `test_git_hooks.py:489` comment reworded (case N keeps its bare-name fixture — that is now the *only* thing it demonstrates) | Acceptance 4, 5 |
| 4 | **Commit 1** = guard + tests + SOP row (guard `.sh` is a usage surface; the SOP is staged WITH it, so `sop_currency` is satisfied without `[sop-ok]` — and acceptance 4's "same commit" is machine-checkable in `git show --stat`) | Acceptance 4 |
| 5 | Cluster 2, one sentence each, in each command's OWN step list (restate-alwayson-obligations): **boot:~100** — before "point at /cicd-resume", exclude `claude/incident-*` (the incident pipeline's; never a parked story step); **merge-epic Step 1.1** — the inventory excludes `claude/incident-*` rows (never fix/merge/land/prune them); **update-sprint:237** — precondition names the exclusion (`claude/*` but never `claude/incident-*`). RED for each: the sweep grep currently returns no carve-out in these three files (`grep -c 'claude/incident' <file>` = 0); GREEN = each carries exactly the carve-out sentence | Acceptance 3 |
| 6 | Regenerate mirrors: `pwsh .agents/scripts/sync-agents.ps1 -NoGlobals`; commit command files + mirrors (**Commit 2**). SOP treatment: check whether the SOP describes these three steps at carve-out granularity; if yes, one-line touch rides Commit 2; if no, `[sop-ok]` with the justification in the message (the SOP's incident/guard row was already corrected in Commit 1) | Acceptance 3 |
| 7 | Re-run acceptance-5 sweep repo-wide **including `.sh` and `docs/`** — paste verbatim; zero bare branch-prefix survivors outside the documented noise filter | Acceptance 5 |
| 8 | `sha256sum .agents/rules/git-policy.md` captured **now** (before any edit) and re-run at the end — byte-identical; also `git diff main...HEAD -- .agents/rules/git-policy.md` must be empty | Acceptance 6 |
| 9 | Mutation sweep (table below) → full suite bare (`run_all.py`, expect 23/23, case count exactly additive over 1907) → `workflow_lint --toolkit-only` → `check_maps --depth3-only --strict` → `/smh-code-review` → walkthrough + task.yaml + Dev Record | gate |

## Mutation table — declared BEFORE the sweep, every mutant drawn from the code

Restore **from copies** (SCC-147's trap: `git checkout --` restores from HEAD and reverts an
uncommitted fix — both times the tell was the closing green check going red), inside a trap;
`git status` after the sweep.

| # | Mutant (edit to `merge-target-guard.sh`) | The named case that must kill it |
|---|---|---|
| M1 | Move the `claude/incident-*)` arm BELOW `claude/*)` (the SCC-148 shadowing shape, in a `case` statement) | INC (a): incident → story → refused |
| M2 | Arm pattern `claude/incident-*` → `incident-*` (the old comment's fiction) | INC (a): real shape falls through to story |
| M3 | `judge` incident arm `unknown` → `refuse` | INC (a): rc != 0 |
| M4 | Arm pattern `claude/incident-*` → `claude/*` (the carve-out swallows the story arm) | INC (d) / TBL "story -> main is REFUSED": story becomes unjudged → allowed |
| M5 | Delete the incident-specific note line | INC (c): `/cicd-mobile-error-team` absent |

## What this lane does NOT do

- **Never touches `git-policy.md`** (acceptance 6 — the sentence is the record; sha-proven).
- No `judge()` verdict-table changes beyond the incident arm; no `destination()` change.
- No new WRONG_LANE / task_preflight work (SCC-148 shipped that; its tests stay untouched).
- No product paths, no deployable surfaces (eject tripwire clear by construction).
- The `test_task_preflight.py:306/343` historical comments stay — accurate history, not claims.

## Risks

- **sync-agents regenerating more than the three commands** — commit only this lane's files,
  explicit paths; diff the manifest before staging.
- **SOP line numbers drift again** if another lane lands mid-flight — re-grep before editing, never
  trust the cached number (already bit the ticket: 1304 → 1311).
- **`[sop-ok]` on Commit 2** is a judgment call — recorded either way in the commit message.

## Self-Audit (2026-08-14)

**Mode:** PRE-WORK · **Right-size: Full** (a live git gate + three command surfaces + the SOP).
Repo echo from command output: `Repo: incident-taxonomy | Branch: chore/SCC-149-incident-taxonomy`.
Plan: this file · Ticket: SCC-149.

- **Phase 0** — change set named above; all 6 acceptance items trace to steps 1–8 and every step
  traces back (the one addition beyond the ticket — `test_git_hooks.py:489`'s comment — traces to
  acceptance 5's "zero bare survivors INCLUDING .sh"). No deployable path in the set: the guard is
  repo tooling, `.github/` untouched — lane check clear.
- **Phase 1 (blast radius)** — walked with live greps, not belief: **(a)** `scripts/INDEX.md:48`
  carries the guard's row; it stays *true* after the change (bare unclassified names still get the
  declined note) but goes *incomplete* — F1 below. **(b)** The three command files' mirrors
  (`.opencode/commands/`, `.agents/workflows/`, launcher skills) regenerate via sync-agents — step 6.
  `commands/INDEX.md` rows unaffected (frontmatter descriptions unchanged). **(c)** The guard's only
  callers are `.githooks/commit-msg` (dispatcher, unchanged) and `test_git_hooks.py` (updated here).
  **(d)** `test_hooks_armed.py` pins `MERGE-TARGET-ENFORCE` arming — untouched by this diff.
  **(e)** Sibling lanes: only `lens-budget`, fully landed, clean — measured, no dependency.
- **Phase 2 (over-engineering)** — one tripwire examined: INC (d) duplicates the TBL
  "story -> main" refusal cell. Kept deliberately and stated: the gate doctrine ("both halves,
  always") wants the arm-pair readable in one block, and the cost is one extra merge in an existing
  fixture. No new files, no new flags, no generalization — the judge arm is one line, the note one
  variable. A **gate that cannot fail** check: INC (b)'s two negatives ride with (c)'s positive
  pipeline-name assertion, so a crashed run cannot pass — the SCC-148 review's own finding class,
  pre-applied.
- **Phase 3 (pre-mortem)** — Other machine: `pwsh` exists on both, `python3` is Mac-correct here,
  PC nuance noted in walkthrough. Fresh clone: no new arming surface (flag already tracked); the
  change makes the gate *allow more*, so the silent failure mode is the swallow — M4 exists for
  exactly that. Gate fires on someone else's commit: the incident note names its owner command.
  Escape hatch: `--no-verify`, unchanged, auditable. Empty input: the sweep's zero-match grep exits
  1 — run it bare, interpret out loud, never pipe it into a gate. Four caches: step 6 + workflow_lint.
  Rollback: two revertable commits; nothing irreversible (no deletes, no transitions in-lane).

| Finding | file:line | Severity | Disposition |
|---|---|---|---|
| F1 — INDEX row goes incomplete: after the change, `claude/incident-*` is *positively classified then deliberately unjudged*, which the row's "unclassified branches … allowed" no longer describes | `.agents/scripts/INDEX.md:48` | minor | one clause added to the row in Commit 1 (it names the guard's behavior; leaving it is the SCC-149 defect class in the file that indexes the fix) |
| F2 — the backticked sweep alone would miss unbackticked prose claims | sweep pattern | minor | step 7 runs BOTH patterns (`` `incident[-/] `` and `incident-\*`); probe today shows the wider net catches the same 3 defects, no more |
| F3 — SOP row moved 1304→1311 since the ticket was written | `workflows_testing_SOP.md` | note | plan already re-greps before editing; never trust the cached line number |

Four quick gates: **verification strategy** — every acceptance item names its command and output
(steps table). **Irreversible** — none in-lane. **Vague steps** — the note wording is the one
free variable; the assertion pins `/cicd-mobile-error-team` so the builder cannot drift it silently.
**Convention fit** — comment style matches the guard's existing ⛔/⭐ idiom; carve-out sentences
follow SCC-148's exact pattern in the two files it already fixed.

Audit verdict: GO

