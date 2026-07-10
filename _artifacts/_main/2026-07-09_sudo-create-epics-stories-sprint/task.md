---
IsArtifact: true
ArtifactMetadata:
  type: task
  date: 2026-07-09
  slug: sudo-create-epics-stories-sprint
---

# Task Checklist — `/sudo-create-epics-stories-sprint` + doc sync

## Author (lobby master)
- [ ] `.agents/commands/sudo-create-epics-stories-sprint.md`
- [ ] `.agents/skills/sudo-create-epics-stories-sprint/SKILL.md`

## Sync (dry-run → real)
- [ ] Lobby `-WhatIf` preview → report
- [ ] Lobby real sync
- [ ] AGY_AVIATIONCHAT `-WhatIf` → real
- [ ] Fresh_Workspace_BMAD `-WhatIf` → real
- [ ] Gap check: `.agents/skills/<name>/` vendored into each project (hand-copy fallback if not)

## Doc
- [ ] Update `_my_resources/diagrams_guides/tea_testing/tea_testing_work_flows_sudo.md` §9/§10/§11 + mermaids

## Verify
- [ ] Command + SKILL + workflow present across all 3 repos
- [ ] `.claude/skills/<name>/SKILL.md` present in all 3
- [ ] Mermaid syntax validates
- [ ] Report per-surface counts

## Close-out
- [ ] walkthrough.md
