---
IsArtifact: true
ArtifactMetadata:
  title: "Task list — generic update-maps + prune"
  type: task_list
  date: 2026-06-27
---

# Task list (final)

- [x] Part A — PATH CONTRACT + context-hygiene policy in `_docs/workspace-standard.md`
- [x] Part B — `check_maps.py` generic: mode + map-path + state-file auto-detect; conformance gate; prune hint; robust root
- [x] Test across all 3 roots + standalone vendored run (caught & fixed the root-detection bug; fixed em-dash mojibake)
- [x] Part D — `/1_update-maps` reframed LOBBY→generic + Step 3.5 prune + report/guardrails
- [x] Part C — synced tool + standard byte-identical to both projects; fresh-workspace now conformant
- [x] Close-out — INDEX row, walkthrough (with test output), this snapshot, surgical git commands

## Deferred (→ item 3, fix clean-workspace / mirroring)
- [ ] Consolidate legacy `scripts/` script copies into the canonical `.agents/scripts/` (kept identical for now)
- [ ] Reconcile/remove stray `Projects/AGY_AVIATIONCHAT/docs/file_structure_rules/workspace-standard.md`
- [ ] fresh-workspace's unrelated uncommitted churn (`.claude/`, `.opencode/`, `_claude_artifacts/`) — separate pass

## Not committed
- [ ] Daniel runs the 3 surgical commits (commands in `walkthrough.md` → Your Actions), then optional `/sync-agents`
