---
description: Session boot / BMAD story pick-up — reads active-context + sprint-status, loads in-scope component specs, surfaces the next story and which sudo- command to run, confirms guardrails before work begins. Pairs with /sudo-update-sprint-memory (the close-out save).
platforms: [opencode, antigravity]
---

# /sudo-boot-sprint-memory — Session Boot + Story Pick-Up

Self-contained — no external workflow file. Project-scoped: reads THIS repo's `_bmad-output/`.
Quick-start to ground yourself at the beginning of any session.
Discovery only — after completion, **do NOT start coding; wait for Daniel's next instruction.**

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/sudo-target-resolution.md` **§ASK** + §BIND: self fast-path →
`$ARGUMENTS` override (this command is the normal place to set the session's active project) → else do
NOT silently reuse the pointer — **ASK Daniel** *"Active project is `<pointer, or none>`. Which project
this session?"* with the `Projects/` list (a project he already named in this chat counts — don't
re-ask). Never guess, never operate on the lobby. Set `PROJECT_ROOT` and **echo exactly**
`Target: Projects/<name>` before any work; every bare path below resolves under `PROJECT_ROOT`, and a
needed path missing there → STOP and say so.

## Step 1 — Read active context
Read `_bmad-output/active-context/active-context.md` and output a `<context>` block summarizing:
- **Sprint Objective** — what are we working on?
- **Stable** — what's tested and working (the "Do NOT Touch" set)?
- **Broken** — what's known-broken or in review?
- **In Play** — which files are currently being modified?
- **Pitfalls** — active-context only POINTS at them now: GREP `_bmad-output/active-context/known-pitfalls.md`
  for the next story's files/components and surface ONLY the matching entries — never bulk-load that file.

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
- **Worktree** — run `git worktree list` and report whether the next/in-play story already has a
  `claude/<story-slug>` tree (`worktree-per-story` → "Resuming"). If it does, say so with its path and branch
  (*"Story <id> → worktree open at `<path>` on `claude/<slug>` — the next `sudo-` step re-enters it, does not
  open a new one"*); the story file and red tests may live ONLY in that tree, so any resumed dev/review work
  must `cd` in first.
- **⚠️ No worktree is NOT proof of a fresh start — check the remote before you say so.** Worktrees are
  machine-local (`.claude/worktrees/` is not in the repo), and Daniel works one sprint across desktop,
  laptop, and mobile. Whenever `git worktree list` shows nothing for the next story, ALSO run
  `git ls-remote --heads origin 'refs/heads/claude/*'`. A `claude/<story-slug>` branch on origin means the
  step was already done on another machine — report it as **"exists on origin, not on this machine"** and
  point at `/sudo-resume` to re-create the working surface. Only when BOTH are empty may you say the next
  step opens a worktree at first edit.
Read-only — cross-check against live files; never edit anything.

> **⛔ This is NOT the master "pick up."** The home-base `pick up` trigger (`AGENTS.md` §7 / `router.md`)
> is the continuity behavior for ALL work — code OR not (research, docs, routing). This step is the
> BMAD-story/sprint-scoped sibling and does NOT replace or modify it.

## Step 3 — Confirm guardrails active this session
- **Component-spec compliance** — check specs before modifying spec'd components.
- **Targeted edits only** — no full-file rewrites.
- **Agent authority boundaries** — each agent has a single responsibility.
- **Shared-resource singleton** — one client per shared resource (DB / auth / cache), via the
  project's factory (per the constitution).
- **Research-first** — read files before editing them.

## Step 4 — Ready
Say:
> "Context loaded. [Sprint objective]. [N in review / all clear]. Next: [story id] → run [sudo- command]. Ready — what's the plan?"
Then stop and wait. (Close the session later with `/sudo-update-sprint-memory`.)

Optional additional input: $ARGUMENTS
