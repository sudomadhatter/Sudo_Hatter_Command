---
description: Session boot / BMAD story pick-up — reads active-context + sprint-status, loads in-scope component specs, surfaces the next story and which sudo- command to run, confirms guardrails before work begins. Pairs with /sudo-update-sprint-memory (the close-out save).
---

# /sudo-boot-sprint-memory — Session Boot + Story Pick-Up (G1)

Self-contained — no external workflow file. Project-scoped: reads THIS repo's `_bmad-output/`.
Quick-start to ground yourself at the beginning of any session. This is the manual trigger for Guardrail G1.
Discovery only — after completion, **do NOT start coding; wait for Daniel's next instruction.**

## Step 1 — Read active context
Read `_bmad-output/active-context/active-context.md` and output a `<context>` block summarizing:
- **Sprint Objective** — what are we working on?
- **Stable** — what's tested and working (the "Do NOT Touch" set)?
- **Broken** — what's known-broken or in review?
- **In Play** — which files are currently being modified?
- **Pitfalls** — gotchas from recent bugs (`## Known V2 Pitfalls`).

## Step 2 — Load in-scope component specs
For each spec flagged in-scope (or implied by the sprint objective), read it from
`_bmad-output/component-specs/` and note its **Invariants** section. If none are flagged, say:
> "No component specs flagged in-scope. I'll load specs as needed based on what we work on."

## Step 2b — Sprint status & the next story (the story "pick up")
Read `_bmad-output/implementation-artifacts/sprint-status.yaml` (grep the epic blocks — don't dump all of
it). Report, compactly:
- **Story states** — counts by status (`ready-for-dev` / `in-progress` / `review` / `done`).
- **Next story to pick up** — the top `ready-for-dev` (or the current `in-progress`), with its file under
  `_bmad/bmm/stories/`.
- **Next command** — which `sudo-` step it needs: not-started → `/sudo-write-story-tests`; mid-dev →
  `/sudo-dev-story-tests`; built & awaiting review → `/sudo-code-review`; reviewed → `/sudo-update-sprint-memory`.
Read-only — cross-check against live files; never edit anything.

> **⛔ This is NOT the master "pick up."** The home-base `pick up` trigger (`AGENTS.md` §7 / `router.md`)
> is the continuity behavior for ALL work — code OR not (research, docs, routing). This step is the
> BMAD-story/sprint-scoped sibling and does NOT replace or modify it.

## Step 3 — Confirm guardrails active this session
- **G2** Component-spec compliance — check specs before modifying spec'd components.
- **G3** Targeted edits only — no full-file rewrites.
- **G5** Agent authority boundaries — each agent has a single responsibility.
- **G6** Firestore singleton — all access through `get_db()`.
- **G8** Research-first — read files before editing them.

## Step 4 — Ready
Say:
> "Context loaded. [Sprint objective]. [N in review / all clear]. Next: [story id] → run [sudo- command]. Ready — what's the plan?"
Then stop and wait. (Close the session later with `/sudo-update-sprint-memory`.)

Optional additional input: $ARGUMENTS
