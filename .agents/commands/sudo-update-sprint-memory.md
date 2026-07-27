---
description: End-of-session / story close-out save — advance the closed story to done (running this command IS Daniel's sign-off; only objectively-red /sudo-code-review tests block the flip), code-verify, route learnings to specs/rules/memory, prune active-context, then LAND the story branch on main_debug (Step 7). Run LAST when closing a story or session.
platforms: [opencode, antigravity]
---

# /sudo-update-sprint-memory — Session End (close-out)

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
in the repo. So absorb the trunk FIRST, inside the worktree:

```bash
git fetch origin main_debug
git rev-list --count HEAD..origin/main_debug     # >0 → behind
git merge origin/main_debug                      # CONFLICT → STOP and report, never force
```

Echo `Base: current with origin/main_debug @ <sha>`. Step 7 re-merges as a cheap safety net; this one is
what makes the board edits land clean. If another lane closed out while you worked, its board line is now
in front of you — **read it before you write yours**, and never delete a line you did not add.

## Step 1 — Read current state & this session's artifacts (scoped — no needless whole-file reads)
1. `_bmad-output/active-context/active-context.md` — full (about to prune it).
2. `_bmad-output/implementation-artifacts/sprint-status.yaml` — **Grep THIS story's id; read only its epic block + line**, never all 400+ lines.
3. `_bmad-output/component-specs/` — names only; open one only when routing a learning into it (Step 3).
4. `_bmad-output/project-context.md` — ONLY if a learning looks app-wide (check for an existing rule first); else skip, its rules loaded at boot.
5. This session's `_artifacts/<YYYY-MM-DD>_<slug>/` — `implementation_plan.md` + `walkthrough.md` (checklist + actions are sections inside it). **Skip anything already read THIS session.** **If `walkthrough.md` ends with a `## Close-Out Handoff` block** (autopilot Stage 4 writes one), that is the AUTHORITATIVE pre-routed learnings — Step 3 lifts it, no re-deriving.
6. **Cross-reference plan vs walkthrough** for plan-vs-built deltas — unless already surfaced this session.

Report: sprint objective, story status, plan-vs-walkthrough deltas, # known pitfalls.

## Step 2 — Verify the claimed work exists on disk (grep-check — NOT a code review)
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
- **Story-status → `done` (this command's PRIMARY purpose).** Daniel invoking this **IS his sign-off** —
  **flip the just-closed story to `done` by default, without asking**, in BOTH the story file
  (`_bmad/bmm/stories/…` frontmatter) AND `sprint-status.yaml`. Print `Closing <story>: review → done`.
  Idempotent: only `ready-for-dev`/`in-progress`/`review` advance; never downgrade.
  - **ONLY objectively-red tests block the flip.** Read the verdict at
    `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`. **FAIL** (a NEW regression or missing
    required tier — actually red) → do NOT flip; tell Daniel to fix via `/sudo-code-review`, then re-run.
    **Every other verdict closes it:** **PASS** → flip; **CONCERNS** → flip + record them; **WAIVED /
    missing / stale** (verdict on an old HEAD) → flip. Fail-open: a gate-read error never blocks close-out.
  - **No "leave it at review and ask" branch — never punt the flip back to Daniel.** A pending
    **live-test / live-verify / live-QA / live-checkride** or "stays review until X" note is NOT a blocker:
    his invocation resolves it. Flip and NOTE it (`note: pending live-test — closed on your invocation`).
    The red-tests **FAIL** is the only refusal.
  - **"commit owed" is NOT a blocker** — the agent commits its own work in the story worktree, and Step 7
    lands it. Nothing about git blocks the status flip.
- **Last Updated**: set to today's date at the top of `active-context.md`.
- **`sprint-status.yaml` CHANGE LOG — one entry per line, newest first.** Add your entry as its own
  `#   YYYY-MM-DD (<story> <stage>): …` line directly under the CHANGE-LOG header block, and bump the
  `# last_updated:` date above it. ⛔ **Never re-join the log into one ` | `-separated line** — it was
  29k characters on a single line, which made every concurrent close-out an unresolvable conflict.
  Distinct lines let two lanes merge. Keep your entry to what the board needs; the narrative belongs in
  the story's walkthrough.

## Step 5 — Prune & budget → run `/sudo-prune-context` (AUTOMATIC, never ask)
Invoke **`/sudo-prune-context`** against the same `PROJECT_ROOT` (it inherits the binding — no
re-resolution). It applies unconditionally — the ONLY gate in THIS command stays Step 4's red-tests
check; everything else, incl. Step 6's memory write, just applies. Carry its report line
(`active-context: ~X / 5,000 tokens`) into Step 6's summary EVERY close-out.

## Step 6 — §5 artifacts, summary & manual catch
- Ensure this session's `_artifacts/<date>_<slug>/` has the single **`walkthrough.md`** ending with a
  **`## Task Checklist`** section (final task snapshot) and a **`## Your Actions`** section — what landed
  (branch + commit range, per Step 7) plus anything still on Daniel — per AGENTS.md §5. (Sections of the
  walkthrough, not separate files.)
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

## Step 7 — Land the story on `main_debug` (the one sanctioned push)

**Daniel invoking this command IS the sign-off for this push.** Run it LAST, after Steps 1–6 wrote the board,
story file, and `active-context.md` — so those edits ride the story branch and land with it.

**Precondition — check FIRST.** `git rev-parse --abbrev-ref HEAD` must be a **`claude/*`** branch (inside the
story worktree). If HEAD is `main_debug`/`main`, this story wasn't worked in a worktree — **do NOT land it.**
Report it and stop — never rescue it by committing in the shared checkout.

Then execute `git-policy.md` → **"The landing"**, inside the worktree: first commit the close-out edits —
EXPLICIT PATHS ONLY (board, story file, active-context, artifacts; `git diff --cached --stat` must show
ONLY this story's files), then merge `origin/main_debug` (CONFLICT → **STOP and report**; never force-push,
never blind-rebase), then `git push origin HEAD:main_debug`.

⛔ **Do NOT push `claude/<story-slug>` to origin.** The local branch is the rollback point and survives a
failed landing push intact. A story branch reaches origin **only** via `/sudo-park` — that is park's whole
purpose, and `/sudo-resume` reads the origin `claude/*` list to find in-flight work on a cold machine.
Pushing here made park redundant and filled that listing with landed-and-dead branches. If this story WAS
parked, its branch is already on origin and Step 8 deletes it there.

- **`main` is untouched.** Only Daniel, directly or via `/sudo-push-e2e`.
- **Report** the branch, the commit range that landed, and the `main_debug` sha — same into the walkthrough's
  `## Your Actions` (Step 6).
- Landing push rejected (remote moved) → **STOP and report.** Re-sync and re-land, never force.

### Step 7b — Reconcile the shared checkout (MANDATORY — the push does NOT do this)

`git push origin HEAD:main_debug` moves the remote and `origin/main_debug`; it leaves `refs/heads/main_debug`
— the branch checked out in `PROJECT_ROOT` — exactly where it was. Skip this and the shared tree falls **one
story behind per landing, forever**, until a `pull --ff-only` refuses on the board files Daniel edits there.
That is the single most common reason close-out "needs untangling every time". Run `git-policy.md`
→ **"Reconcile the shared checkout"** now, from `PROJECT_ROOT`:

1. `git -C "$ROOT" fetch origin`, then `git -C "$ROOT" rev-list --left-right --count main_debug...origin/main_debug`.
2. **`0 0`** → current, done. **ahead > 0** → real divergence, **STOP and report** (Daniel's call).
   **behind only** → fast-forward.
3. Dirty tree → `git stash push -m "pre-<slug>-land reconcile"` **first** (that dirt is somebody's in-flight
   work and the stash is its only copy), `git merge --ff-only origin/main_debug`, then `git stash pop`.
4. **`stash pop` conflict → STOP and report** the conflicted files and what each side wanted. Never
   `stash drop`, never `checkout --` over it to force the fast-forward through.
5. Confirm `--left-right --count` is `0 0` and the tree is clean, and **state that in the report** — an
   unverified reconcile is how this silently regresses.

⚠️ If the stash held edits to `sprint-status.yaml` / `active-context.md`, they were authored on the
pre-landing base: after popping, **verify BOTH intents survived** (your close-out AND theirs) rather than
trusting a clean pop — grep for a line you wrote and a line they wrote before moving on.

## Step 8 — Prune the merged worktree & branches (AUTOMATIC)

Immediately after Step 7 landing succeeds:
1. Invoke `/sudo-close-workingtree <story-slug>` to verify the merge, remove the local worktree (`.claude/worktrees/<story-slug>`), and delete both the local and remote GitHub branches (`claude/<story-slug>`).
2. Confirm both local disk and remote origin are clean.

Optional additional input: $ARGUMENTS

