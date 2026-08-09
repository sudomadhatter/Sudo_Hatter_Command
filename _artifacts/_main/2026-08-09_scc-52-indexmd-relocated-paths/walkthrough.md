---
type: walkthrough
story: SCC-52
date: 2026-08-09
branch: chore/SCC-52-indexmd-relocated-paths
---

# SCC-52 — Two relocated path refs in `commands/INDEX.md`

SCC-49's close-out link check flagged two paths in `.agents/commands/INDEX.md` that do not resolve.
Neither file is missing. **Both are relocations**, which is the failure mode that looks like a dead
link and isn't — the target moved and the citation stayed put.

## Task Checklist

- [x] **`sudo-adviser-board-REFERENCE.md`** — cited as `_my_resources/research_docs/`, actually lives
      in `_my_resources/diagrams_guides/workflows_tea_testing/`. `research_docs/` exists, which is why
      the wrong path reads as plausible. Corrected.
- [x] **`scripts/autopilot-dev-story-opencode.ps1`** — written lobby-relative, but the opencode
      autopilot engine is **project-local** (`autopilot-engine-is-project-local`): a copy sits in
      four `Projects/*/scripts/`, and none at the lobby root. A lobby-relative path can therefore
      never resolve, no matter which project you mean. Rewritten as
      `Projects/<name>/scripts/…` with the reason stated inline, so the next reader does not "fix"
      it back to a bare path.
- [x] **Stale line count corrected** — the entry claimed ~826 lines; the file is **843**. Found only
      because verifying the path meant opening it.

## Evidence

| Claim | Proof |
|---|---|
| Both refs now resolve | link check over `commands/INDEX.md` → **3 path refs, 0 unresolved** |
| The project-local template is real | `Projects/AGY_AVIATIONCHAT/scripts/autopilot-dev-story-opencode.ps1` exists (843 lines) |
| Enforcement suite green | `python3 .agents/scripts/tests/run_all.py` → **8/8 files, 237 cases** |

`Verdict: PASS @ HEAD` — docs-only, no code surface touched, no lint floor applies.

## Your Actions

Pre-existing defects, not introduced by SCC-49 — that pass is what found them. Nothing else owed.

**One finding about the gate itself**, raised rather than patched: `task_preflight.py`'s clean-tree
check errors on **any** dirty path, including files belonging to a different ticket. On this run it
blocked on SCC-41's in-flight `_artifacts/` folder, which has nothing to do with SCC-52 and does not
enter the merge. Loosening it mid-run would have been "working around the failing check", which the
command forbids — so it is recorded here for a decision instead.
