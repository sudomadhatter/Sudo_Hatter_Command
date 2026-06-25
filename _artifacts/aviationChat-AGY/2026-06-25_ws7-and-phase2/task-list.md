---
IsArtifact: true
ArtifactMetadata:
  title: "WS7 + aviationChat Phase 2 — task list (final)"
  type: task_list
  date: 2026-06-25
---

# Task list — final state

## Part A — WS7 (home base)
- [x] A1 — `-Root`/`-MapPath` added to master drift script; re-vendored to aviationChat (hash-matched)
- [x] A2 — `_docs/repo-map.md` generated + curated header (names all top-level incl. `Projects/` pointer)
- [x] A3 — home-base SessionStart hook wired to repo-map inject + drift (direct edit worked; no `.proposed`)
- [x] A4 — `_docs/repo-map.md` row added to AGENTS.md §4

## Artifact-location rule (Daniel, mid-session)
- [x] Moved session folder → `_artifacts/aviationChat-AGY/2026-06-25_ws7-and-phase2/`
- [x] Codified "artifacts go where you work from" in AGENTS.md §5/§7, workspace-standard, INDEX, memory + MEMORY.md

## Part B — aviationChat Phase 2
- [x] B1 — preserve-sweep (skills 0 unique, workflows reclassified, roster in project-context, gate captured)
- [x] Gate preserved → `.agents/rules/000-PLAN-FIRST-GATE.md` (`_opencode_artifacts`→`_artifacts`)
- [x] Repoint `.agent/`→`.agents/` — 96 files (live wiring + README + .gemini + deploy ignores)
- [x] Consolidate `_claude_artifacts/`+`_opencode_artifacts/`→`_artifacts/` — 25 files
- [x] Option A — repointed gate path in the 2 `_bmad/custom/*.toml` (0 residual; nothing else in `_bmad/` touched)
- [x] B3 — removed forked `.claude/rules/` (18 files)
- [x] B5 — fixed `pyrefly-paths.md` + `adk_file_formating.md` (→ in-repo `v3-prompt-architecture`)
- [x] Fixed 3 backend `# See: .agent/...` comment pointers → `.agents/` (comments only)
- [x] Deleted `.agent/` (1,059 files) — only `.agents/` remains
- [x] B7 — regenerated `docs/repo-map.md`; drift exit 0; GitNexus affected_count 0 / risk low

## Close-out
- [x] walkthrough.md (+ Your Actions, both repos)
- [x] task-list.md (this file)
- [x] home-base `_artifacts/INDEX.md` row + `_artifacts/_home/active-context.md` updated
- [ ] **Daniel:** commit home base · commit aviationChat · apply aviationChat `settings.json.proposed`

## Noted follow-ups (not done — out of this session's scope)
- `_docs/repo-map.md` in aviationChat is a stale secondary map (canonical is `docs/repo-map.md`).
- `agent-context-protocol.md` referenced by 2 backend docstrings exists in neither toolkit (pre-existing dead ref).
- `your-action-required.md` (deprecated artifact name) still referenced inside the 2 `_bmad/custom/*.toml`.
- Master `.agents/commands/*` at the home base may carry the same `_claude_artifacts`/`.agent/` staleness (re-vendor source).
