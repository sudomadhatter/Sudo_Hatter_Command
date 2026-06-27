---
IsArtifact: true
ArtifactMetadata:
  title: "Task list — unify command sync (todo item 2)"
  type: task_list
  date: 2026-06-27
  todo_item: 2
---

# Task list (final)

- [x] Rewrite `sync-agents.ps1` — global refresh + `platforms:` filter + per-surface purge + `-GlobalsOnly`/`-NoGlobals`
- [x] Tag 6 commands with `platforms:` frontmatter (5 claude-only, 1 opencode-only)
- [x] `sync-agents.md` — document one-command-all-surfaces
- [x] `slash_command_updating.md` — slim to `-GlobalsOnly` alias
- [x] `commands/INDEX.md` — sync line + platform convention
- [x] `_docs/workspace-standard.md` — new "Command sync & platform reach" subsection
- [x] `AGENTS.md` §4 tool-dirs row + §8 portability
- [x] Run `/sync-agents`; verify counts + platform filter both directions
- [x] Fix bug A — broken opencode junction → resilient per-cache skip-with-warning
- [x] Fix bug B — over-broad `^bmad-` preserve → check master-managed first
- [x] Close-out — INDEX row, walkthrough (with real output + Your Actions), this snapshot

## Pending (Daniel)
- [ ] Run the surgical commit (walkthrough → Your Actions #1)
- [ ] Restore/repoint the opencode junction target, then `/sync-agents -GlobalsOnly` + restart opencode (#2/#3)

## Out of scope → item 3 (fix clean-workspace mirroring)
- [ ] Re-vendor `.agents/` (new sync engine + tagged commands) into both projects
- [ ] Broken opencode junction is environmental — restore vs repoint is Daniel's call
