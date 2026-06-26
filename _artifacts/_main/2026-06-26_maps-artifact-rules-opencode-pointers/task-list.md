---
IsArtifact: true
ArtifactMetadata:
  title: Task list — maps + artifact rules + opencode pointer fix
  type: task_list
  date: 2026-06-26
---

# Task list (final state)

- [x] Investigate all three asks across main + aviationchat + clean-bmad (read-only)
- [x] Verify artifact rules in place — `artifacts-always-first.md` byte-identical in all 3 (no action)
- [x] Verify opencode `.agent`→`.agents` fix — aviationchat ✅; main + clean-bmad still broken
- [x] Plan written + approved
- [x] Fix `.agent/`→`.agents/` pointers: main (.agents/.claude/.opencode)
- [x] Fix `.agent/`→`.agents/` pointers: clean-bmad (.agents/.claude/.opencode)
- [x] Exclude 4 intentional-prose files (generate_doc_graph.py, skills_explained.md, antigravity.md, adk_file_formating.md)
- [x] Targeted rewrite: clean-bmad adk_file_formating.md stale path → in-repo v3-prompt-architecture
- [x] Fix stale `/1_ccps_boot-context` → `/boot-sprint-context` in clean-bmad AGENTS.md
- [x] Fix aviationchat check_maps.py root-resolution bug (master + vendored, kept identical)
- [x] Maps: main clean (no edits); aviationchat AUTO regen (epic-15); clean-bmad AUTO no-diff + curated dead-path fix
- [x] Re-run linters → main & aviationchat both "All maps & INDEXes agree with disk"
- [x] Write walkthrough + task-list + INDEX row
- [ ] Daniel: commit each repo + set anchors (main, aviationchat) — handed off in walkthrough "Your Actions"
- [ ] Optional: vendor check_maps.py into clean-bmad; re-sync mirrors via /sync-agents
