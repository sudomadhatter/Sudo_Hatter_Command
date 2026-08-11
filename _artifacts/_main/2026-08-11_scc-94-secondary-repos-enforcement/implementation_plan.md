# SCC-94 — enforce `secondary_repos` at close-out

## The gap

`secondary_repos` appeared in three places — `MANIFEST_SCHEMA`, `smh-quick-dev.md`, and
`smh-close-task-merge-tree.md` — and was **read by nothing**. `check_manifest()` validated
`task_key` and `branch` only.

So a cross-repo task could declare *"this also lands in `Projects/X` under `KEY-00`"* and close out
green while that key was one `X`'s commit-msg hook rejects, its branch was never pushed, or `X`
was not even checked out. Declared cross-repo intent with zero verification is how the SCC-73
back-pointer stayed owed until an unrelated audit happened to surface it.

## Why close-out, and not `run_all`

Project-store defects are `[SIGNAL]` in the lobby's memory gate, never failures, and that is
deliberate: a project is a separate repo whose hook rejects this repo's keys, so a blocking gate
there would red **every unrelated lane** over a defect nobody in the lobby may fix.

That objection does not survive at close-out. A lane that *declares* a secondary repo has asserted
it is cross-repo work — it can commit there, and it is about to merge. Blocking it is fair, and a
single-repo lane never reaches any of this. Same signal, moved to the moment where the person
reading it is the person who can act on it.

## Acceptance

- A1 each declared row's repo resolves to a real git checkout — **including from a worktree**,
  where submodules do not populate
- A2 the declared ticket key is one that repo's own `.agents/jira.conf` answers to
- A3 that repo is clean and `0/0` with its origin — the lobby's `git status` cannot see it
  (`ignore = all`)
- A4 its memory store passes the **same** `check_store()` contract the lobby's does — blocking
- A5 a row with no `ticket:`, or a manifest using the unreadable inline `[{…}]` form, never passes
  silently
- A6 **negative controls:** a correct declaration still exits 0, a repo with no memory store yet is
  not a failure, and `secondary_repos: []` behaves exactly as before
- A7 the command body, the SOP row and all four generated doors say the rows are now enforced
- A8 `run_all` 12/12, `workflow_lint --toolkit-only` 0/0, `sop_currency` exit 0

## Test approach

RED first, against real git repos in temp dirs with real bare origins — these are ahead/behind and
ancestry questions, and a mocked git would only prove the mock agrees with itself. The RED run was
**6 of 9 failing**, with the three cases that *should* pass without the feature passing, which is
what distinguishes a real RED from fixtures that fail for setup reasons.
