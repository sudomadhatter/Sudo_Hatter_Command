# Walkthrough — SCC-149: incident branch-prefix taxonomy (guard carve-out + consumer step lists)

**Ticket:** [SCC-149](https://sudo-command.atlassian.net/browse/SCC-149) · **Branch:** `chore/SCC-149-incident-taxonomy` · **Plan:** `implementation_plan.md` (Self-Audit GO, operator `approved`)

## Task Checklist

- [x] Step 0/0.5 — worktree off main @ `44a12c1` (SCC-147's tip), assets linked, ticket → In Progress, sibling check (lens-budget fully landed, no dependency)
- [x] Step 1/1.5 — 6 acceptance items grounded in real lines; plan + self-audit GO; literal `approved`
  - finding while grounding: the SOP row drifted 1304 → 1311 after SCC-147; never trust a ticket's cached line number
  - finding while grounding: `test_git_hooks.py:489` (case N's comment) repeated the false taxonomy claim — a surface the ticket missed
- [x] Step 2 — RED: INC block, 3 assertions failing at their own checks (91/94)
- [x] Step 3 — GREEN: guard carve-out, 94/94; Commit 1 `f7f6961` (guard + tests + SOP row + INDEX clause, SOP staged with the guard — no `[sop-ok]`)
- [x] Step 3 — Cluster 2: three consumer carve-outs + mirrors; Commit 2 `fe225dc` (`[sop-ok]`, justification in message)
  - finding at the sweep: my own Commit-1 comment quoted the old false literal, re-tripping the acceptance-5 grep — reworded (the comment-literals-invert-source-grep-tests class, caught by running the sweep against HEAD instead of trusting the edit)
- [x] Step 3 — mutation sweep: 6 mutants (5 declared + 1 re-aim), 6 killed; restore from copies byte-identical; closing green run
  - finding in the sweep itself: M5's kill was a SYNTAX ERROR (empty `if` body), not a caught silent absence — every case crashed and the verdict line still said "killed by its named case". Re-aimed as M5b (note → `:`, script valid): killed by the note assertion ALONE. The red-dies-before-its-assertion class, inside the sweep built to catch it.
- [x] Full gate at `ec13bc7`, every command bare: run_all **23/23 files, 1911/1911 cases, exit 0** (exactly additive: 1907 main + 4 INC, predicted before measured) · workflow_lint --toolkit-only exit 0 · check_maps --depth3-only --strict exit 0
  - mid-lane hazard, caught before damage: one commit command ran in the SHARED CHECKOUT on main — the shell's cwd silently reverted between tool calls (the SCC-97 signature this very lane's gate exists for). The add was a no-op there and the commit refused empty; redone with `-C` pinned to the worktree, which every git call carries since
- [ ] Step 4 — /smh-code-review

## Evidence

### Acceptance 1 — the guard positively classifies `claude/incident-*`, both arms proven on real git

The INC block in `test_git_hooks.py` drives real `git merge` through a real `core.hooksPath`
(the harness's charter: a source-grep cannot see whether git ever invoked the hook).

**RED — before the fix (guard at `44a12c1`'s state), the assertions fail where they assert:**

```
[FAIL] INC · a claude/incident-* hotfix merge into main is ALLOWED: edy:  git merge --abort   then re-check where you are standing:
[FAIL] INC · ...and it is never the story-lane refusal: edy:  git merge --abort   then re-check where you are standing:
[FAIL] INC · ...and the note names the pipeline that owns the lane: edy:  git merge --abort   then re-check where you are standing:
[PASS] INC · the ordinary story arm still refuses (the carve-out swallowed nothing): ...
-- 91/94 passed --
```

Which line raised: each `[FAIL]` is the case's own `c.check` — the captured evidence is the guard's
*refusal remedy text* (`git merge --abort …`), i.e. the story-lane refusal firing on the incident
merge, exactly the ticket's claim. Not a setup death. The fourth case passes green-first and is
declared as characterization: the story arm's refusal predates this lane (SCC-144's TBL loop).

**GREEN — after the fix, run bare (exit code read directly, no pipe):**

```
exit=0
[PASS] INC · a claude/incident-* hotfix merge into main is ALLOWED: SCC-149)
[PASS] INC · ...and it is never the story-lane refusal: SCC-149)
[PASS] INC · ...and the note names the pipeline that owns the lane: SCC-149)
[PASS] INC · the ordinary story arm still refuses (the carve-out swallowed nothing): ...
-- 94/94 passed --
```

The PASS evidence tail `SCC-149)` is the guard's new note actually printing in the captured merge
output — the allowed merge says who owns the lane.

### Acceptance 2 — the comment matches the code that now exists

`merge-target-guard.sh` lines 50–58 now describe the real shape (`claude/incident-<short-id-lower>`),
the real mechanism (carve-out ABOVE the story arm, first-match order called out as load-bearing at
the arm itself), and the real verdict (positively classified, deliberately unjudged). The old text
("`incident-*` is explicitly outside the branch model") described an arm that never existed.

### Acceptance 3 — each consumer carries the carve-out in its OWN step list

Commit `fe225dc`, one sentence each, at the exact step where the scan happens:

- `cicd-boot-sprint-memory.md` (the check-the-remote bullet): a `claude/incident-*` branch on origin
  is never "the step was already done on another machine" — report as incident, route nowhere.
- `cicd-merge-epic-workingtrees.md` Step 1.1 (the inventory): `claude/incident-*` matches are
  EXCLUDED — never fix, merge, land or PRUNE one there (the escalating arm).
- `cicd-update-sprint-memory.md` (the landing precondition): `claude/*` **and never
  `claude/incident-*`** — the branch satisfies the glob and must not satisfy the gate.

Mirrors regenerated by `sync-agents` (never hand-edited): `.opencode/commands/` ×3,
`.agents/workflows/` ×2 (update-sprint-memory carries no antigravity workflow), manifest updated.

### Acceptance 4 — SOP row corrected in the SAME commit as the guard

`git show --stat f7f6961` shows the four files landing together — the guard, its test file, the SOP
(`workflows_testing_SOP.md` row at line 1311), and `scripts/INDEX.md`. `sop_currency` was satisfied
by staging the SOP with the usage surface, not by `[sop-ok]`.

### Acceptance 5 — repo-wide sweep, both patterns, including `.sh` and `docs/`

Run against the committed tree (`git grep … HEAD`), noise filter documented:

```
=== sweep A: backticked `incident[-/] minus claude/incident ===
cicd-mobile-error-team.md:17,234   — `incident:<short-id>` is a GitHub ISSUE label; `incident-response.yml` is a WORKFLOW FILENAME
git-policy.md:212                  — the protected rule sentence itself (acceptance 6)
mobile-mode.md:48                  — workflow filename
test_git_hooks.py:491,529          — the bare `incident-42` FIXTURE name (case N's point, post-fix)
test_task_preflight.py:306,343     — historical comments about the OLD dead shape (accurate history)
sentry_error_response_team.md:176, tea_deep_reference.md:613 — artifact/command filenames
=== sweep B: unbackticked incident-\* ===
(zero hits after the comment reword)
```

Zero bare branch-prefix survivors. The one post-commit-1 hit was this lane's own comment quoting
the removed literal inside its removal story — the comment-literal class: a grep guard cannot tell
a claim from a mention of the claim. Reworded in `ec13bc7`; the sweep above is the final run at
that sha, and sweep B's zero includes `.sh` and `docs/` as the ticket demanded.

### Acceptance 6 — `git-policy.md:210-212` byte-identical

```
$ shasum -a 256 .agents/rules/git-policy.md      # captured BEFORE any edit
e1e165040d7a98350a5fed9ec4fdb94a6d37bf61f3eac0286de57a64208cbc90
$ git diff main...HEAD -- .agents/rules/git-policy.md
(empty)
$ shasum -a 256 .agents/rules/git-policy.md      # at the end
e1e165040d7a98350a5fed9ec4fdb94a6d37bf61f3eac0286de57a64208cbc90
```

### Mutation sweep — declared in the plan BEFORE running, all drawn from the code

Pre-declared in the plan; run as one sweep. Restore from COPIES (never `git checkout --`;
SCC-147's trap), application verified by an explicit unified-diff line count (SCC-129's lesson).

| # | Mutant | Named case | Result |
|---|---|---|---|
| M1 | incident arm moved BELOW `claude/*` (SCC-148's shadowing shape in a `case`) | INC allow | **KILLED** by its named case (exit 1) |
| M2 | pattern → `incident-*` (the old comment's fiction) | INC allow | **KILLED** by its named case (exit 1) |
| M3 | judge verdict `unknown` → `refuse` | INC allow | **KILLED** by its named case (exit 1) |
| M4 | pattern widened to `claude/*` (carve-out eats the story arm) | INC story-arm | **KILLED** by its named case AND the TBL loop (story→main, story→chore all flipped to allowed) |
| M5 | the pipeline-name note **deleted** | INC note | **killed dishonestly** — see below |
| M5b | the note replaced with `:` (script stays valid) | INC note | **KILLED** by its named case alone — the honest kill |

```
restored byte-identical: True
closing green confirmation: exit=0 ['-- 94/94 passed --']
```

**The M5 story — a finding against this lane's own sweep, caught by reading which line raised.**
M5 deleted both `echo` lines, which left an **empty `if` body — a syntax error in sh** — so every
case in the suite crashed and the sweep's verdict line still read "KILLED by its named case"
(the named case was indeed among the failures, along with everything else). That kill proves
deleting the lines breaks the script; it proves nothing about whether a *silently absent* note
would be noticed — the red-dies-before-its-assertion class, inside the sweep built to catch
exactly that class. M5b re-aims it: the note becomes a no-op (`:`), the script stays valid, and
the only case that can catch it is the note assertion — run separately, killed by that case alone.

## Code Review (2026-08-14)

(appended by /smh-code-review)

## Your Actions

(filled at close)
