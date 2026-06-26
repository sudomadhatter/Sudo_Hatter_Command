---
title: Finish the artifacts policy (work-from-cwd) + home-base repo-map/drift — Walkthrough
type: walkthrough
workspace: _home
date: 2026-06-25
status: COMPLETE (agent-side) — commit pending
plan: ./implementation_plan.md
---

# Walkthrough — artifacts policy finish (work-from-cwd) + home-base repo-map/drift

## What this was
Finish the `_artifacts/` setup: write the structure how-to, reconcile the canonical docs to the placement
policy, and confirm the home base's hybrid repo-map/drift. Approved as a 5-workstream plan (WS-A…E + drop WS-C).

## ⚠️ Plot twist — the policy changed mid-execution (and that's fine)
Right after approval, a **mobile edit landed via git merge** that changed the artifact-placement policy from
*"artifacts live WITH the work (always project-local)"* → **"artifacts go where you WORK FROM (your cwd)."** I
paused, flagged the conflict, and (on your "clear to continue") **re-aligned to work-from-cwd**:
- **WS-C dropped** — under work-from-cwd, clean-bmad work done *from the home base* correctly lives in the
  home-base bucket `_artifacts/clean-bmad-workspace/`. No migration needed; clean-bmad untouched.
- **WS-A redone** — the README I'd written to the old policy was rewritten to work-from-cwd.
- **WS-B retargeted** — reconciled the *remaining* stale refs to work-from-cwd (the merge had already done
  AGENTS.md §5/§7 + workspace-standard Part 2).
- **WS-D was already done by the merge** — `_docs/repo-map.md` + the SessionStart drift hook were already wired.

## What changed — this session (home base)
| WS | Change | File |
|---|---|---|
| WS-A | New **artifacts how-to** (work-from-cwd; folder shapes; **story→`<epic>/<story>/`, create epic if missing**; session-folder set) | `_artifacts/README.md` |
| WS-B | §3 gate repointed off `_artifacts/<workspace>/…` → "the right `_artifacts/` for where you work from (§5)" | `AGENTS.md` |
| WS-B | Part-1 stragglers (§9 spec, supporting-files, format checklist) + appendix note → work-from-cwd | `_docs/workspace-standard.md` |
| WS-B | The master rule flipped: intro blockquote + §2 placement (was "file by what the work changes, not where you ran it" — the *opposite*) + §6/§7 path examples → work-from-cwd | `.agents/rules/artifacts-always-first.md` |
| WS-D | Refreshed the AUTO body to the documented `--mode content` rebuild (curated header was already authored by the merge) | `_docs/repo-map.md` |
| memory | Renamed `artifacts-live-with-the-work` → **`artifacts-go-where-you-work-from`** (new file; old deleted; `MEMORY.md` repointed) | `~/.claude/.../memory/` |

## Already done by the merge (verified, not re-done)
- `AGENTS.md` §4/§5/§7 + `workspace-standard.md` Part 2 + `INDEX.md` header → work-from-cwd.
- `.claude/settings.json` SessionStart hook: continuity + gate + `_docs/repo-map.md` injection + drift check.
- `.agents/scripts/check-repo-map-drift.ps1` evolved with `-Root` / `-MapPath` / `-IgnoreExtra`.
- `_docs/repo-map.md` curated header authored.

## Verification (real output)
- **Home-base repo-map regenerated:** `generate_repo_map.py --mode content --ignore Projects,_my_resources` → `exit=0`.
- **Drift check clean:** `check-repo-map-drift.ps1 -Root … -MapPath _docs/repo-map.md` → `exit=0`, silent (no drift).
- **Stale-ref sweep:** `grep '_artifacts/<workspace>'` across AGENTS.md / workspace-standard / artifacts-always-first
  → only the dated appendix line remained, now marked **superseded**. No live stale refs left.

## ⚠️ Your Actions (I do not commit/push — git-policy)
The tree mixes three things: the **merge** (already staged — settings.json, drift script, repo-map, router/INDEX),
**this session's policy work**, and the **earlier clean-bmad session**. Review `git status`, then commit the
home-base policy work (the merge files come along since they're staged):

```bash
cd "c:/Sudo_Hatter_Command"
git add _artifacts/README.md "_artifacts/_home/2026-06-25_artifacts-policy-finish-and-drift-backport" \
  .agents/rules/artifacts-always-first.md AGENTS.md _docs/workspace-standard.md _docs/repo-map.md
git status                      # confirm: policy files + the staged merge (settings.json, check-repo-map-drift.ps1, router.md, INDEX.md)
git commit -m "docs(home-base): finish artifacts work-from-cwd reconciliation + home-base repo-map/drift; README how-to; align AGENTS/workspace-standard/artifacts-always-first"
git push
```
> The clean-bmad reshape session (`_artifacts/clean-bmad-workspace/...`, its repo, router/INDEX rows) is separate
> — commit it on its own pass if you haven't. Memory edits live in `~/.claude/...` (outside this repo).

## Open / next
- Optional: re-sync the updated `artifacts-always-first.md` to each project's `.claude/`·`.opencode/` (the
  projects' vendored copies still carry older wording) — a `/sync-agents` propagation pass.
- The earlier clean-bmad hand-offs still stand (apply its `settings.json.proposed`, commit its repo).
