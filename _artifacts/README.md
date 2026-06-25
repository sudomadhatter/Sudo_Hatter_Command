# `_artifacts/` — shared memory (home base)

Plans, walkthroughs, and continuity for work done **from the home base**. The session ledger is
[`INDEX.md`](./INDEX.md) (placement rules live in its header); the full model is `_docs/workspace-standard.md`;
the plan-first protocol is `.agents/rules/artifacts-always-first.md`.

## Where a session folder goes — by where you WORK FROM
The deciding factor is your **cwd**, not only what the work is about (full rules → the [`INDEX.md`](./INDEX.md) header):
- **From the home base** (cwd = `Sudo_Hatter_Command/`) → **here**: project work → a per-project bucket
  `_artifacts/<project>/…` (the bucket name = the `Projects/<name>/` folder); home-base / cross-project work →
  `_artifacts/_home/…`. Either way, log a row in `INDEX.md`.
- **From inside a project** (cwd = `Projects/<name>/`) → that project's own `Projects/<name>/_artifacts/` and its
  own `active-context.md` / `INDEX.md` (follow its rules — not this ledger).
- **Finding history:** look in BOTH the home-base bucket `_artifacts/<project>/` and the project-local one.

## How to structure the folder
- **Random / system task** → `<YYYY-MM-DD>_<slug>/` (date first so they sort; slug = lowercase-hyphenated, ≤6 words).
- **Story** → `<epic>/<story>/` — **the epic folder houses all of its stories. Create the epic folder if it isn't
  there yet**, then nest the story inside (e.g. `epic-9/story-9.4-ios-shell/`). Story folders are epic-scoped, not date-prefixed.
- **Retired** → `_archived/` — archive history, don't delete it.

## What each session folder carries
| File | When |
|---|---|
| `implementation_plan.md` | always — approved **before** any edits |
| `walkthrough.md` | at close — what changed + **real pasted test output** + a **"Your Actions"** git command |
| `task-list.md` | at close — snapshot of the final TodoWrite list |
| `code-review.md` / `self-audit-stress-test.md` / `bug-list.md` | when those run |

**Continuity:** `active-context.md` is the pickup/handoff brief for that location —
`_artifacts/<project>/active-context.md` (a project worked on from here) or `_artifacts/_home/active-context.md`.
