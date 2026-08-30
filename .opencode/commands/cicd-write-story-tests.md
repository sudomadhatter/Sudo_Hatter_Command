---
description: Story prep — create the next BMAD story, then write its failing acceptance tests (ATDD red phase) before any code. Step ① of the sudo dev flow.
platforms: [opencode, antigravity, zoo]
---

# /cicd-write-story-tests — Create Story + Red Tests (①)

Thin orchestrator — calls two existing workflows back-to-back so a story arrives with its acceptance
tests already written and **failing**. Tests-first, before any dev. Project-scoped (targets THIS repo).

> Flow position: `cicd-boot-sprint-memory` → **`cicd-write-story-tests`** → `cicd-dev-story-tests` →
> `cicd-code-review` → `cicd-close-story-merge-tree`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
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
   `/cicd-create-epic-sprint` — missing → go back and run it), then open
   `.claude/worktrees/<story-slug>` on `claude/<JIRA-KEY>-<story-slug>` **off the epic ref by name** —
   slug `story-<id-dashed>-<short-name>`, e.g. `story-21-3-student-archive`:
```bash
git -C "$PROJECT_ROOT" fetch origin epic/<JIRA-KEY>-<slug>
git -C "$PROJECT_ROOT" worktree add --no-track .claude/worktrees/<story-slug> \
    -b claude/<JIRA-KEY>-<story-slug> origin/epic/<JIRA-KEY>-<slug>
```

   ⛔ **`--no-track` is not optional, and it is the price of naming the base as an operand.** A
   *remote-tracking* start point makes `branch.autoSetupMerge` (on by default) set this lane's upstream
   to **the epic**, so `git status -sb` reads `## claude/…...origin/epic/…` — every later `0 0` check
   measures the wrong remote — and a bare `git push` dies with *"The upstream branch of your current
   branch does not match the name of your current branch"*. `push.autoSetupRemote=true` does **not**
   rescue it, and git's own suggested remedy is `git push origin HEAD:epic/…`, the mid-story epic push
   `.agents/rules/worktree-per-story.md` G3 bans. With `--no-track` the lane has no upstream until its
   first push, which then creates `origin/claude/<JIRA-KEY>-<story-slug>` and reports `0 0`. Same trap,
   different cure, at `.agents/commands/smh-plan-task.md` — a Task lane branches from `origin/main` and
   spends a second line on `git branch --unset-upstream`; one flag here cannot be forgotten.

   ⛔ **The base is an OPERAND, so the shared checkout never leaves `main` (SCC-256).** `EnterWorktree`
   is the other door and it is **not** equivalent — `worktree.baseRef: "head"` makes it inherit the
   CURRENT HEAD, so taking it means checking the epic branch out first and going **back to `main`** the
   moment the tree is open. A shared checkout left parked on an epic branch is what
   `.agents/rules/worktree-per-story.md` ("it stands on `main`") exists to prevent: every later
   `git status`, `worktree add` and boot then reads a tree the operator believes is `main`.
3. **Either way, link the gitignored assets** — `python3 .agents/scripts/link-worktree-assets.py
   "$PROJECT_ROOT"/.claude/worktrees/<story-slug>` (PC: `python`). A tree has no `.env`,
   `backend/.venv`, `auth_keys/` or `node_modules` of its own and the runners resolve them relative to
   CWD, so Step 3's reds cannot even be run red without it. Idempotent on a re-entered tree;
   `/cicd-prune-worktree` runs the `--unlink` half before the tree is removed.

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

1. **Rule TWO things first** (they shape the mint) — both are per-story facts genuinely knowable
   at pickup, which is exactly why the third one left:
   - **Lane** — can this story ship via `/cicd-quick-dev` instead of the full ①②③ loop? (Small blast
     radius, P2/P3 risk score, no new endpoint/contract/auth surface.) → label `quick-dev`. Default is
     the full loop, no label.
   - **Blocked** — does it depend on an unlanded story/ticket? → label `blocked` + a `Blocks` link.

   ⛔ **Parallel is NOT ruled here** (operator ruling 2026-08-09, SCC-56). `parallel-ok` is a
   property of a **set at a moment**, never of one story — and at this instant the siblings do not
   exist yet: this step mints 19.1's ticket **before** 19.2's story file is written, so there is
   nothing to compare against, and it is never re-evaluated. A boolean also cannot express
   *"safe after AVCH-34"*. The proof it never worked is empirical — **zero** tickets across `SCC`
   and `AVCH` carried the label. Never re-add it here. Once the epic's stories are all written:
   **`/cicd-label-tasks <EPIC-KEY>`**.
