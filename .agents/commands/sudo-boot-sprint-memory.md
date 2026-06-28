---
description: Session boot — reads active-context, loads in-scope component specs, confirms sprint state before work begins. Pairs with /update-sprint-context (the close-out save).
---

# /boot-sprint-context — Session Boot (G1)

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

## Step 3 — Confirm guardrails active this session
- **G2** Component-spec compliance — check specs before modifying spec'd components.
- **G3** Targeted edits only — no full-file rewrites.
- **G5** Agent authority boundaries — each agent has a single responsibility.
- **G6** Firestore singleton — all access through `get_db()`.
- **G8** Research-first — read files before editing them.

## Step 4 — Ready
Say:
> "Context loaded. [Sprint objective]. [N items in review / all clear]. Ready — what's the plan?"
Then stop and wait. (Close the session later with `/update-sprint-context`.)

Optional additional input: $ARGUMENTS
