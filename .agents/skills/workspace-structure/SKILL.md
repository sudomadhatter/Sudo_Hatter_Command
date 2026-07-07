---
name: workspace-structure
description: "Files & folders organization strategy for this system. Use when creating, moving, renaming, reorganizing, or adding folders/files; scaffolding a new workspace; or deciding whether a folder needs an AGENTS.md vs an INDEX.md. This is the decision guide — the full spec is docs/workspace-standard.md."
---

# Workspace Structure — files & folders organization strategy

The **decision guide** for how folders and files are organized in this system — the quick "what goes where +
which control file" reference. The **full spec is `docs/workspace-standard.md`** (read it for the complete
model, the PATH CONTRACT, and examples). This skill is the routing/decision layer over it; do not duplicate its
content here.

## Tier model — which folders get a control file
| Tier | What | Gets |
|---|---|---|
| **1 — Floor** (work happens here) | workspace roots: the lobby, each `Projects/<name>/`, `_system/`, `_routing-canary/`, `.agents/` | full **`AGENTS.md`** (Map/Mission/Support + routing table) + 1-line `CLAUDE.md`/`GEMINI.md` adapters |
| **2 — Guarded infrastructure** | `_artifacts/`, `_my_resources/`, `docs/` | a short local-law **`AGENTS.md`** (~15 lines) + adapters, so the folder's special rules self-enforce |
| **3 — Leaf content** | everything else | **`INDEX.md`** only (inventory), or nothing |

## Reading-order rule
Entering any folder: **if it carries an `AGENTS.md`, read that FIRST** (the local law — how to act there); read
its `INDEX.md`/`README.md` only when you need the inventory. Only "special instruction" folders carry an
`AGENTS.md`; most don't — for those, `INDEX.md` is the map.

## Adapters
`CLAUDE.md` / `GEMINI.md` are **always one-line adapters** pointing to `AGENTS.md`. Nothing model-specific or
heavy in them — no GitNexus block, no rules. Keep them bare. GitNexus code-intel, if a repo has it, lives in its
own `docs/gitnexus.md` with a one-line pointer from `AGENTS.md` — never inline.

## Naming & artifact buckets
Dated `YYYY-MM-DD_<slug>.md`; versioned `_draft`/`_v2`/`_final`; artifacts go **where you work FROM** (the
`artifacts-always-first` rule owns the full bucket model). Full model → `docs/workspace-standard.md`.

## When you CHANGE the structure
Propagate structural changes to `Projects/Fresh_Workspace_BMAD/` — the living template new projects clone from —
so they inherit the current shape, not a stale one. See the `living-template-sync` rule: rules/toolkit ride
`/sync-agents`; front-door + structure changes are hand-mirrored.

## Full spec
`docs/workspace-standard.md` — the canonical, complete model.
