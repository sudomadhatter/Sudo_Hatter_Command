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
1. **`git worktree list`** — if a `claude/<JIRA-KEY>-<story-slug>` tree already exists (a re-run, or ② started),
   **re-enter it**; never open a second for the same slug.
2. Else confirm the story's EPIC branch exists (`epic/<JIRA-KEY>-<slug>`, cut by
   `/sudo-create-epic-sprint` — missing → go back and run it) and HEAD is on it (**never** `main`),
   then open `.claude/worktrees/<story-slug>` on `claude/<JIRA-KEY>-<story-slug>` off it — slug
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

## Step 1.6 — Mint the story's Jira ticket + rule the lane (AUTOMATIC — operator ruling 2026-08-07)
The story file exists, so its ticket must too — ① is the story's single classification point. Using the
repo's project from `.agents/jira.conf` and the EPIC's ticket key (it's in the epic branch name):

1. **Rule three things first** (they shape the mint):
   - **Lane** — can this story ship via `/sudo-quick-dev` instead of the full ①②③ loop? (Small blast
     radius, P2/P3 risk score, no new endpoint/contract/auth surface.) → label `quick-dev`. Default is
     the full loop, no label.
   - **Parallel** — can it run beside the epic's other in-flight stories? Binds on FILE OVERLAP (per
     the parallel-lanes rule): disjoint file sets → label `parallel-ok`.
   - **Blocked** — does it depend on an unlanded story/ticket? → label `blocked` + a `Blocks` link.
2. **Mint it — one call does the dedupe, the outline, and the proof** (SCC-49: a ticket with only a
   summary is a title, not a ticket, and the whole board was minted that way):

   ```bash
   python3 .agents/scripts/jira_feed.py mint --story <n.m> --project <PROJECT> \
          --jira-project <PROJ> --epic-key <EPIC-KEY> --summary "<n.m> — <Story Title>" \
          --lane <full|quick-dev> [--parallel-ok] [--blocked-by <KEY>] --apply
   ```

   It (a) searches the BMAD number first — a backfilled board or a re-run already has the ticket, and
   a twin nothing will ever move again is worse than none — reusing that key and backfilling the
   outline if it was bare; (b) renders the **description from the story file** you just wrote (its
   statement, its ACs, the lane rulings, the story-file path) — nothing invented, and a story with no
   AC section says exactly that; (c) creates it bare (no `--assignee`), parented, with the ruled
   labels; (d) **reads the ticket back and exits 2 if the description did not land.**
   It prints `JIRA_KEY=<KEY>` — take the key from there, **never invent one.** Non-zero exit → STOP
   and fix; do not carry on with an unkeyed or hollow ticket. Full acli reference:
   `.agents/rules/jira.md`.
3. **Stamp the story file frontmatter** — the file is the machine truth, the board only mirrors it:
   `jira_key: <KEY>` (Step 4.5 of `/sudo-update-sprint-memory` moves the ticket by reading exactly
   this field), plus the rulings: `lane: quick-dev|full`, `parallel_ok: true|false`,
   `blocked_by: [<keys>]` (omit when empty).
4. **Set its state:** blocked → `acli jira workitem link create --out <BLOCKER-KEY> --in <KEY> --type
   Blocks`, then transition to `Blocked` if the board has that status (else the label carries it).
   Not blocked → transition to `In Progress` (`--yes`). Full acli reference: `.agents/rules/jira.md`.

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
