# Implementation Plan — Standardize "What's Next" open-tasks check

**Date:** 2026-06-25
**Work from:** home base
**Status:** AWAITING APPROVAL

## Goal
Give every converted workspace the same "check what I'm doing" capability: a
`_my_resources/open_tasks/` folder holding Daniel's `todo_list.md` (+ any plan/PRP
notes), wired so that asking **"what's next?"** reads the open-tasks for **wherever
you're working FROM** — mirroring the existing artifacts "where you work from" rule.

## Decisions (locked with Daniel)
- **Trigger:** on-demand. No SessionStart hook. Wire router + each project `AGENTS.md`
  so "what's next / open tasks" reads that location, READ-ONLY.
- **aviationChat migration:** move the 5 existing notes from `_my_resources/_Open_Task/`
  into the standard `_my_resources/open_tasks/`. Show each move; nothing deleted blind.
- **Scope:** converted projects only — `aviationChat-AGY` + `clean-bmad-workspace`
  (+ home base, already done). Others get it when converted.

## The standard (what "same format" means)
```
<workspace>/_my_resources/open_tasks/
    todo_list.md        ← tasks to complete + open work (the canonical file)
    <slug>.md           ← optional plan/PRP notes (e.g. admin_graph_rag_update.md)
```
Rule everywhere: **READ-ONLY** for agents (Daniel's notes); always cross-check vs the
live project files for staleness.

## Changes

### 1. Home base — already compliant
- `_my_resources/open_tasks/todo_list.md` exists; router row exists. No change beyond
  confirming wording.

### 2. aviationChat-AGY  (`Projects/aviationChat-AGY/`)
- Create `_my_resources/open_tasks/`.
- **Move** these 5 files from `_my_resources/_Open_Task/` → `_my_resources/open_tasks/`:
  - `admin_graph_rag_update.md`
  - `looping_workflow_prp.md`
  - `production-readiness-audit.md`
  - `repo-map-auto-maintenance.md`
  - `sprint-dependency-map.md`
- Create/seed `open_tasks/todo_list.md` if none exists (skeleton: Todo list / Open Work).
- Remove the now-empty `_Open_Task/` dir.
- Add a "what's next / open tasks" row to its `AGENTS.md` routing table (READ-ONLY).

### 3. clean-bmad-workspace  (`Projects/clean-bmad-workspace/`)
- Create `_my_resources/open_tasks/todo_list.md` (skeleton).
- Add the same "what's next / open tasks" row to its `AGENTS.md` routing table.

### 4. Lobby router & docs (small wording)
- `router.md` row 20: clarify it resolves by **where you work from** (lobby →
  home-base `open_tasks/`; inside a project → that project's `open_tasks/`).
- Update the home-base memory note `[[my-resources-personal-area-protected]]` carve-out
  to name the standardized `_my_resources/open_tasks/` path across workspaces.

## Out of scope
- jetChat, B&L WorldWide, NEXGen Films, ingestion-Pipeline-AC, openCode (pending conversion).
- No SessionStart hook.

## Verify
- `open_tasks/todo_list.md` resolves at home base + both converted projects.
- Both project `AGENTS.md` files have the read-only open-tasks row.
- aviationChat `_Open_Task/` is gone; its 5 notes are intact under `open_tasks/`.

## Close-out
- `walkthrough.md` + `task-list.md` in this folder; append row to `_artifacts/INDEX.md`.
