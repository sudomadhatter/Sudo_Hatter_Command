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
`Projects/`, never the lobby itself:
0. **Self (sub-project fast path — check FIRST, STOP here if it matches)** — this repo has **no**
   `Projects/` subfolder → you ARE the project: `PROJECT_ROOT = .`, skip to the binding rule. Don't read
   `active-project.txt`, parse `$ARGUMENTS` for a project, or ask — cases 1–3 are command-center-only.
1. **Inline override** — `$ARGUMENTS` begins with a folder name under `Projects/` → that's the target;
   consume the token, write the name alone into `.agents/active-project.txt` (overwrite).
2. **Active pointer** — else use `.agents/active-project.txt` if it names a folder under `Projects/`.
3. **Ask** — else STOP and ask Daniel *"Which project are we closing out? (e.g. AGY_AVIATIONCHAT)"* —
   never guess, never operate on the lobby.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

**Binding rule (EVERY step below):** every "THIS repo", `{project-root}`, and bare path (`_bmad-output/…`,
`_bmad/…`, `_artifacts/…`, `sprint-status.yaml`, story files) resolves **under `PROJECT_ROOT`**, never the
lobby. ONE exception: Step 6's Claude auto-memory write always targets Daniel's global memory dir. A needed
project path missing under `PROJECT_ROOT` → STOP and say so.

## Step 1 — Read current state & this session's artifacts (scoped — don't read whole files you don't need whole)
1. `_bmad-output/active-context/active-context.md` — full (you're about to prune/edit it).
2. `_bmad-output/implementation-artifacts/sprint-status.yaml` — **Grep THIS story's id; read only its epic block + line**, never all 400+ lines (~27k tokens — whole-file reads are this command's biggest waste).
3. `_bmad-output/component-specs/` — names only; open a spec only when routing a learning into it (Step 3).
4. `_bmad-output/project-context.md` — ONLY if a learning looks app-wide (check for an existing rule first). Otherwise skip; its rules were loaded at boot.
5. This session's `_artifacts/<YYYY-MM-DD>_<slug>/` — `implementation_plan.md` + `walkthrough.md` (its `## Task Checklist` + `## Your Actions` are sections of it, not separate files). **Skip anything already read THIS session** (post-/autopilot the walkthrough + code-review are already in context). **If `walkthrough.md` ends with a `## Close-Out Handoff` block** (autopilot Stage 4 writes one), it is the AUTHORITATIVE pre-routed learnings list — Step 3 lifts it instead of re-deriving.
6. **Cross-reference plan vs walkthrough** for plan-vs-built deltas — unless already surfaced this session.

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
  sign-off that the story is done** — **flip the just-closed story to `done` by default, without asking**,
  in BOTH the story file (`_bmad/bmm/stories/…` frontmatter) AND `sprint-status.yaml`. Print
  `Closing <story>: review → done`. Idempotent: only `ready-for-dev`/`in-progress`/`review` advance;
  never downgrade.
  - **ONLY objectively-red tests block the flip.** Read the verdict at
    `_bmad-output/implementation-artifacts/sudo-code-review-<story>.md`. **FAIL** (a NEW regression or a
    missing required tier — tests actually red) → do NOT flip; tell Daniel to fix the red via
    `/sudo-code-review`, then re-run this. **Every other verdict closes it:** **PASS** → flip;
    **CONCERNS** → flip + record them in the summary; **WAIVED / missing** (no baseline / gate not run)
    **/ stale** (verdict HEAD ≠ current HEAD) → flip. Fail-open: a gate-read error never blocks close-out.
  - **No "leave it at review and ask" branch — never punt the flip back to Daniel.** A pending
    **live-test / live-verify / live-QA / live-checkride** or "stays review until X" note is NOT a blocker:
    his invocation resolves it. Flip and NOTE it (`note: story flagged a pending live-test — closed on your
    invocation`). The red-tests **FAIL** is the only refusal.
  - **"commit owed" is NOT a blocker** — agents never commit; Daniel commits right after close-out.
  - (No conflict with /autopilot: it's autonomous, so it deliberately stops at `review`; here the human IS
    the loop, so this command owns `review → done`.)
- **Last Updated**: set to today's date at the top of `active-context.md`.

## Step 5 — Prune & cap (this is what keeps boot cheap) — AUTOMATIC, never ask
Unconditional *apply* (same tier as Step 4), **without asking** — active-context is project-scoped and
reversible (history survives in `_artifacts/` + git), so NO permission gate here. The ONLY gate in this
command is Step 4's red-tests check; everything else, including Step 6's memory write, just applies.
- **`active-context.md` hard cap ≈ 250 lines of LIVE state** — move crept-in history to
  `_artifacts/<date>_<slug>/walkthrough.md` / git; no narrative logs here.
- **Completed tasks > 5** → delete the oldest.
- **Pitfall staleness** — ALWAYS re-check pitfalls you added/touched this session. Run the FULL sweep over
  EVERY `## Known V2 Pitfalls` entry ONLY when over the ~250-line cap (the grep-per-entry pass is expensive
  and mostly returns "keep"). Per entry checked:
  1. Story dependency now `done` in sprint-status → **stale, remove**.
  2. "Degraded until Story Y" and Y is `done` → **stale, remove**.
  3. References a code pattern; grep it — gone → **stale, remove**.
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
- **Memory (AUTOMATIC — validate, cross-check, write; no approval gate):** for each candidate (Close-Out
  Handoff `→ Claude memory` bucket, or derived in Step 3), self-validate and write WITHOUT asking:
  1. **Valid to store?** A durable, cross-session fact — recurring pitfall, architecture invariant, or
     Daniel preference — NOT a one-off story detail, NOT already captured in Steps 3–4. Fails → drop it.
  2. **Cross-check existing memory.** Read `MEMORY.md` + any same-topic file. Already covered → UPDATE
     that file in place (no duplicate); CONTRADICTED → the new learning wins, rewrite the stale file.
     Only create a NEW file when nothing covers it.
  3. **Write it.** One fact per file (`name` / `description` / `metadata.type` frontmatter) + a one-line
     `MEMORY.md` pointer — added, refreshed, or kept accurate per case.
  - **Zero valid candidates** → print `🧠 Memory: nothing cross-session this session — unchanged` (MOST
    sessions — project learnings already routed in Steps 3–4; memory is only durable non-component facts).
  - Summary lists writes, e.g. `🧠 Memory: wrote [name] (new) · updated [name] (superseded stale entry)`.
- **Then ask Daniel (always, separate from memory):** *"Saved the session updates from the codebase +
  artifacts. Any manual learnings, new bugs, or sprint-objective changes to add?"* Apply any additions. Done.

Optional additional input: $ARGUMENTS
