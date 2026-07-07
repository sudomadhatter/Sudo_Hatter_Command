---
name: living-template-sync
description: "Fresh_Workspace_BMAD is the LIVING TEMPLATE new projects are cloned from. `/sync-agents` (lobby) auto-flags when Fresh's front-door pattern has drifted; this rule is how to RECONCILE it. Rule/toolkit edits ride /sync-agents automatically; front-door + structure changes are per-workspace (NOT synced) and must be hand-mirrored into Fresh, kept generic."
activation: On demand — when /sync-agents flags Fresh drift, or you change the front-door / structure pattern
---

# Living Template — keep Fresh_Workspace_BMAD current

**`Projects/Fresh_Workspace_BMAD/` is the golden skeleton** cloned + renamed to start every new project. If it
drifts behind the home base, every new project starts stale. Keeping it current is a standing obligation.

## Detection is automated
`/sync-agents` (on a lobby sync) runs a **Fresh drift-check** and warns when Fresh's front-door pattern lags —
missing `docs/gitnexus.md`, `AGENTS.md` missing the reading-order rule or still inlining a GitNexus block, or
`docs/workspace-standard.md` differing from the lobby canon. **You don't have to remember to look — the tool
tells you.** This rule is what to DO about it.

## What propagates how
1. **Rules + toolkit (`.agents/**`) → automatic.** `/sync-agents` additively vendors `.agents/` into every
   project incl. Fresh. Nothing to hand-do.
2. **Front-door + structure (root `AGENTS.md` / adapters / `INDEX.md`, `docs/`, folder layout) → hand-mirror
   into Fresh.** These are per-workspace content, so a blind copy would wipe the skeleton. Adapt to the
   skeleton: keep generic (no product specifics), `<PROJECT_NAME>` placeholders where a real project fills in.
3. **Verify clone-readiness.** A clone + rename of Fresh should need only placeholder fills — never structural
   setup. Re-run `/sync-agents`; the drift-check should come back clean.

## Why
Any rule or structure change at the home base must also land in Fresh — the living/evolving workflow for new
projects — so new projects are never set up from scratch.
