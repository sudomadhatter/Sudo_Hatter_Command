---
title: Task list snapshot — clean-bmad quick-start skeleton reshape
type: task-list
date: 2026-06-25
---

# Final TodoWrite snapshot

- [x] **WS1** — Re-cast AGENTS.md identity (aviationChat app → AGY quick-start skeleton); keep 9-section routing
- [x] **WS2** — Rewrite README.md to the real structure + sharpen the quick-start flow
- [x] **WS5** — Genericize residual placeholders (project-context.md dead `.agent/` refs; keep `{{tokens}}`)
- [x] **WS7** — `check-repo-map-drift.ps1` built + tested; SessionStart hook = hand-off (auto-mode blocked the
  agent self-editing `.claude/settings.json`); full config saved as `settings.json.proposed`
- [x] **WS4** — Verify stack kept (untouched); skills-registry reviewed (generic/stack-aligned, left as-is)
- [x] **WS3** — Regenerate `docs/repo-map.md` auto body + rewrite curated header
- [x] **WS6** — Update `router.md` row + `active-context.md` + `INDEX.md` + `walkthrough.md` + this `task-list.md`
  + memory

## Not done by the agent (by design)
- [ ] **Apply the SessionStart hook** — Daniel copies `settings.json.proposed` over `.claude/settings.json`
  (auto-mode guardrail on startup config).
- [ ] **Commit + push** clean-bmad + home-base — git-policy (commands in `walkthrough.md`).

## Deferred follow-ups (separate sessions)
- [ ] Promote `check-repo-map-drift.ps1` → master `.agents/scripts/` + wire the home-base hook.
- [ ] Prune aviationChat skills from the vendored `.agents/` set (master sync profile + `/sync-agents`).
- [ ] `_claude_artifacts/` full retirement (master pass; check autopilot `$RepoRoot`).
