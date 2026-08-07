---
description: End-of-session / story close-out save — advance the closed story to done (running this command IS Daniel's sign-off; only objectively-red /sudo-code-review tests block the flip), code-verify, route learnings to specs/rules/memory, prune active-context, then LAND the story branch on its EPIC branch (Step 7). Run LAST when closing a story or session.
platforms: [opencode, antigravity]
---

# /sudo-update-sprint-memory — Session End (close-out)

> **Rules in force for this command:**
> - `.agents/rules/worktree-per-story.md` — one worktree per story, resolve-or-STOP, never delete through a junction

Self-contained, project-scoped — targets THIS repo's `_bmad-output/`. Run as the last step closing a story
(or any dev / brainstorm / research session). **Active-context holds STATE, not history** — narratives go to
the walkthrough + git, durable cross-session facts to Claude's auto-memory; this keeps `active-context.md`
small so `/sudo-boot-sprint-memory` stays cheap.

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/sudo-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** *"Which project are we closing out?"* —
never guess, never operate on the lobby. Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>`
before any work; every bare path below resolves under `PROJECT_ROOT`, and a needed project path missing
there → STOP and say so. ONE exception to §BIND: Step 6's Claude auto-memory write always targets Daniel's
global memory dir.

## Step 0.5 — Sync the branch BEFORE you read or edit the board (parallel-lane safety)
Steps 1–6 read **and rewrite** `sprint-status.yaml` + `active-context.md`. Do that on a stale base and you
author every board edit against an old file, then discover it at Step 7's merge — on the two hottest files
in the repo. So absorb the story's EPIC branch FIRST, inside the worktree (`epic/<JIRA-KEY>-<slug>` —
exactly one live `epic/*` branch is the normal case):

```bash
git fetch origin epic/<JIRA-KEY>-<slug>
git rev-list --count HEAD..origin/epic/<JIRA-KEY>-<slug>    # >0 → behind
git merge origin/epic/<JIRA-KEY>-<slug>                     # CONFLICT → STOP and report, never force
```

Echo `Base: current with origin/epic/<JIRA-KEY>-<slug> @ <sha>`. Step 7 re-merges as a cheap safety net; this one is
what makes the board edits land clean. If another lane closed out while you worked, its board line is now
in front of you — **read it before you write yours**, and never delete a line you did not add.

## Step 0.6 — Preflight: one call instead of ten (AUTOMATIC, never ask)

Run it before reading anything. It answers, mechanically, every question Steps 1–2 and 7–8 used to
answer by hand — and each of those has been silently wrong at least once:

```bash
python .agents/scripts/closeout_preflight.py --story <id> --project <PROJECT> --fetch \
       [--branch <name>] [--worktree <path>] [--require-gates suite,ruff,pyrefly]
```

It reports: did the code land on the epic branch · is every repo `0/0` and clean · are the registered
worktrees LIVE/LOST/HUSK · do both status surfaces agree · does the walkthrough carry a `Verdict:`
(with the pre-2026-08-02 standalone-file fallback) · is that verdict stale against HEAD · does the
story's **File List** still exist in the tree · is `active-context` inside budget · did the required
gates actually run at this commit · can the epic close.

**Exit 2 = BLOCKED — resolve before flipping anything. Exit 1 = warnings: read them, they do not
block.** A warning that says *"landing was NOT verified"* means exactly that — it is not a pass.
Paste the block into the close-out summary; it IS the evidence for Steps 1, 2, 7 and 8.

## Step 1 — Read current state & this session's artifacts (scoped — no needless whole-file reads)
1. `_bmad-output/active-context/active-context.md` — full (about to prune it).
2. `_bmad-output/implementation-artifacts/sprint-status.yaml` — **Grep THIS story's id; read only its epic block + line**, never all 400+ lines.
3. `_bmad-output/component-specs/` — names only; open one only when routing a learning into it (Step 3).
4. `_bmad-output/project-context.md` — ONLY if a learning looks app-wide (check for an existing rule first); else skip, its rules loaded at boot.
5. This session's `_artifacts/<YYYY-MM-DD>_<slug>/` — the TWO living docs: `implementation_plan.md` (carries `## Self-Audit`) + `walkthrough.md` (carries the `## Task Checklist` outline, `## Evidence`, `## Suite Ledger`, `## Code Review` with the verdict, and `## Your Actions` — everything close-out needs is in this ONE doc). **Skip anything already read THIS session.** **If `walkthrough.md` ends with a `## Close-Out Handoff` block** (autopilot Stage 4 writes one), that is the AUTHORITATIVE pre-routed learnings — Step 3 lifts it, no re-deriving.
6. **Cross-reference plan vs walkthrough** for plan-vs-built deltas — unless already surfaced this session.

Report: sprint objective, story status, plan-vs-walkthrough deltas, # known pitfalls.

## Step 2 — Verify the claimed work exists on disk (grep-check — NOT a code review)
**Step 0.6 already did the file-level half**: its `file-list` lines check every path the story CLAIMED
it changed against the tree — tracked ✅ / untracked-never-committed ⚠️ / absent ❌. Do not redo it by
hand; an `ERROR: claimed but ABSENT` there means the work was renamed or never landed, and it blocks.
What remains for you is the *semantic* half — that the named fix is actually present in those files.
Code-verify the story/task you just closed: grep its fix/feature in the files it touched, mark
`✅ Code-Verified` / `❌ Not Found` / `⚠️ Partial`. After an /autopilot run it's already tests-green +
QA-approved — a confirming grep is enough; don't re-run the suites. Only RE-verify a pre-existing
`## Active Tasks` entry if THIS session changed its files. Human-gated carryovers (pending live-QA / deploy)
can't be grep-advanced — leave as-is. Queue every `✅` to move to `## Completed Tasks`.

## Step 3 — Route each learning to the RIGHT home (the 4 homes)
**If `walkthrough.md` has a `## Close-Out Handoff` block, LIFT it:** its four sub-sections map 1:1 to the
four homes below — route each item to its tagged home. Pre-sorted by the doer, so
do NOT re-derive. **Only if there is NO such block** (a manual, non-autopilot session) categorize every
learning yourself:
- **New architecture rule / invariant (app-wide)** → `_bmad-output/project-context.md` (`## Critical Architecture Rules`)
- **New component pitfall / gotcha / failure mode** → `_bmad-output/component-specs/<spec>.md`
- **New bug discovered (still open)** → `active-context.md` (`## Active Tasks`)
- **Cross-session fact / recurring pitfall / Daniel preference (NOT component-scoped)** → a Claude
  auto-memory file **+ a one-line `MEMORY.md` pointer. Collect here; validated + written automatically in
  Step 6, no approval gate** (frontmatter spec there).

Append format for specs/rules: `- **YYYY-MM-DD**: [description]. (Source: session artifacts)`.

## Step 4 — Apply updates (specs / rules / active-context now; memory waits for Step 6)
- **Every active-context entry is BORN as a pointer — ≤3 lines: outcome · STILL-OWED · pointer** to where
  the record actually lives (the map in `/sudo-prune-context`). The narrative goes in `sprint-status.yaml`'s
  story line + the walkthrough, NEVER here — active-context POINTS at information, it does not restate it.
- **Completed tasks**: move `✅` items to `## Completed Tasks` with `- **Resolved:** YYYY-MM-DD` (pointer form).
- **Story-status → `done` (this command's PRIMARY purpose).** The operator invoking this **IS the
  sign-off** — **flip the just-closed story to `done` by default, without asking.** Do it with the
  script, never by hand-editing two files:

  ```bash
  python .agents/scripts/story_status.py set <id> done --project <PROJECT>
  ```

  It writes the story frontmatter **and** the board key in one operation **or neither** — the two
  surfaces drifted apart repeatedly when this was two manual edits (six stories were found drifted on
  2026-08-03 alone). It refuses a downgrade, refuses an unknown status, and refuses outright if the two
  surfaces already disagree — that case needs `--reconcile`, which is a decision, not a default.
  It prints `board X -> Y, frontmatter X -> Y`; echo that as `Closing <story>: review → done`.
  Idempotent: only `ready-for-dev`/`in-progress`/`review` advance; never downgrade.
  - **Gate evidence (advisory this sprint, hard after):** if the story recorded gate receipts, confirm
    them before the flip — `python .agents/scripts/gate_receipt.py check --story <id> --require
    <gates> --advisory`. A receipt proves the gate RAN, at which commit; prose cannot.
    ⏳ Remove `--advisory` at the close of the first full sprint after this landed (ruling 2026-08-02).
  - **ONLY objectively-red tests block the flip.** Read the **`Verdict: … @ <sha>`** line in the story
    walkthrough's `## Code Review` section (stories closed before 2026-08-02 keep the old standalone
    verdict — fall back to `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md` when the
    walkthrough has no such section). **FAIL** (a NEW regression or missing
    required tier — actually red) → do NOT flip; tell Daniel to fix via `/sudo-code-review`, then re-run.
    **Every other verdict closes it:** **PASS** → flip; **CONCERNS** → flip + record them; **WAIVED /
    missing / stale** (verdict on an old HEAD) → flip. Fail-open: a gate-read error never blocks close-out.
  - **No "leave it at review and ask" branch — never punt the flip back to Daniel.** A pending
    **live-test / live-verify / live-QA / live-checkride** or "stays review until X" note is NOT a blocker:
    his invocation resolves it. Flip and NOTE it (`note: pending live-test — closed on your invocation`).
    The red-tests **FAIL** is the only refusal.
  - **"commit owed" is NOT a blocker** — the agent commits its own work in the story worktree, and Step 7
    lands it. Nothing about git blocks the status flip.
- **Epic closure — do it in the SAME pass, never leave it to be noticed later.** An umbrella cannot
  close itself: when every child of this story's epic is terminal (`done`/`descoped`), the epic key is
  the only thing still holding it open, and a stale-open epic keeps recommending finished work.
  Step 0.6's `epic` line already answers this — `epic-N is 'X' but ALL n children are terminal - it can
  close now`. When it says that:
  1. diff `_bmad-output/planning-artifacts/epics.md` against the board keys 1:1 — a child that exists in
     one and not the other is the real finding, and it is NOT closeable yet;
  2. flip the epic key with `story_status.py set epic-N done --project <PROJECT>`;
  3. update the epic's status line in `epics.md` in the same edit — the two rot independently.
  **A pending live-verify / live-QA debt does NOT hold an epic open** — same rule as the story flip
  above. A `deferred` or `deferred-v3` child DOES: park it under a *deferred epic*, never as a parked
  row under a finished one, or the epic can never close.
- **Last Updated**: set to today's date at the top of `active-context.md`.
- **CHANGE LOG — `_bmad-output/history/CHANGELOG.md`, one entry per line, newest first** (Wave 4
  split, 2026-08-03: the log no longer lives in `sprint-status.yaml` — the pointer there says so).
  Add your entry as its own `#   YYYY-MM-DD (<story> <stage>): …` line directly under the CHANGE-LOG
  header block in THAT file. The board's real `last_updated:` key refreshes automatically when
  `story_status.py set` flips the story. ⛔ **Never re-join the log into one ` | `-separated line** —
  it was 29k characters on a single line, which made every concurrent close-out an unresolvable
  conflict. Distinct lines let two lanes merge. Keep your entry to what the board needs; the narrative
  belongs in the story's walkthrough. ⛔ **Never add a narrative note to the board row itself** — a
  non-terminal row may carry ≤120 chars; a terminal row carries NOTHING (`workflow_lint` errors on
  both, and the flip drops the old note automatically).

## Step 4.5 — Move the Jira ticket (AUTOMATIC, never ask)

The YAML just changed, so the story's Jira ticket must move with it. Read `jira_key:` from the story's
frontmatter and transition it to match the flip (`review` → `In Review`; a close-out to `done` →
`Done`), posting the gate evidence as a comment:
`acli jira workitem transition --key <KEY> --status "<Status>"` then
`acli jira workitem comment create --key <KEY> --body "<verdict line + walkthrough path @ sha>"`. Full acli reference: `.agents/rules/jira.md`.
If the story has no `jira_key` yet (pre-Jira story) or the project has no Jira project, note that in
the Step 6 summary and continue — never invent a key. *(The scrum-board map + its rebuild step were
retired 2026-08-07, SCC-13; `sprint-status.yaml` remains the machine state and Jira is the human view.)*

## Step 5 — Prune & budget → run `/sudo-prune-context` (AUTOMATIC, never ask)
Invoke **`/sudo-prune-context`** against the same `PROJECT_ROOT` (it inherits the binding — no
re-resolution). It applies unconditionally — the ONLY gate in THIS command stays Step 4's red-tests
check; everything else, incl. Step 6's memory write, just applies. Carry its report line
(`active-context: ~X / 5,000 tokens`) into Step 6's summary EVERY close-out.

## Step 6 — §5 artifacts, summary & manual catch
- Ensure this session's `_artifacts/<date>_<slug>/` has the single **`walkthrough.md`** with its
  sections per `artifacts-always-first` §5 — **`## Task Checklist`** (the outline), **`## Evidence`**,
  and **`## Your Actions`** (what landed — branch + commit range, per Step 7 — plus anything still on
  Daniel); story work also carries `## Suite Ledger` + the review's `## Code Review`. (Sections of the
  walkthrough, not separate files; ≤ 10 KB.)
- Print a **`Session save applied:`** summary — ✅ tasks moved to Completed, 🧠 learnings routed (→ file),
  🧹 stale pitfalls / old completed pruned.
- **Memory (AUTOMATIC — validate, cross-check, write; no approval gate):** for each candidate (Close-Out
  Handoff `→ Claude memory` bucket, or from Step 3), self-validate + write WITHOUT asking:
  1. **Valid to store?** A durable cross-session fact (recurring pitfall, architecture invariant, Daniel
     preference) — NOT a one-off, NOT already captured in Steps 3–4. Fails → drop it.
  2. **Cross-check existing memory.** Read `MEMORY.md` + any same-topic file. Already covered → UPDATE that
     file in place (no duplicate); CONTRADICTED → new learning wins, rewrite the stale file. NEW file only
     when nothing covers it.
  3. **Write it.** One fact per file (`name`/`description`/`metadata.type` frontmatter) + a one-line
     `MEMORY.md` pointer.
  - Report outcome: `🧠 Memory: wrote [name] (new) · updated [name]`, or `🧠 Memory: nothing cross-session
    — unchanged` (most sessions).
- **Then ask Daniel (always, separate from memory):** *"Saved the session updates. Any manual learnings, new bugs, or sprint-objective changes to add?"* Apply any additions.

## Step 7 — Land the story on the EPIC branch (the one sanctioned push)

**Daniel invoking this command IS the sign-off for this push.** Run it LAST, after Steps 1–6 wrote the board,
story file, and `active-context.md` — so those edits ride the story branch and land with it.

⚠️ **Several sibling worktrees live** (operator says so, `git worktree list` shows sibling story lanes, or
a LANDING RULE is posted on the board): STOP this solo flow — read `.agents/commands/sudo-merge-epic-workingtrees.md`
and follow IT end to end: it runs this command's close-out per story itself (fix → merge → land → flip
`done` → combined gate → prune ALL trees) in one shot; nothing returns here.

**Precondition — check FIRST.** `git rev-parse --abbrev-ref HEAD` must be a **`claude/*`** branch (inside the
story worktree). If HEAD is the epic branch or `main`, this story wasn't worked in a worktree — **do NOT land
it.** Report it and stop — never rescue it by committing in the shared checkout.

Then execute `git-policy.md` → **"The landing"**, inside the worktree: first commit the close-out edits —
EXPLICIT PATHS ONLY (board, story file, active-context, artifacts; `git diff --cached --stat` must show
ONLY this story's files), then merge `origin/epic/<JIRA-KEY>-<slug>` (CONFLICT → **STOP and report**; never force-push,
never blind-rebase), **then the MERGE GATE — prove the tree that ships, not the one ③ reviewed** (the solo
counterpart of `/sudo-merge-epic-workingtrees` Step 5's combined gate): run
`git diff --name-only <③-verdict suite SHA>..HEAD -- backend/ frontend/`.
- **Empty** → the merge changed no code under you (fast-forward / doc-only drift): ③'s green already
  describes this exact tree — inherit it, say `Merge gate: inherited ③ green @ <sha>`, and push.
- **Non-empty** → the epic branch moved code since ③'s run, so the merged tree has NEVER been tested: run the
  full suite of the touched stacks on it NOW (parallel flags; the conftest suite lock serializes the box) and
  paste totals into the walkthrough. **Red → STOP: no push, nothing lands** — the board/status flips from
  Steps 1–6 ride this branch, so a stopped landing publishes nothing. Report the failing tests + which
  epic-branch commits collided (`git log <suite-SHA>..origin/epic/<JIRA-KEY>-<slug> --oneline`); the fix is a follow-on
  on the branch, then re-gate.
Then `git push origin HEAD:epic/<JIRA-KEY>-<slug>` — THE landing.

⛔ **Do NOT push `claude/<JIRA-KEY>-<story-slug>` to origin.** The local branch is the rollback point and survives a
failed landing push intact. A story branch reaches origin **only** via `/sudo-park` — that is park's whole
purpose, and `/sudo-resume` reads the origin `claude/*` list to find in-flight work on a cold machine.
Pushing here made park redundant and filled that listing with landed-and-dead branches. If this story WAS
parked, its branch is already on origin and Step 8 deletes it there.

- **`main` is untouched.** Only Daniel, directly or via `/sudo-push-e2e`.
- **Report** the branch, the commit range that landed, and the epic-branch sha — same into the walkthrough's
  `## Your Actions` (Step 6).
- Landing push rejected (remote moved) → **STOP and report.** Re-sync and re-land, never force.
- **No shared-checkout reconcile is owed.** It stands on `main`, which moves only when the epic merges via
  `/sudo-push-e2e`. (The old Step 7b reconcile died with `main_debug` on 2026-08-07.)

## Step 8 — Prune the merged worktree & branches (AUTOMATIC)

Immediately after Step 7 landing succeeds:
1. Invoke `/sudo-close-workingtree <story-slug>` to verify the merge, remove the local worktree (`.claude/worktrees/<story-slug>`), and delete both the local and remote GitHub branches (`claude/<JIRA-KEY>-<story-slug>`).
2. Confirm both local disk and remote origin are clean.

Optional additional input: $ARGUMENTS

