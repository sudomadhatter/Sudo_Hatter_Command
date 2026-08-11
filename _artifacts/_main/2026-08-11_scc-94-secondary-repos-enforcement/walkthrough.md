# SCC-94 — walkthrough

**`secondary_repos` is now enforced.** Nine new cases; `test_task_preflight` 48 → 59, all passing.
`run_all` 12/12 exit 0 · `workflow_lint --toolkit-only` 0/0 exit 0 · `sop_currency` exit 0.

Verified end to end against the live **SCC-88** lane, not only fixtures:

```
[INFO ] secondary: Projects/AGY_AVIATIONCHAT: empty stub in this lane (submodules do not
        populate in a worktree) - verified in the shared checkout at …/Projects/AGY_AVIATIONCHAT
[INFO ] secondary: Projects/AGY_AVIATIONCHAT: AVCH-53 matches its jira.conf (AVCH)
-- 0 error(s), 1 warning(s), 107 info --   VERDICT: clear to close out and merge
```

## The two bugs I found in my own work

**1. `\s*` swallowed the line break.** `secondary_rows()` matched `^secondary_repos:\s*(.*)$`
under `re.MULTILINE`. `$` matches *before* a newline, but `\s` matches the newline **itself**, so
`\s*(.*)` ran past the line end and captured the next line. Every block-form manifest read as an
"inline form", and every declared repo went unverified behind a warning that looked like a
manifest style complaint. Caught because the positive control that had passed during RED started
*failing* after the implementation — more cases failing after writing the feature was the tell.
Fixed with `[^\S\n]*` (horizontal whitespace only).

**2. ⭐ It blocked every cross-repo close-out, in the one place close-outs happen.** The first
version resolved the secondary repo only under the lane. **Submodules do not populate in a
worktree** — `Projects/<name>/` is an empty stub in every lane — so the real SCC-88 lane got:

> `ERROR secondary: Projects/AGY_AVIATIONCHAT: declared as a secondary repo but not a git checkout here`

All nine fixtures were green when this was true. They built the secondary inside a plain repo, so
they never modelled the only environment that matters. Now it falls back to the main worktree's
checkout — which is not a workaround: submodule content is **shared**, so there is exactly one
checkout of that repo and one branch state to verify — and it says which checkout it used. Pinned
by a test that builds a **real linked worktree** with the secondary present only in the main
checkout.

That test also corrected a wrong assertion of mine: I asserted `code == 0`, but a live lane always
warns that its worktree is still checked out, which is exit 1. The property under test is that the
check does not **block** (exit 2), and it now says so.

## Design note kept in the code

The blocking/reporting split is the load-bearing decision and the comment above `check_secondary`
carries it: project-store defects cannot fail `run_all`, because a lobby gate that reds for a
defect nobody in the lobby may fix blocks every unrelated lane. At close-out that objection does
not hold — the lane declared the cross-repo work, so it can commit there.

`store_problems()` imports `check_store` from the gate rather than reimplementing it: a second
copy of "what makes a store valid" would drift from the one `run_all` enforces. In this repo
`.agents/scripts/tests/` **is** the enforcement layer, so the dependency is not a test/production
inversion. An import failure is reported as a warning, never swallowed — a check that quietly
becomes a no-op when its dependency moves is worse than no check, because the green still looks
earned. Both the "it read the store" and "a seeded defect fires" halves were verified directly
against AGY's real store rather than inferred from silence.

## Doors and docs

The command body crossed into a stale-mirror state: `.opencode/commands/smh-close-task-merge-tree.md`
is a **full 16.4 KB mirror**, not a stub, so editing the command left it out of date. Re-synced —
all four doors current, and the change is scoped to that one command plus the sync manifest.

Noted in passing, **not fixed here**: `workflow_lint --toolkit-only` reported 0 errors / 0 warnings
while that mirror was stale. A generated door can silently drift from its command and the lint does
not see it. That is its own ticket.

The SOP row for `/smh-close-task-merge-tree` never mentioned the manifest at all. `sop_currency`
passed anyway, so this was added rather than taken as permission to skip — a cross-repo close-out
can now be blocked by *another repo's* state, which is exactly the kind of thing an operator has to
learn before it happens, not during.

## Scope held

The AGY-side memory gate stays an AVCH ticket. Repo-local enforcement never centralises; this is
the half the command center actually owns.
