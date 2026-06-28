# `_artifacts/` — shared memory (home base)

Plans, walkthroughs, and continuity for work done **from the home base**. The session ledger is
[`INDEX.md`](./INDEX.md) (placement rules live in its header); the full model is `_docs/workspace-standard.md`;
the plan-first protocol is `.agents/rules/artifacts-always-first.md`.

> **⛔ The store is `_artifacts/` — never `_claude_artifacts/` or `_opencode_artifacts/`** (both retired/deleted).
> Every agent and tool writes here — `/bmad-dev-story`, `/bmad-quick-dev`, autopilot, or a hand session alike.
> If a story's `source:` line or an old note points at `_claude_artifacts/`, that is dead history — write here.

## Where a session folder goes — three rules, by where you WORK FROM
The deciding factor is your **cwd**, not only what the work is about (full rules → the [`INDEX.md`](./INDEX.md) header):
1. **Project work** → a per-project bucket `_artifacts/<project>/…` (bucket name = the `Projects/<name>/` folder).
   **Create the bucket if it isn't there yet; otherwise reuse it.**
2. **Main / home-base / cross-project work** → `_artifacts/_main/…` (formerly `_home`).
3. **Stories** → nest under the parent **epic folder** `epic_<E>/<story>/` (create `epic_<E>/` if missing) —
   **any** story (autopilot, BMAD, or hand-dev'd); the parent is decided by the story id, not the tool.
- **From the home base** (cwd = `Sudo_Hatter_Command/`) → **here**, per rules 1–3; log a row in `INDEX.md`.
- **From inside a project** (cwd = `Projects/<name>/`) → that project's own `Projects/<name>/_artifacts/` and its
  own `active-context.md` / `INDEX.md` (follow its rules — not this ledger). No *cross-project* `_main` inside a
  project — but a project keeps a **local `_main/`** for its own system/infra work.
- **opencode** writes under [`opencode/`](./opencode/README.md), applying the same three rules inside it.
- **Finding history:** look in BOTH the home-base bucket `_artifacts/<project>/` and the project-local one.

## How to structure the folder
- **Story** → `epic_<E>/<story>/` — **the epic folder houses all of its stories. Create `epic_<E>/` if it isn't
  there yet**, then nest the story inside (e.g. `epic_9/story-9.4-ios-shell/`, or an autopilot run
  `epic_14/2026-06-27_autopilot-14-6/`). Epic-scoped, not date-prefixed. Holds for **any** story — the parent is
  the story id, not the tool.
- **System / infrastructure** ("systems things": the agent system, rules, scripts, CI) → `_main/<YYYY-MM-DD>_<slug>/`.
- **Random one-off** → `<YYYY-MM-DD>_<slug>/` (date first so they sort; slug = lowercase-hyphenated, ≤6 words).
- **Retired** → `_archived/` — archive history, don't delete it.

## What each session folder carries
| File | When |
|---|---|
| `implementation_plan.md` | always — approved **before** any edits |
| `walkthrough.md` | at close — what changed + **real pasted test output** + a **"Your Actions"** git command |
| `task-list.md` | at close — snapshot of the final TodoWrite list |
| `code-review.md` / `self-audit-stress-test.md` / `bug-list.md` | when those run |

**Continuity:** `active-context.md` is the pickup/handoff brief for that location —
`_artifacts/<project>/active-context.md` (a project worked on from here) or `_artifacts/_main/active-context.md`.
