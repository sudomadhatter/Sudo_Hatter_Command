---
IsArtifact: true
ArtifactMetadata:
  title: Task list — clean-bmad .agents conversion
  type: task_list
  date: 2026-06-24
---

# Task list — clean-bmad-workspace conversion (final snapshot)

- [x] Stage model-agnostic autopilot doc into master `.agents/workflows/` (B2)
- [x] Sync master toolkit into clean-bmad (A2)
- [x] Add 6 project rules + drop `git-closeout-commits` in `.agents/rules/` (A1+A5a)
- [x] Rewrite root `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` — generic + git rule (A3)
- [x] Rewrite `opencode.json` to `.agents/` paths (A4)
- [x] Retire old format: delete `.agent/`, `.claude/rules/`, collapse `.gemini/` (A5b) — 3 unique workflows preserved first
- [x] Point `_01_My` autopilot doc at master copy
- [x] Structural verification (C2) — all 6 checks ✓
- [x] Write `conversion-playbook.md` (C1)
- [x] Close-out: `walkthrough.md` + `task-list.md` + active-context/INDEX

## Deferred to Daniel (not blocking)
- [ ] Live opencode routing test (the real model-agnostic proof)
- [ ] Decide fate of the 3 preserved old workflows (promote / archive)
- [ ] Global git follow-up: never-commit as master default (2-line master edit, on go-ahead)
- [ ] Commit + push both repos (agents don't push — command in walkthrough)
