# Walkthrough — SCC-215: `## Your Actions` is errands only

**Ticket:** SCC-215 (Task) · **Branch:** `chore/SCC-215-your-actions-errands-only` · **Lane:** `/smh-quick-fix`

> **This record is retroactive, and saying so is the point.** The three law edits shipped on
> 2026-08-17 as `11c5b7d` and reached `main` in the SCC-205 wave, but no walkthrough, no `task.yaml`
> and no Dev Record were ever filed — so the ticket sat at `In Progress` with its work already
> landed. This session absorbed `origin/main`, verified every acceptance criterion against the
> shipped text rather than against the diff's promise, and wrote the record the close-out needs.
> Artifacts live in the tree; their absence is not evidence a step ran.

## What changed

**Shipped 2026-08-17 in `11c5b7d` (already on `main`):**

- `.agents/rules/artifacts-always-first.md` §6 (line 239) — the definition. `## Your Actions` is now
  **errands only**: what the operator must go and DO outside the chat. `a decision` is deleted from
  the legal row types and replaced with an explicit ban — *"Never a decision or a question. The
  operator is in the session — ask, and tick the row with the answer."* The survival test is written
  as a test: a row survives only if they would have to leave the chat to do it.
- `.agents/rules/git-policy.md` line 414 — the restatement, moved in the same commit so the two law
  sites cannot drift. Carries the same errands-only wording, the same ban, and a pointer back to
  `artifacts-always-first` §6 as the definition.
- `docs/_scc_sops_prds/workflows_testing_SOP.md` (§ `/smh-close-task-merge-tree`, ~line 780) — the
  operator-facing page said the contradicting thing at the operator's own desk, so it rode along:
  errands only, with the history of the two retirements (*a main merge*, then *a decision*) kept as
  context rather than as law.

**This session:**

- Absorbed `origin/main` into the lane — it was 20 commits behind, and the merge fast-forwarded to
  `2c435ea` because `11c5b7d` was already an ancestor of `main`. The PR therefore carries this
  record and nothing else.
- `_artifacts/_main/2026-08-19_SCC-215-your-actions-errands-only/` — this walkthrough and `task.yaml`.
- `_artifacts/_main/INDEX.md` — the session row.

## Evidence

**Acceptance criteria, measured against the shipped text on this branch:**

| AC | Result | How |
|---|---|---|
| 1. `decision` is no longer a legal row type at either site | ✅ | `grep -n -i decision` on both files: every surviving hit is either the ban itself (`artifacts-always-first:242`, `git-policy:415`), or unrelated prose about the sign-off (`git-policy:83,98,102-103`) and other sections (`artifacts-always-first:41,195,266,289`). No hit lists it as a permitted row. |
| 2. Both sites carry the ask-first line and do not contradict | ✅ | `artifacts-always-first:239-243` and `git-policy:414-417` both read **errands only** + *"Never a decision or a question"*; `git-policy` points at `artifacts-always-first` §6 as the definition, so there is one source and one restatement. |
| 3. New text uses a generic referent, not a personal name | ✅ | Both new passages say *"the operator"*. The two pre-existing `Daniel` mentions in `git-policy` sit in untouched neighbouring bullets and are outside this ticket's scope. |

**Scope check:** `.agents/commands/cicd-code-review.md:363` needed no change (the ticket said so) and
got none. `jira_feed.py`'s `_BANNED_PATTERNS` was declared NOT IN SCOPE and is untouched — the law
moved, the filter did not.

**Gates, run bare on this branch:**

- `python3 .agents/scripts/tests/run_all.py` → **34/34 files passed**
- `python3 .agents/scripts/workflow_lint.py --toolkit-only` → **0 error(s), 0 warning(s), 8 info** (exit 0)
- `python3 .agents/scripts/check_maps.py --depth3-only --strict` → see below
- `python3 .agents/scripts/lane_qualify.py` on the real diff → **LIGHT**

`git rev-parse HEAD` → `c6f5e54` (the record commit, pushed to `origin/chore/SCC-215-your-actions-errands-only`). The law itself is `11c5b7d`, already an ancestor of `origin/main` — this branch fast-forwarded onto `2c435ea` before the record was written, so the gate totals above were measured on a tree identical to `main` plus this file.

## Your Actions

- [x] The merge itself — lands via this branch's PR