2. **Mint it — one call does the dedupe, the outline, and the proof** (SCC-49: a ticket with only a
   summary is a title, not a ticket, and the whole board was minted that way):

   ```bash
   python3 .agents/scripts/jira_feed.py mint --story <n.m> --project <PROJECT> \
          --jira-project <PROJ> --epic-key <EPIC-KEY> --summary "<n.m> — <Story Title>" \
          --lane <full|quick-dev> [--blocked-by <KEY>] --apply
   ```

   It (a) searches the BMAD number first — a backfilled board or a re-run already has the ticket, and
   a twin nothing will ever move again is worse than none — reusing that key and backfilling the
   outline if it was bare; (b) renders the **description from the story file** you just wrote (its
   statement, its ACs, the lane rulings, the story-file path) — nothing invented, and a story with no
   AC section says exactly that; (c) creates it bare (no `--assignee`), parented, with the ruled
   labels, **typed `Story` because a story file backs it** — not because it has a parent; everything
   has a parent, and a `Task` under a *grouping* epic looks identical (→ `.agents/rules/jira.md`
   §Work-item types, which is where that model is documented); (d) **reads the ticket back and exits 2
   if the description did not land.**
   It prints `JIRA_KEY=<KEY>` — take the key from there, **never invent one.** Non-zero exit → STOP
   and fix; do not carry on with an unkeyed or hollow ticket. Full acli reference:
   `.agents/rules/jira.md`.
3. **Stamp the story file frontmatter** — the file is the machine truth, the board only mirrors it:
   `jira_key: <KEY>` (Step 4 of `/cicd-close-story-merge-tree` moves the ticket by reading exactly
   this field), plus the rulings: `lane: quick-dev|full`, `blocked_by: [<keys>]` (omit when empty).
   ⛔ No `parallel_ok:` — same reason as above; `/cicd-label-tasks` owns that field.
4. **Set its state:** blocked → `acli jira workitem link create --out <BLOCKER-KEY> --in <KEY> --type
   Blocks`, then transition to `Blocking` if the board has that status (else the label carries it).
   ⛔ The status is **`Blocking`**, not `Blocked` — `Blocked` exists on neither board and the
   transition fails outright (`jira.md` §The map).
   Not blocked → **`python3 .agents/scripts/jira_feed.py start --key <KEY> --apply`** (SCC-113).

   > This was a prose `acli transition` step until SCC-113. It is the script now for the reason
   > SCC-49 gave for the other four seams: it reads the ticket back rather than trusting an `acli`
   > that exits 0 on a write it never made, and it is idempotent, so ① re-run on an existing ticket
   > cannot double-move it. **Read the exit code:** `0` moved or already there · `3` left alone
   > (the ticket is `Blocking`/`In Review`/`Deferred` — expected when you just linked a blocker
   > above, so continue) · `2` the board REFUSED it (a `Done` key means the key is wrong — STOP) ·
   > `4` the board was UNREACHABLE (transport, not a verdict — carry on, and ⛔ do **not** mint a
   > second ticket). Full reference: `.agents/rules/jira.md`.

## Step 2 — BDD Vision Lock (ATDD Contract Phase — MANDATORY, never silently skipped)
Invoke the **`/cicd-bdd-tests`** workflow. This is an interactive session with the Test Architect (Murat)
to hash out exact expected behaviors until they are 100% understood. The locked Given/When/Then contract
is codified **into the story's ATDD red test file(s)** (BDD-structured pytest scenarios for backend;
BDD-structured vitest/Playwright `describe`/`it` for frontend) — Step 3 extends those same files. A
standalone `pytest-bdd` `.feature` + step-defs pair is **opt-in only** (the human explicitly chooses it
during the lock, when Gherkin itself buys value); never default to it.

This phase is a standing part of the enterprise flow — **the ONLY exit without a contract is a recorded
waiver**: the story has no product-behavior surface (docs-only, characterization-only), the human confirms
the waiver in chat, and the story frontmatter records `bdd: waived — <rationale>`. Either way the story
leaves ① carrying `bdd: locked` (+ contract paths) or `bdd: waived` in its frontmatter —
`/cicd-dev-story-tests` (②) **hard-gates on that record** and will refuse to dev a story without it.

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
**Do NOT start implementing.** `cicd-dev-story-tests` turns the reds green next.

**Git:** commit ①'s output **inside the worktree** with explicit paths (`git add -A` / `.` / `-u` are
banned — they sweep other teams' work in). Do NOT push the epic branch mid-story; Step 3 of
`/cicd-close-story-merge-tree` owns that landing (→ `worktree-per-story`, `git-policy`).

Optional additional input: $ARGUMENTS
