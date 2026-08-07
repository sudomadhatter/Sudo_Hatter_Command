---
description: Story prep — create the next BMAD story, then write its failing acceptance tests (ATDD red phase) before any code. Step ① of the sudo dev flow.
platforms: [opencode, antigravity]
---

# /sudo-write-story-tests — Create Story + Red Tests (①)

Thin orchestrator — calls two existing workflows back-to-back so a story arrives with its acceptance
tests already written and **failing**. Tests-first, before any dev. Project-scoped (targets THIS repo).

> Flow position: `sudo-boot-sprint-memory` → **`sudo-write-story-tests`** → `sudo-dev-story-tests` →
> `sudo-code-review` → `sudo-update-sprint-memory`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/sudo-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override (remainder = the real argument — story id, focus, …) → `.agents/active-project.txt` → else
**STOP and ask** — never guess, never operate on the lobby. Set `PROJECT_ROOT` and **echo exactly**
`Target: Projects/<name>` before any work. Every bare path below resolves under `PROJECT_ROOT` (nested
`bmad-*`/`1_*` skills bind their `{project-root}` to it); a needed path missing under `PROJECT_ROOT` →
STOP and say so, never fall back to the lobby.

## Step 0.5 — Open the story worktree (BEFORE the first project file is written)
① writes the story file and its red tests, so `worktree-per-story` applies in full. Under `PROJECT_ROOT`:
1. **`git worktree list`** — if a `claude/<story-slug>` tree already exists (a re-run, or ② started),
   **re-enter it**; never open a second for the same slug.
2. Else confirm the story's EPIC branch exists (`epic/<epic-key>-<slug>`, cut by
   `/sudo-create-epic-sprint` — missing → go back and run it) and HEAD is on it (**never** `main`),
   then open `.claude/worktrees/<story-slug>` on `claude/<story-slug>` off it — slug
   `story-<id-dashed>-<short-name>`, e.g. `story-21-3-student-archive`.

**Ordering caveat:** the slug depends on the story id, which Step 1 may be the thing that resolves ("the
next story"). Resolve the id first, then open the tree — still before the story file is written; never
write into the shared checkout planning to move it afterwards.

Re-bind every path below under it (story file, red tests, `_artifacts/…`, `sprint-status.yaml`, test
commands) and echo `Worktree: <path> (<branch>)`.

## Step 1 — Create the story
Invoke the **`bmad-create-story`** skill for the story in `$ARGUMENTS` (a story id like `11.16`, or "the
next story" when empty). This writes the story file under `_bmad/bmm/stories/` with its acceptance
criteria (ACs). Confirm the story file + ACs exist before continuing. If create-story stops for input,
surface it and stop — never guess.

## Step 2 — BDD Vision Lock (ATDD Contract Phase — MANDATORY, never silently skipped)
Invoke the **`/sudo-bdd-tests`** workflow. This is an interactive session with the Test Architect (Murat)
to hash out exact expected behaviors until they are 100% understood. The locked Given/When/Then contract
is codified **into the story's ATDD red test file(s)** (BDD-structured pytest scenarios for backend;
BDD-structured vitest/Playwright `describe`/`it` for frontend) — Step 3 extends those same files. A
standalone `pytest-bdd` `.feature` + step-defs pair is **opt-in only** (the human explicitly chooses it
during the lock, when Gherkin itself buys value); never default to it.

This phase is a standing part of the enterprise flow — **the ONLY exit without a contract is a recorded
waiver**: the story has no product-behavior surface (docs-only, characterization-only), the human confirms
the waiver in chat, and the story frontmatter records `bdd: waived — <rationale>`. Either way the story
leaves ① carrying `bdd: locked` (+ contract paths) or `bdd: waived` in its frontmatter —
`/sudo-dev-story-tests` (②) **hard-gates on that record** and will refuse to dev a story without it.

## Step 3 — Write the failing acceptance tests (ATDD red phase)
Invoke the **`bmad-testarch-atdd`** skill against the story just created. Generate any remaining unit/component acceptance tests that codify each AC and **must fail now** (no implementation exists yet) —
**extending the Step 2 contract file(s), not minting sibling test files** (one red file per story per
stack; the Vision Lock scenarios and the ATDD reds live together). If the epic has a
`bmad-testarch-test-design` risk plan, pull it so P0 ACs get priority coverage.

**Ground every red before it counts (per `tests-must-gate-for-real`).** A red must fail because the
feature is *unbuilt*, never because it invented something. Before leaving this step, verify against the
ACTUAL code (grep the producing surface; read the page/handler/endpoint) that every asserted string,
selector, endpoint, and **precondition** is real or is the honest absence of a real thing — and that the
test's assumed auth / precondition model matches reality (e.g. don't assert an auth-gated page as
"public"). A test asserting copy that does not exist in source, or misreading the auth model, is
**fiction, not a red** — it fails identically whether the feature is unbuilt or the assertion is bogus,
so it can never go green. Fix or drop it here; do not hand fiction to ②.

## Done
Report: story id + path, ACs covered, the red tests written (paths) and confirmation they fail as
expected — plus the `Worktree: <path> (<branch>)` line from Step 0.5, so ② knows where the story lives.
**Do NOT start implementing.** `sudo-dev-story-tests` turns the reds green next.

**Git:** commit ①'s output **inside the worktree** with explicit paths (`git add -A` / `.` / `-u` are
banned — they sweep other teams' work in). Do NOT push the epic branch mid-story; Step 7 of
`/sudo-update-sprint-memory` owns that landing (→ `worktree-per-story`, `git-policy`).

Optional additional input: $ARGUMENTS
