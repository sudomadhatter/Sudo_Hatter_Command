---
IsArtifact: true
ArtifactMetadata:
  title: Tier-2 local law — per-folder AGENTS.md + adapters for the infrastructure folders
  type: implementation_plan
  date: 2026-07-03
  status: PRE-APPROVED (Daniel, in chat — "no you are clear to just implement this")
---

# Implementation Plan — Tier-2 local law (folder-level AGENTS.md)

## Why (Daniel's ask)
Re-reading the folder-as-workspace transcript plan, we missed a layer: per-folder `AGENTS.md` files.
Agreed shape (proposed by Claude, approved by Daniel): NOT every folder — a **3-tier model**. The
mechanism that gives this teeth: Claude Code auto-attaches a nested `CLAUDE.md` the moment it touches
any file in that subtree (Codex: nested `AGENTS.md`; Gemini: hierarchical context files) — so a local
law + adapters gets **auto-injected at the point of contact**, no reliance on the model choosing to read.

## The tier model
| Tier | Folders | Gets |
|---|---|---|
| 1 — Floors (work happens) | root, projects, `_system/`, `_routing-canary/`, `.agents/` | Full `AGENTS.md` (already exists) |
| 2 — Guarded infrastructure | `_artifacts/`, `_my_resources/`, `docs/` | **NEW**: ~15-line local-law `AGENTS.md` + 1-line `CLAUDE.md`/`GEMINI.md` adapters |
| 3 — Leaf content | epic buckets, transcripts, diagrams | `INDEX.md` only — no AGENTS.md |

Plus ONE reading-order rule, codified once: *entering any folder — `AGENTS.md` first (how to act
here); `INDEX.md`/`README.md` only when you need the inventory.*

## Changes (lobby only this session; project rollout = follow-up)
1. **NEW** `_artifacts/{AGENTS,CLAUDE,GEMINI}.md` — law digest matches the 2026-07-03
   artifact-routing-fix state (epic_<E>/<story>/ nesting, tea/, _main/, one-doc walkthrough);
   points at README.md + INDEX.md header + artifacts-always-first.md as canon.
2. **NEW** `_my_resources/{AGENTS,CLAUDE,GEMINI}.md` — PROTECTED/read-only law + the one
   `/1_update-maps` `## Open Work` exception; points at README.md.
3. **NEW** `docs/{AGENTS,CLAUDE,GEMINI}.md` — what each doc is; AUTO-body regen-only law;
   docs/ is NOT synced by /sync-agents.
4. Root `AGENTS.md` §1 — add the reading-order item.
5. `docs/workspace-standard.md` — new "tier model" subsection in Part 1 + format-checklist row +
   PATH CONTRACT row.
6. `.agents/scripts/check_maps.py` — **check 8 (NON-FATAL hint)**: Tier-2 dirs present must carry
   AGENTS.md + both adapters; docstring 7→8. (Non-fatal so unconverted projects don't start failing.)
7. `.agents/workflows/1_update-maps.md` — fix stale "**six** checks" (line 64) → eight, incl. the new hint.
8. `_artifacts/README.md` rot fix — drop the abolished `task-list.md` row (one-doc rule), fix
   `_docs/`→`docs/` pointer.
9. Regen repo-map AUTO body (new files in scanned dirs) + `check_maps.py` verify clean.
10. `/sync-agents` — propagate the two toolkit edits (6+7) to all surfaces.
11. **Walkthrough deliverable (Daniel-directed):** update
    `_my_resources/diagrams_guides/system/file_folder_structure+maintaining.md` with the tier model,
    8-check linter, one-doc close (stale line 167), and the docs/ node fix (master-implementation-plan
    lives in `_my_resources/docs/`, not `docs/`). Explicitly authorized edit in the protected area.

## Out of scope (follow-ups, flagged in walkthrough)
- Per-project Tier-2 files + vendored `workspace-standard.md` refresh (docs/ is not synced — per-project pass).
- Converting the 4 non-workspace projects (JETCHAT, B-L, NEXGen, OpenChat).
- Promoting check 8 from hint → fatal conformance once all workspaces carry the files.

## Verification
- `python .agents/scripts/check_maps.py` (lobby) → exit 0, check-8 hint section clean.
- Temporarily rename one adapter → hint fires → restore (negative test).
- Adapters byte-pattern-identical to the root pattern (one front door per LLM).
