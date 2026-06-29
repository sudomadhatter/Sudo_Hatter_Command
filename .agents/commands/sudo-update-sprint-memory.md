---
description: End-of-session / story close-out save — advance the closed story to done (running this command IS Daniel's sign-off; only objectively-red /sudo-code-review tests block the flip), code-verify, route learnings to specs/rules/memory, prune active-context. Run as the LAST step when closing a story or any session.
platforms: [opencode, antigravity]
---

# /sudo-update-sprint-memory — Session End (G1 close-out)

Self-contained — no external workflow file. Project-scoped: targets THIS repo's `_bmad-output/`.
Run as the last step when closing a story (or any dev / brainstorm / research session).

> **Active-context holds STATE, not history.** Session narratives belong in
> `_artifacts/<date>_<slug>/walkthrough.md` + git — never in `active-context.md`. Durable cross-session
> facts belong in Claude's auto-memory. This command routes each learning to its correct home and keeps
> `active-context.md` small so `/sudo-boot-sprint-memory` stays cheap.

## Step 0 — Resolve the target project (FIRST — before any other step)
Run from the **command center** (the lobby), this close-out operates on exactly ONE child project under
`Projects/`, never the lobby itself. Resolve the target now:
0. **Self** — if the current repo already has `_bmad/bmm/config.yaml` and **no** `Projects/` subfolder,
   you are inside a project already: `PROJECT_ROOT = .`. Skip to the binding rule.
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is
   the target; consume that first token (the remainder is the real argument). Write the name alone into
   `_my_resources/active-project.txt` (overwrite) so later commands inherit it.
2. **Active pointer** — else read `_my_resources/active-project.txt`; if it names a folder under
   `Projects/`, use it (normally the same project you booted/built this session).
3. **Ask** — else STOP and ask Daniel *"Which project are we closing out? (e.g. AGY_AVIATIONCHAT)"* —
   never guess, never operate on the lobby.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

**Binding rule (applies to EVERY step below):** every "THIS repo", every `{project-root}`, and every bare
path (`_bmad-output/…`, `_bmad/…`, `_artifacts/…`, `sprint-status.yaml`, story files) resolves **under
`PROJECT_ROOT`**, never the lobby. The Claude auto-memory write in Step 6 is the ONE exception — it always
targets Daniel's global memory dir, not the project. If a needed project path is missing under
`PROJECT_ROOT`, STOP and say so.

## Step 1 — Read current state & this session's artifacts (scoped — don't read whole files you don't need whole)
Read:
1. `_bmad-output/active-context/active-context.md` — full (you're about to prune/edit it).
2. `_bmad-output/implementation-artifacts/sprint-status.yaml` — **Grep for THIS story's id + read only its epic block + line**, NOT all 400+ lines (that file is ~27k tokens; reading it whole is the single biggest waste in this command).
3. List `_bmad-output/component-specs/` — names only. Open a spec only when you have a learning to route into it (Step 3).
4. `_bmad-output/project-context.md` — open ONLY if a session learning looks app-wide (to check for an existing rule before adding one). Otherwise skip; its rules were loaded at boot.
5. This session's `_artifacts/<YYYY-MM-DD>_<slug>/` — `implementation_plan.md` and `walkthrough.md` (its `## Task Checklist` + `## Your Actions` are sections of it, not separate files). **Skip any artifact you already read earlier THIS session** (e.g. right after an /autopilot run the walkthrough + code-review are already in context — don't re-read them). **If `walkthrough.md` ends with a `## Close-Out Handoff` block** (autopilot Stage 4 writes one), that block is the AUTHORITATIVE, pre-routed list of this run's learnings — Step 3 lifts it instead of re-deriving.
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
**If `walkthrough.md` has a `## Close-Out Handoff` block, LIFT it:** its four sub-sections map 1:1 to the four
homes below — route each listed item to its tagged home (a sub-section that says `none` = nothing for that
home). The block is pre-sorted by the agent that did the work, so do NOT re-derive — the Step 2 code-verify is
enough. **Only if there is NO such block** (e.g. a manual, non-autopilot session) categorize every learning
yourself from the artifacts:
- **New architecture rule / invariant (app-wide)** → `_bmad-output/project-context.md` (`## Critical Architecture Rules`)
- **New component pitfall / gotcha / failure mode** → `_bmad-output/component-specs/<spec>.md`
- **New bug discovered (still open)** → `active-context.md` (`## Active Tasks`)
- **Cross-session fact / recurring pitfall / Daniel preference (NOT component-scoped)** → a Claude
  auto-memory file (one fact per file, with `name` / `description` / `metadata.type` frontmatter) **+ a
  one-line `MEMORY.md` pointer. Collect the candidates here; they are validated, cross-checked against
  existing memory, and written automatically in Step 6 — no approval gate.**

Append format for specs/rules: `- **YYYY-MM-DD**: [description]. (Source: session artifacts)`.

## Step 4 — Apply updates (specs / rules / active-context now; memory waits for Step 6)
- **Completed tasks**: move `✅` items to `## Completed Tasks` with `- **Resolved:** YYYY-MM-DD`.
- **Story-status → `done` (THE PRIMARY purpose of this command).** Daniel invoking this command **IS his
  sign-off that the story is done** — so for the story you just closed, **close it out: flip it to `done`
  by default, without asking** — in BOTH the story file (`_bmad/bmm/stories/…` frontmatter) AND
  `sprint-status.yaml`. Echo it: print `Closing <story>: review → done`. Idempotent: only
  `ready-for-dev`/`in-progress`/`review` advance to `done`; never downgrade a status.
  - **The ONLY thing that blocks the flip is objectively-red tests.** Read this story's verdict at
    `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`. **FAIL** (a NEW test regression or
    a missing required tier — tests are actually red) → do NOT flip; tell Daniel to run `/sudo-code-review`,
    fix the red, then re-run this command. **Every other verdict closes the story:** **PASS** → flip;
    **CONCERNS** → flip + record the concerns in the close-out summary; **WAIVED / missing** (no
    `sudo-tests.yaml` baseline, or the gate wasn't run) **/ stale** (verdict HEAD ref ≠ current HEAD) →
    flip (no gate to block on). Fail-open: a gate-read error never blocks close-out.
  - **Do NOT punt the flip back to Daniel — there is no "leave it at review and ask" branch.** If the
    story, its sprint-status note, or active-context mentions a pending **live-test / live-verify / live-QA
    / live-checkride** or "stays review until X", that is NOT a blocker here: Daniel running this command is
    the sign-off that resolves it. Flip anyway and just NOTE it in the close-out summary
    (`note: story flagged a pending live-test — closed on your invocation`). The red-tests **FAIL** above
    is the only refusal.
  - **"commit owed" is NOT a blocker.** Agents never commit, so almost every freshly-built story owes a
    commit; Daniel commits right after close-out. Flip to `done` anyway.
  - (This does NOT contradict /autopilot, which is autonomous and deliberately stops at `review` because no
    human is in the loop. `/sudo-update-sprint-memory` is Daniel-invoked — the human IS the loop — so it
    owns the `review → done` advance.)
- **Last Updated**: set to today's date at the top of `active-context.md`.

## Step 5 — Prune & cap (this is what keeps boot cheap) — AUTOMATIC, never ask
This whole step is an unconditional *apply* (same tier as Step 4): prune and cap **without asking**.
Active-context is project-scoped and reversible (history survives in `_artifacts/` + git), so there is
NO permission gate here. The ONLY gate in this command is the live-test story→done check (Step 4) —
everything else, including the memory write (Step 6), just applies.
- **`active-context.md` hard cap ≈ 250 lines of LIVE state.** If history has crept in, move it to
  `_artifacts/<date>_<slug>/walkthrough.md` / git — do not keep narrative logs here.
- **Completed tasks > 5** → delete the oldest (history lives in `_artifacts/` + git).
- **Pitfall staleness** — ALWAYS re-check the pitfalls you added/touched this session. Run the FULL
  staleness sweep over EVERY `## Known V2 Pitfalls` entry ONLY when `active-context.md` is over its
  ~250-line cap (that grep-per-entry pass is expensive and mostly returns "keep", so it only earns its
  cost when the file actually needs trimming). For each entry checked:
  1. References a story dependency and that story is `done` in sprint-status → **stale, remove**.
  2. Describes a temporary degraded state ("degraded until Story Y") and Y is `done` → **stale, remove**.
  3. References a code pattern; grep it — if the pattern no longer exists → **stale, remove**.
  4. Permanent architectural invariant (e.g. "Firestore uses named DB") → **keep**.
- **Size caps**: component spec > 120 lines → keep 8 most-recent failure modes; `project-context.md`
  target 150 / hard cap 200 → compress by grouping rules without losing meaning.
- **Normalize encoding** of any line you touch (no `â€"` mojibake — use real `—` `→` `⚠️`).

## Step 6 — §5 artifacts, summary & manual catch
- Ensure this session's `_artifacts/<date>_<slug>/` has the single **`walkthrough.md`** ending with a
  **`## Task Checklist`** section (final task snapshot) and a **`## Your Actions`** section (manual steps +
  the exact `git` command — agents never commit), per AGENTS.md §5. (There is no separate `task-list.md`
  or `your-action-required.md` — both are sections of the walkthrough.)
- Print a summary:
  > **Session save applied:**
  > - ✅ Moved to Completed: [tasks]
  > - 🧠 Learnings: [rule/pitfall] → [file]
  > - 🧹 Pruned: [stale pitfalls / old completed]
- **Memory (AUTOMATIC — validate, cross-check, write; no approval gate):** For each candidate (from the
  Close-Out Handoff `→ Claude memory` bucket, or one you derived in Step 3), self-validate and write it
  WITHOUT asking. Run this check per candidate:
  1. **Valid to store?** It must be a durable, cross-session fact — a recurring pitfall, an architecture
     invariant, or a Daniel preference — NOT a one-off detail of this story and NOT something already
     captured in a spec / rule / active-context in Steps 3–4. If it fails this, drop it (don't write).
  2. **Cross-check against existing memory.** Read `MEMORY.md` and any same-topic memory file. If a memory
     already covers this fact, UPDATE that file in place (don't duplicate); if the new learning CONTRADICTS
     an existing memory, the new one wins — rewrite the stale file to match reality. Only create a NEW file
     when nothing existing covers it.
  3. **Write it.** One fact per file with `name` / `description` / `metadata.type` frontmatter + a one-line
     `MEMORY.md` pointer. New file → add the pointer; updated file → leave/refresh its pointer; superseded
     file → keep its single pointer line accurate.
  - **If there are zero valid candidates,** print `🧠 Memory: nothing cross-session this session — unchanged`
    and move on. (This is MOST sessions — project learnings already routed to specs / active-context / rules
    in Steps 3–4; memory is only for durable, non-component facts.)
  - In the summary, list what was written/updated, e.g. `🧠 Memory: wrote [name] (new) · updated [name]
    (superseded stale entry)`.
- **Then ask Daniel (always, separate from memory):** *"Saved the session updates from the codebase +
  artifacts. Any manual learnings, new bugs, or sprint-objective changes to add?"* Apply any additions. Done.

Optional additional input: $ARGUMENTS
