---
IsArtifact: true
ArtifactMetadata:
  title: "Wire open_tasks/todo_list into 'pick up' + 'what's next' for all three workspaces"
  type: implementation_plan
  date: 2026-06-27
---

# Implementation Plan — open-tasks surfaced on "pick up" AND "what's next" (all three workspaces)

**Todo item:** `Projects/AGY_AVIATIONCHAT/_my_resources/_open_tasks/todo_list.md` item 1 —
*"add this file as something that gets included on the call 'pickup' for all three projects aviationChat,
clean-workspace and main."*

**Daniel's in-flight clarifications (this session):**
- Triggering it by literally saying **"pick up"** is fine (no SessionStart auto-load needed).
- **"what's next" must work too** — both triggers should surface the list.
- If a folder is missing, create it. (None are — see below.)
- fresh-workspace `_artifacts` is still a mess → that's **item 3**, out of scope here.

## Goal
Make the open-tasks list reliably surface for **where you work FROM**, via **two triggers**:
1. **"pick up"** — as part of the continuity brief (today it only reads `active-context.md`).
2. **"what's next" / "open tasks" / "what's left"** — the standalone routing trigger (already wired, verify).

Both READ-ONLY (Daniel's notes; cross-check vs live files).

## What I found (research, read-only)
- **All three workspaces already have the file** — nothing to create:
  | Workspace ("pick up" target) | open-tasks file (current path on disk) |
  |---|---|
  | **main** / home base | `_my_resources/open_tasks/todo_list.md` |
  | **aviationChat** (`Projects/AGY_AVIATIONCHAT`) | `_my_resources/`**`_open_tasks`**`/todo_list.md`  ⟵ underscore-prefixed, the odd one |
  | **clean-workspace** (`Projects/Fresh_Workspace_BMAD`) | `_my_resources/open_tasks/todo_list.md` |
  They are **distinct per-workspace lists**, not copies — so this is "each pickup surfaces its OWN list," consistent with the system's "where you work FROM" philosophy.
- **"what's next" is already wired** in all three: aviationChat `AGENTS.md` §6 row, clean-workspace `AGENTS.md` §6 row, and `router.md` row 20 (home base). It functions today.
- **"pick up" is NOT wired** to open-tasks anywhere — every PERSISTENCE section (`AGENTS.md` §7 home base / §9 projects) only points at `active-context.md`. **This is the actual gap.**
- The canonical sources never learned about open-tasks: `_docs/workspace-standard.md` (the persistence model + active-context section list + format checklist) and `.agents/templates/project-template/AGENTS.md` (no "what's next" row, persistence line omits it). That's why the 2026-06-25 standardization drifted — it patched routing rows but not the model/template.
- **Path inconsistency:** the 2026-06-25 INDEX row says aviationChat was `git mv`'d to `open_tasks/` (no underscore), but on disk it is now `_open_tasks/` (a later rename pass reintroduced the underscore). The other two use `open_tasks/`.

## Plan — three tiers (approve any subset)

### Tier 1 — CORE: wire "pick up" → open-tasks (delivers the literal ask)
1. **Root `AGENTS.md` §7 PERSISTENCE** (home base = "main") — add a line: on **"pick up"**, after the `active-context.md` brief, also read `_my_resources/open_tasks/todo_list.md` (+ any plan/PRP `.md` notes there) and include a one-line "what's queued"; **READ-ONLY**.
2. **`Projects/AGY_AVIATIONCHAT/AGENTS.md` §9 PERSISTENCE** — same line, path `_my_resources/_open_tasks/todo_list.md` (or `open_tasks/` if Tier 3 runs).
3. **`Projects/Fresh_Workspace_BMAD/AGENTS.md` §9 PERSISTENCE** — same line, path `_my_resources/open_tasks/todo_list.md`.

Wording added (tailored per path):
> - **"pick up" also surfaces open tasks:** after the `active-context.md` brief, read this workspace's `_my_resources/open_tasks/todo_list.md` (+ any plan/PRP `.md` notes alongside it) and add a one-line "what's queued." **READ-ONLY** — Daniel's notes; never edit; cross-check vs live files. (Same source the "what's next" routing row uses.)

### Tier 2 — DURABILITY: stop it from drifting + new projects inherit both triggers
4. **`.agents/templates/project-template/AGENTS.md`** — add a "What's next / open tasks" routing row, and extend the PERSISTENCE line to include open-tasks on pickup. (Every future clone gets both triggers.)
5. **`_docs/workspace-standard.md`** — document open-tasks in: the §9 PERSISTENCE description, the `active-context.md` numbered sections (PICK UP points at open-tasks), the "Supporting files every workspace carries" list, and the format checklist.

### Tier 3 — OPTIONAL (Daniel's call — touches protected `_my_resources/`): normalize the odd path
6. `git mv Projects/AGY_AVIATIONCHAT/_my_resources/_open_tasks  →  .../open_tasks` (matches the `open_tasks/` standard used by the other two + the 2026-06-25 decision), then update the one `_open_tasks` reference in that AGENTS.md §6 row. Makes all wiring reference an identical relative path. **Recommended** — but it renames a folder inside your protected personal area, so it only runs on your explicit OK.

## Files touched
| # | File | Tier | Change |
|---|---|---|---|
| 1 | `AGENTS.md` (root §7) | 1 | +pickup→open_tasks line |
| 2 | `Projects/AGY_AVIATIONCHAT/AGENTS.md` (§9) | 1 | +pickup→open_tasks line |
| 3 | `Projects/Fresh_Workspace_BMAD/AGENTS.md` (§9) | 1 | +pickup→open_tasks line |
| 4 | `.agents/templates/project-template/AGENTS.md` | 2 | +"what's next" routing row, +pickup line |
| 5 | `_docs/workspace-standard.md` | 2 | document open_tasks in the persistence model |
| 6 | `Projects/AGY_AVIATIONCHAT/_my_resources/_open_tasks/` → `open_tasks/` (+ §6 row) | 3 (opt) | `git mv` + ref update |

> Note: `router.md` row 20 already covers "what's next" at the lobby — **no change needed**. Project `AGENTS.md` §6 "what's next" rows already exist — verified, no change (except #6's ref if Tier 3 runs).

## Execution order
Tier 1 (#1→#3) → Tier 2 (#4→#5) → Tier 3 (#6, only if approved). All edits are small (1–3 lines); no code.

## Verification
- Grep each edited `AGENTS.md`/standard for the new pickup line; confirm path matches the file that exists on disk.
- Dry-run "pick up" mentally for each workspace: PERSISTENCE now names both `active-context.md` AND `open_tasks/todo_list.md`.
- Dry-run "what's next" for each: routing row resolves to an existing file.
- If Tier 3 runs: confirm `open_tasks/todo_list.md` exists post-`mv` and zero `_open_tasks` refs remain in aviationChat.
- Home-base maps: no repo-map drift expected (no new top-level dirs); spot-check.

## Open questions for you
- **A. Tier scope** — Core only (1–3), or Core + Durability (1–5)? I recommend **1–5** (otherwise it drifts again, exactly like the 2026-06-25 pass).
- **B. Tier 3 path normalization** — normalize aviationChat `_open_tasks` → `open_tasks`? I recommend **yes** (one uniform path), but it's your protected area, your call.

## Git
No commits by me. Each repo touched (home base; aviationChat `main_debug`; clean-workspace) gets its exact commit command in the closing `walkthrough.md` "Your Actions."
