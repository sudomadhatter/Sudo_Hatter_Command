# Implementation Plan — Command/Workflow Parity Sync

**Date:** 2026-06-26
**Scope:** lobby (Sudo_Hatter_Command) + Projects/clean-bmad-workspace + (read-only ref) Projects/aviationChat-AGY
**Status:** AWAITING APPROVAL — no files touched yet

## Goal (Daniel's decisions)
1. **clean-bmad = exact mirror of aviationchat** for commands + workflows.
2. **Full workflow backfill** into clean-bmad.
3. **Lobby = true superset** of all projects' commands.

## Root cause (what's going on)
The old `/1_ccps_boot-context` + `/1_ccps_update-active-context` are broken thin wrappers pointing at a
non-existent workflow file (`@.agent/workflows/1_ccps_*.md` — wrong path, file absent). aviationchat
already replaced them with the **self-contained** `/boot-sprint-context` + `/update-sprint-context`.
The lobby and clean-bmad never got that migration, so they carry the broken pair. aviationchat is canonical.

---

## Phase 1 — clean-bmad `.agents/` master (commands)
**ADD (copy verbatim from aviationchat `.agents/commands/`):**
- `1_update-maps.md`
- `autopilot_claude.md`
- `autopilot_opencode.md`
- `boot-sprint-context.md`
- `update-sprint-context.md`

**DELETE (broken / not in canonical):**
- `1_ccps_boot-context.md`
- `1_ccps_update-active-context.md`
- `sm.md`

Result: clean-bmad commands == aviationchat's 32-command set.

## Phase 2 — clean-bmad `.agents/` master (workflows)
**ADD 26 files** copied verbatim from aviationchat `.agents/workflows/` (the full backfill set), and
**overwrite `INDEX.md`** to match aviationchat's workflow INDEX. Result: clean-bmad workflows == aviationchat.

## Phase 3 — Lobby `.agents/` master (superset)
**ADD (copy from aviationchat):** `autopilot_claude.md`, `autopilot_opencode.md`,
`boot-sprint-context.md`, `update-sprint-context.md`.
**DELETE (broken):** `1_ccps_boot-context.md`, `1_ccps_update-active-context.md`.
**KEEP `sm.md`** (lobby is a command center; harmless superset extra — flagging, not removing).
Lobby workflows stay sparse by design (the new commands are self-contained or covered by
`autopilot_bmad_dev_loop.md`), so no new lobby workflow files.

## Phase 4 — Propagate to tool dirs (sync, don't hand-edit mirrors)
For **clean-bmad** and the **lobby**: run the canonical sync (`/sync-agents`, plus
`/slash_command_updating` for the opencode/Antigravity global caches) to push the edited `.agents/`
masters into `.claude/`, `.opencode/`, `.gemini/`, `.antigravity/`. This also purges known ghosts
(e.g. clean-bmad's `.claude/commands/1_live-user-QA-bugs.md` not in its master).

## Phase 5 — Docs & maps (the documentation update)
- `clean-bmad/.agents/commands/INDEX.md` + `workflows/INDEX.md` — regenerate to match new set.
- `lobby/.agents/commands/INDEX.md` + `workflows/INDEX.md` — add sprint-context + autopilot rows, drop ccps rows.
- `lobby/_docs/repo-map.md` — refresh any command/workflow counts/refs (via `/1_update-maps` linter).
- Grep both workspaces for lingering `1_ccps_` references in AGENTS.md / README / docs and fix.

## Phase 6 — Verify (core sync)
- Re-run the delta diffs: clean-bmad commands/workflows == aviationchat; lobby is superset.
- Confirm no dangling `1_ccps_` references remain anywhere in scope.

## Phase 7 — All-projects sweep (old commands + doc parity)
Check **every** workspace under `Projects/` (aviationChat-AGY, clean-bmad-workspace, jetChat-AGY,
ingestion-Pipeline-AC, B&L WorldWide, NEXGen Films, openCode) + the lobby:
- **Old/deprecated commands:** grep every `.agents/commands/` + mirror (`.claude`/`.opencode`/`.gemini`/
  `.antigravity`) for the retired `1_ccps_boot-context` / `1_ccps_update-active-context` (and any other
  dead `/` command files). Flag any project still carrying them; remove per Daniel's call.
- **Command documentation:** grep each workspace's docs that list `/` commands (INDEX.md files,
  AGENTS.md, README.md, repo-map.md, any `commands` tables) and confirm they match what's actually
  on disk — update stale entries.
- Report a per-project table (clean / had-old-commands / docs-fixed) before editing beyond the three
  core workspaces.

## Phase 8 — Refresh maps (run /1_update-maps)
Once Phases 1–7 land, run `/1_update-maps` for **main (lobby)**, **aviationChat-AGY**, and
**clean-bmad-workspace** so each repo-map + INDEX reflects the new command/workflow reality.

## Phase 9 — Final report
- Confirm parity + clean sweep + maps current across all three core workspaces.
- Report before any `git commit` (never auto-commit — Daniel's gate); hand off git commands.

## Caveats / things I'll watch
- Copied sprint-context/autopilot commands may carry aviationchat-specific prose; I'll scan for
  hardcoded aviationchat-only paths and neutralize if found (clean-bmad has its own `_bmad-output/`).
- Other projects (jetChat-AGY, ingestion-Pipeline-AC) are OUT of scope for this pass.
- `sm` removed from clean-bmad but kept in lobby — confirm that's acceptable.
