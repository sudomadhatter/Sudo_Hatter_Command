---
description: End-of-session / story close-out save — advance the closed story to done (gated only on explicit live-test notes), code-verify, route learnings to specs/rules/memory, prune active-context. Run as the LAST step when closing a story or any session.
---

# /update-sprint-context — Session End (G1 close-out)

Self-contained — no external workflow file. Project-scoped: targets THIS repo's `_bmad-output/`.
Run as the last step when closing a story (or any dev / brainstorm / research session).

> **Active-context holds STATE, not history.** Session narratives belong in
> `_artifacts/<date>_<slug>/walkthrough.md` + git — never in `active-context.md`. Durable cross-session
> facts belong in Claude's auto-memory. This command routes each learning to its correct home and keeps
> `active-context.md` small so `/boot-sprint-context` stays cheap.

## Step 1 — Read current state & this session's artifacts (scoped — don't read whole files you don't need whole)
Read:
1. `_bmad-output/active-context/active-context.md` — full (you're about to prune/edit it).
2. `_bmad-output/implementation-artifacts/sprint-status.yaml` — **Grep for THIS story's id + read only its epic block + line**, NOT all 400+ lines (that file is ~27k tokens; reading it whole is the single biggest waste in this command).
3. List `_bmad-output/component-specs/` — names only. Open a spec only when you have a learning to route into it (Step 3).
4. `_bmad-output/project-context.md` — open ONLY if a session learning looks app-wide (to check for an existing rule before adding one). Otherwise skip; its rules were loaded at boot.
5. This session's `_artifacts/<YYYY-MM-DD>_<slug>/` — `implementation_plan.md`, `walkthrough.md`, `task-list.md`. **Skip any artifact you already read earlier THIS session** (e.g. right after an /autopilot run the walkthrough + code-review are already in context — don't re-read them).
6. **Cross-reference `implementation_plan.md` vs `walkthrough.md`** for plan-vs-built deltas — unless you already surfaced those deltas this session.

Report: sprint objective, this story's status, plan-vs-walkthrough deltas, # known pitfalls.

## Step 2 — Code-verify THIS session's work (not the whole backlog)
Code-verify the story/task you just closed: grep for its described fix/feature in the files it touched,
mark `✅ Code-Verified` / `❌ Not Found` / `⚠️ Partial`. After an /autopilot run this is already
tests-green + QA-approved — a quick confirming grep is enough; do NOT re-run the suites.
Only RE-verify a pre-existing `## Active Tasks` entry if THIS session changed its files. Human-gated
carryovers (pending live-QA / deploy) can't be advanced by a grep — leave them as-is. Queue every `✅`
to move to `## Completed Tasks`.

## Step 3 — Route each learning to the RIGHT home (the 4 homes)
Categorize every learning from the session and send it to exactly one home:
- **New architecture rule / invariant (app-wide)** → `_bmad-output/project-context.md` (`## Critical Architecture Rules`)
- **New component pitfall / gotcha / failure mode** → `_bmad-output/component-specs/<spec>.md`
- **New bug discovered (still open)** → `active-context.md` (`## Active Tasks`)
- **Cross-session fact / recurring pitfall / Daniel preference (NOT component-scoped)** → **PROPOSE** a
  Claude auto-memory file (one fact per file, with `name` / `description` / `metadata.type` frontmatter)
  **+ a one-line `MEMORY.md` pointer. Do NOT write memory yet — list the proposals and write only after
  Daniel says OK in Step 6.**

Append format for specs/rules: `- **YYYY-MM-DD**: [description]. (Source: session artifacts)`.

## Step 4 — Apply updates (specs / rules / active-context now; memory waits for Step 6)
- **Completed tasks**: move `✅` items to `## Completed Tasks` with `- **Resolved:** YYYY-MM-DD`.
- **Story-status → `done` (a PRIMARY purpose of this command).** For the story you just closed, flip it
  to `done` in BOTH the story file (`_bmad/bmm/stories/…` frontmatter) AND `sprint-status.yaml` — by
  DEFAULT, without asking. Idempotent: only `ready-for-dev`/`in-progress`/`review` advance to `done`;
  never downgrade a status.
  - **"commit owed" is NOT a blocker.** Agents never commit, so almost every freshly-built story owes a
    commit; Daniel commits right after close-out. Flip to `done` anyway.
  - **GATE — pause and double-check with Daniel BEFORE flipping** only when the story / its sprint-status
    note / active-context carries an explicit *"not done yet"* signal: a pending or DEFERRED
    **live-test / live-verify / live-QA / manual-pass / live-checkride**, an `OPEN (Daniel, live-only)`
    item, `await Daniel`, "I need to test it", or an explicit "stays review until X". Then leave the
    status as-is and ask; flip only on Daniel's OK.
  - (This does NOT contradict /autopilot, which is autonomous and deliberately stops at `review`.
    `/update-sprint-context` is Daniel-invoked, so it owns the `review → done` advance.)
- **Last Updated**: set to today's date at the top of `active-context.md`.

## Step 5 — Prune & cap (this is what keeps boot cheap)
- **`active-context.md` hard cap ≈ 150 lines of LIVE state.** If history has crept in, move it to
  `_artifacts/<date>_<slug>/walkthrough.md` / git — do not keep narrative logs here.
- **Completed tasks > 5** → delete the oldest (history lives in `_artifacts/` + git).
- **Pitfall staleness** — ALWAYS re-check the pitfalls you added/touched this session. Run the FULL
  staleness sweep over EVERY `## Known V2 Pitfalls` entry ONLY when `active-context.md` is over its
  ~150-line cap (that grep-per-entry pass is expensive and mostly returns "keep", so it only earns its
  cost when the file actually needs trimming). For each entry checked:
  1. References a story dependency and that story is `done` in sprint-status → **stale, remove**.
  2. Describes a temporary degraded state ("degraded until Story Y") and Y is `done` → **stale, remove**.
  3. References a code pattern; grep it — if the pattern no longer exists → **stale, remove**.
  4. Permanent architectural invariant (e.g. "Firestore uses named DB") → **keep**.
- **Size caps**: component spec > 120 lines → keep 8 most-recent failure modes; `project-context.md`
  target 150 / hard cap 200 → compress by grouping rules without losing meaning.
- **Normalize encoding** of any line you touch (no `â€"` mojibake — use real `—` `→` `⚠️`).

## Step 6 — §5 artifacts, summary & manual catch
- Ensure this session's `_artifacts/<date>_<slug>/` has **`walkthrough.md`** (with a **"Your Actions"**
  section: manual steps + the exact `git` command — agents never commit) and a **`task-list.md`** snapshot,
  per AGENTS.md §5. (There is no `your-action-required.md`.)
- Print a summary:
  > **Session save applied:**
  > - ✅ Moved to Completed: [tasks]
  > - 🧠 Learnings: [rule/pitfall] → [file]
  > - 🧹 Pruned: [stale pitfalls / old completed]
  > - 🧠 Memory proposed (awaiting OK): [name → one-line]
- **Ask Daniel:** *"Saved the session updates from the codebase + artifacts. Any manual learnings, new
  bugs, or sprint-objective changes — and shall I write the proposed memory file(s)?"*
  Apply any additions; write the approved memory files (+ `MEMORY.md` pointers). Otherwise the save is done.

Optional additional input: $ARGUMENTS
