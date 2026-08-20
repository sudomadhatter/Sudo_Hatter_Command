---
description: Prune & budget a project's active-context + pitfalls — enforce the ≤20 KB (~5,000-token) context budget, compact still-live state to pointers, DELETE everything else (git is the undo), sweep stale pitfalls, and report `active-context: ~X / 5,000 tokens`. Invoked by /cicd-update-sprint-memory Step 5; also runnable standalone whenever boot feels heavy. Applies unconditionally — never asks.
---

# /cicd-prune-context — Prune & Budget the Active Context

The maintenance pass that keeps `/cicd-boot-sprint-memory` cheap. **Unconditional apply, never ask** —
active-context is project-scoped and reversible (history in `_artifacts/` + `_archive/` + git). This
command touches ONLY context files — never story status, never `sprint-status.yaml` story lines, never git.

## Step 0 — Resolve the target project
Bind the target per `.agents/rules/smh-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override → `.agents/active-project.txt` → else **STOP and ask** — never guess, never operate on the lobby.
(When `/cicd-update-sprint-memory` invokes this, `PROJECT_ROOT` is already bound — inherit it, don't
re-resolve.) Set `PROJECT_ROOT` and **echo exactly** `Target: Projects/<name>` before any work. Files:
`_bmad-output/active-context/active-context.md` + `known-pitfalls.md` beside it.

## The budget
- **`active-context.md` has a hard CONTEXT budget: ≤ 20 KB ≈ 5,000 tokens.** Lines are NOT the metric —
  context is. **Measure: file size in bytes ÷ 4**; report **`active-context: ~X / 5,000 tokens`** every
  run (the save carries this line into its Step 6 summary, and the door into its own). Over budget →
  prune **in this same pass**, one-in-one-out: adding an entry means compacting/archiving another.

## Prune = two moves — deletion is the normal outcome, not a failure
1. **Still-live state** → compact to a ≤3-line pointer (outcome · STILL-OWED · pointer), keep.
2. **Everything else** (stale, superseded, finished, recorded at its home) → **DELETE** — git history is
   the undo. Read the entry ONCE before cutting: a buried STILL-OWED obligation must survive as a
   pointer line (the 2026-07-13 OIDC-env loss is the cautionary case), and a standing ruling must live
   in memory/specs before its text dies here.

**`_archive/` is unmaintained COLD STORAGE, not a routing home** — append-only, zero upkeep, never a
mandatory copy step; checked (with git history) only when something feels previously solved.

## The map — route information to its ONE home; active-context only POINTS
- `sprint-status.yaml` story line → per-story ledger + dated history log
- `_artifacts/<epic>/<story>/walkthrough.md` → the story record: task outline + evidence +
  `## Code Review` (verdict + findings — follow-on seeds point here) + Your Actions
  (pre-2026-08-02 stories: verdicts in `sudo-code-review-<story>.md`)
- `component-specs/<spec>.md` → component pitfalls/contracts · `project-context.md` → app-wide rules
- `known-pitfalls.md` (beside active-context) → the V2 pitfall long-tail, **grep-scoped, never bulk-loaded**
- Claude auto-memory → cross-session facts + operator rulings · `_archive/` → pruned text

## The sweeps
- **Completed tasks > 5** → compact the oldest to pointer form if it isn't, then move it to `_archive/`.
- **Pitfall staleness** — pitfalls live in `known-pitfalls.md` (soft budget 60 KB). ALWAYS re-check entries
  touched this session. **Prune-on-touch:** a story that touches a pitfall's component MOVES that entry
  into the component spec. Run the FULL four-rule sweep only when over budget:
  1. Story dependency now `done` in sprint-status → **stale, remove**.
  2. "Degraded until Story Y" and Y is `done` → **stale, remove**.
  3. References a code pattern; grep it — gone → **stale, remove**.
  4. Permanent architectural invariant (e.g. "Firestore uses named DB") → **keep**.
- **Size caps**: component spec > 120 lines → keep 8 most-recent failure modes; `project-context.md`
  target 150 / hard cap 200 → group rules without losing meaning.
- **Normalize encoding** of any line you touch (no `â€"` mojibake — use real `—` `→` `⚠️`).

## Done
Report: the **`active-context: ~X / 5,000 tokens`** line, what was compacted vs deleted vs archived
(counts + one-liners), and any STILL-OWED pointers that survived a cut. Nothing else — status flips and
learnings routing belong to `/cicd-update-sprint-memory`, and git to `/cicd-close-story-merge-tree`.

Optional additional input: $ARGUMENTS
