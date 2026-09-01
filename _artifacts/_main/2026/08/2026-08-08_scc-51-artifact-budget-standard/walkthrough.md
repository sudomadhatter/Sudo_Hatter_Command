# SCC-51 — Artifact byte caps removed, replaced by a substance standard

Plan: [implementation_plan.md](implementation_plan.md) · Branch: `chore/SCC-51-artifact-budget-standard`
· Ticket: SCC-51 (epic SCC-33)

The 8 KB / 10 KB hard caps on `implementation_plan.md` and `walkthrough.md` are gone from every live
surface. What replaces them is a stated standard — *dense, not short* — plus one line that decides the
edge case: **length is never a reason to omit a finding, an AC, or a piece of evidence.**

## Task Checklist

- [x] Establish the ruling and the boundary (what goes, what stays)
  - The caps shipped **in the same commit** (2026-08-02) that made `implementation_plan.md` a
    **two-author** doc — dev writes it, `/sudo-self-audit` appends §7 into it. Proven with `git log -S`.
    A fixed cap on a two-author doc squeezes the second author, and the second author is the auditor.
  - The number was never validated against a real audit. The first Full audit run under it compressed
    its own findings to fit — the gate cutting substance while the filler survived.
- [x] Remove the caps from all 9 planned sites (rule ×2, commands ×2, tomls ×3, linter, tests)
- [x] Defend the removal with tests instead of prose
  - Two guard cases: the linter must expose neither `check_artifact_budgets` nor `_BUDGETS`, and the
    rule must still carry the standard text. A future agent "restoring the budget" trips the suite.
- [x] Sweep wider than the plan's own list — **found 4 more live sites**
  - `.opencode/commands/` is a **generated mirror**. Editing `.agents/commands/` left the opencode lane
    still reading `≤ 10 KB`. Any command edit has to check the mirror or re-run `/sync-agents`.
  - Three **memory** files still taught the cap. This is the one that mattered: memory is recalled
    into context before any rule file is read, so `MEMORY.md:128` ("8/10 KB binds in-flight STORY docs")
    would have reinstalled the cap on the next session — from a source the operator never sees.
    Renamed the memory to `limits-relocate-content-never-truncate` and repointed both backlinks.
- [x] Keep the limits that are legitimate — verified each against the test below
- [x] Move the SOP quick-reference in the same commit (armed `sop-currency` gate)

## The rule that decides it

A limit is **legitimate** when going over means *the wrong content is in this file* — the fix MOVES or
DELETES content that belongs elsewhere, and nothing is lost. A limit is **harmful** when going over means
*you found more than expected* — the rules forbid a second file, so the only remaining lever is
destroying substance.

**Removed** (fail the test): plan ≤ 8 KB, walkthrough ≤ 10 KB.
**Kept** (pass it): `active-context.md` ≤ 20 KB, board note budget, board size cap, autopilot `-MaxCost`,
quick-dev's soft 900–1600-token spec range, and *never split into a second file* — a structure rule, not
a size rule.

## Evidence

| AC | Evidence |
|---|---|
| No byte cap survives on any live surface | `git grep "10 KB\|8 KB"` outside `_artifacts/` returns **4 hits, all deliberate dated notes** recording the removal (rule, linter comment, test comment, SOP page) |
| The linter no longer enforces a threshold | `_BUDGETS` + `check_artifact_budgets()` + the `main()` call site deleted from `workflow_lint.py`; replaced by a comment saying do not re-add one, and why |
| The removal is defended, not just documented | 2 new guard cases in `test_workflow_lint.py`, both PASS |
| The standard replaced the number | `artifacts-always-first.md` §5 carries "Dense, not short — and there is NO byte cap" + the ⛔ omission line + a dated removal note |
| Memory can't re-teach the cap | memory renamed + rewritten; `MEMORY.md` index line and the one backlink repointed |
| Kept limits are intact | `active-context` 20 KB check, `check_board_note_budget`, and `BOARD_SIZE_CAP` all still present and still tested (W4 cases pass) |

```
python3 .agents/scripts/tests/run_all.py    → 8/8 files passed
  == encoding scanner control ==  19/19 passed
  [PASS] SCC-51 no byte-budget check exists on the linter
  [PASS] SCC-51 the rule states the standard that replaced the cap
```

`workflow_lint.py` project mode was not run: the lobby has no
`_bmad-output/implementation-artifacts/sprint-status.yaml`, so it resolves no project here. Its
`--staged` encoding gate runs on commit via the pre-commit hook.

## Code Review (2026-08-08)

Verdict: PASS @ (commit below)

Reviewed against the plan's own site list, then independently by a wider `git grep` — which is what
surfaced sites 10–13. The plan's list was incomplete in exactly the way the change was about: it covered
the files I had read, not the files that would be *read to me*.

## Your Actions

Landed on `chore/SCC-51-artifact-budget-standard` off `main` @ `64b2aa9`. Nothing merged, nothing pushed
to `main`.

- Merge the branch when you're ready (a `chore/*` off main — no worktree close-out, no board flip).
- **Before merging:** two untracked read-copies exist in your checkout at
  `_artifacts/_main/2026-08-08_scc-51-artifact-budget-standard/` and
  `_artifacts/_main/2026-08-08_scc-41-autopilot-worktrees/`. Git refuses to overwrite untracked files,
  so the SCC-51 one must be deleted first.
- SCC-41 (autopilot worktrees) is unblocked by this and gets its plan rewritten at full detail next.
