---
IsArtifact: true
ArtifactMetadata:
  title: Artifact-routing fix — make every engine + command nest under epic_<E>/
  type: implementation_plan
  date: 2026-07-03
---

# Artifact-routing fix — every agent/workflow lands artifacts in the right folder

## Problem (verified on disk)
Story artifacts are landing at the `_artifacts/` **root** instead of `_artifacts/epic_<E>/<story>/`.
Ground truth: `Projects/AGY_AVIATIONCHAT/_artifacts/2026-07-03_autopilot-11-18/` (today's opencode run)
sits at root, though `epic_11/` exists right beside it; `tea-17-p1-unit-stragglers/` (interactive run)
also dropped at root instead of under the `tea/` bucket.

## Root causes
1. **opencode engine drift.** `scripts/autopilot-dev-story-opencode.ps1` (both AGY + Fresh_Workspace,
   line ~185) computes `$Folder = _artifacts/<date>_<slug>` with **no `epic_<E>/` parent**. It was forked
   from a *pre-fix* copy of the claude engine (`autopilot-dev-story.ps1`, which DOES nest — lines 290–312).
   The `2026-07-03_autopilot-11-18` run used this engine (log banner: "opencode engine").
2. **Interactive command only enforces the path at the end.** `/sudo-dev-story-tests.md` names
   `_artifacts/epic_<E>/<story>/` only in **Step 5** (close-out checklist). Steps 1–4 delegate to
   `bmad-dev-story` / `sudo-self-audit` / `bmad-testarch-*`, none of which are told the path, so the plan +
   audit land wherever the sub-skill defaults.
3. **Docs out of sync.** AGY `_artifacts/README.md` contradicts itself — the banner says "There is no
   `_main` bucket inside a project" but placement rule #2 (and the rule + disk) use `_main/`. INDEX has no
   row for this regression and no `tea/` bucket entry.

Not broken (verified): the **claude** engine (both projects) and **`/autopilot_mobile.md`** (computes epic
nesting correctly at its Step 2). The `_AP` twins + `autopilot_mobile.workflow.js` trust the `folder` handed
to them, so fixing the engine's `$Folder` computation fixes them for free.

## Changes
| # | File | Change |
|---|---|---|
| 1 | `Projects/AGY_AVIATIONCHAT/scripts/autopilot-dev-story-opencode.ps1` | Port the epic-parent block from the claude engine (add `$parent = epic_<N>`, dual reuse-glob epic+root, mint under `$parent`). Single-point fix — `$Folder` feeds all 4 stage prompts + presence checks. |
| 2 | `Projects/Fresh_Workspace_BMAD/scripts/autopilot-dev-story-opencode.ps1` | Same port (keep the two projects' engines in parity). |
| 3 | `.agents/commands/sudo-dev-story-tests.md` (master) | Add an explicit "resolve + create the epic artifact folder" step BEFORE Step 1 and pass it into every sub-step, so the plan/audit/walkthrough all write there — not just the Step-5 checklist. |
| 4 | `Projects/AGY_AVIATIONCHAT/_artifacts/README.md` | Fix the `_main` self-contradiction (there IS a local `_main/`); document the `tea/` bucket for TEA stories. |
| 5 | `Projects/AGY_AVIATIONCHAT/_artifacts/INDEX.md` | Add a row for this fix; add `tea/` to the bucket table; record the two relocations. |
| 6 | data | `git mv` the 2 misplaced folders: `2026-07-03_autopilot-11-18/` → `epic_11/`, `tea-17-p1-unit-stragglers/` → `tea/`. |
| 7 | sync | `/sync-agents` to propagate the master `.agents/` command edit to all surfaces. |

## Verification
- `grep -n epic_` both opencode engines → parent logic present.
- Re-list `_artifacts/` root → no story folders left at root (only INDEX/README/_main/_archived/tea/epic_*/logs).
- Dry-run the AGY opencode engine (`-DryRun`) for a story id → prints `Folder : ...\epic_11\...`.
- README self-consistency: banner ↔ placement table agree on `_main/`.

## Out of scope / notes
- Fresh_Workspace README/INDEX not touched (empty-ish; engines fixed for parity). Flag if you want them too.
- `tea/` bucket is codified as the TEA-story home (16 folders already use it) — judgment call, called out here.
