---
IsArtifact: true
ArtifactMetadata:
  title: "Walkthrough — Story-Artifact Token Optimization (two-doc close)"
  type: walkthrough
  date: 2026-08-02
---

# Walkthrough — Story-Artifact Token Optimization

> Plan: [implementation_plan.md](implementation_plan.md) (approved). Scope grew mid-run on Daniel's
> instruction: propagate across projects — lobby + AGY_AVIATIONCHAT + Fresh_Workspace_BMAD +
> NEXgen-VR-Director. TEA artifacts kept by ruling. First walkthrough written in the new outline shape.

## Task Checklist

- [x] Lobby rule rewrite — `artifacts-always-first.md`: two-doc close, §5 outline walkthrough, §6 review→walkthrough, §7 audit→plan, budgets (plan ≤8 KB / walkthrough ≤10 KB), legacy clauses
  - Mid-session drift: another lane landed `a5113ea`+`32ac02c` (Step 4.5 certification + `## Suite Ledger`) while I held stale reads — re-read every command before editing; the new shape absorbs `## Suite Ledger` as its own section.
- [x] Satellite rules — constitution (killed the "two homes by design" line), 000-PLAN-FIRST-GATE, mobile-mode, bmad_code_review_sudo_fix, both bmad TOMLs (outline shape baked into persistent_facts + on_complete)
- [x] Sudo commands + `_AP` twins — self-audit (Phase-4 persist step), dev-story-tests (Step 2 lanes + Step 5 = 2 docs), code-review (verdict → walkthrough `## Code Review`, diff-first clean-room ordering, Your-Actions triage), update-sprint-memory (flip gate reads `Verdict:` line, legacy fallback), merge-epic-workingtrees, prune-context
- [x] Autopilot surfaces — reference spec (relay/diagram/folder/resume maps), autopilot_claude/opencode/mobile commands (stage tables, REVIEW INCOMPLETE, mobile's inlined stage-3 resume logic)
- [x] Engines (6 × .ps1) — AGY pair edited by hand (`Test-DocSection` marker detection, stage-2 hard throw, stage-4 soft warn + `$reviewOk`, prompts); Fresh + NEXgen pairs patched via `git apply` of AGY's diff (byte-identical twins; dry-run verified) — all 6 PARSE OK
- [x] Fan-out — `/sync-agents`: lobby (20 claude / 47 opencode cmds + 3 global caches + codex skills) + 3 project syncs (23/50 each, 21 workflows regenerated)
- [x] Projects — 8 rule/TOML/reference files copied to each (blob-verified pre-edit = lobby HEAD, so straight copy was safe); `_artifacts/AGENTS.md` local law updated ×3
- [ ] Memory write + per-repo commit/push — in flight at close (see Your Actions)

## Evidence

Machine contracts now in force (the greps downstream steps rely on):
- Plan audit: `## Self-Audit (<date>)` section with **`Audit verdict: GO | NO-GO`** line.
- Review: `## Code Review (<date>)` section with **`Verdict: PASS|CONCERNS|FAIL|WAIVED @ <sha>`** first line — close-out's done-flip gate and both merge flows read this; legacy standalone files are the fallback for pre-2026-08-02 stories.
- Retired for new work: `self-audit-stress-test.md`, `code-review.md`, `sudo-code-review-<story>.md`. TEA outputs (`atdd-checklist-*`, `automation-summary-*`, `certification-*.json`) unchanged by ruling.

Verification pasted:
```
All 6 engines: [System.Management.Automation.Language.Parser]::ParseFile → PARSE OK
git apply --check engines.patch → clean on Fresh_Workspace_BMAD and NEXgen-VR-Director
Retired-name grep over .agents/ → only legacy-fallback / prohibition / history lines remain
sync-agents: lobby + 3 projects, all surfaces reported, Fresh living-template check OK
```

## Suite Ledger

| scope | command | result | why this run |
|---|---|---|---|
| 6 ps1 engines | PS AST ParseFile | OK ×6 | edited runtime code must parse |
| engine patch | git apply --check ×2 | clean | verify twins before applying |
| toolkit | retired-name grep | legacy-only | prove no live references remain |

## Your Actions

1. **Restart opencode** so the refreshed global command cache is picked up (sync-agents note).
2. **Live AGY worktree** (`story-21-8b-demo-data-quarantine`): its vendored toolkit copies predate this change — it inherits everything when it merges trunk; its in-flight story may still close the old way (legacy fallbacks cover it). No action unless it wedges.
3. First story under the new shape: sanity-check that ② produces the two docs and ③ appends — the budgets and section contracts are new muscle memory for the agents.
4. Commits + pushes: done by this session per repo (lobby, AGY, Fresh, NEXgen + lobby gitlink bump) — verify below in the final chat report; nothing else is owed.
