---
IsArtifact: true
ArtifactMetadata:
  title: Artifact-routing fix — every engine + command nests under epic_<E>/ (all 3 surfaces)
  type: walkthrough
  date: 2026-07-03
---

# Walkthrough — artifact-routing fix (lobby · AGY · Fresh)

## What was wrong
Story artifacts were landing at the `_artifacts/` **root** instead of `_artifacts/epic_<E>/<story>/`.
Proof on disk: `Projects/AGY_AVIATIONCHAT/_artifacts/2026-07-03_autopilot-11-18/` (today's run) sat at the
root next to an existing `epic_11/`, and `tea-17-p1-unit-stragglers/` sat at the root instead of under
`tea/`.

Two independent root causes:
1. **opencode engine drift.** `scripts/autopilot-dev-story-opencode.ps1` (both AGY + Fresh) computed
   `$Folder = _artifacts/<date>_<slug>` with **no `epic_<E>/` parent** — it was forked from a *pre-fix*
   copy of the claude engine (`autopilot-dev-story.ps1`, which nests correctly). The 11-18 run used this
   engine (log banner "opencode engine"), so it dropped at root.
2. **Interactive command enforced the path too late.** `/sudo-dev-story-tests.md` only named
   `_artifacts/epic_<E>/<story>/` at **Step 5** (close-out). Steps 1–4 delegate to `bmad-dev-story` /
   `sudo-self-audit` / `bmad-testarch-*`, none of which were told the path — so the plan + audit landed
   wherever the sub-skill defaulted.

Not broken (verified, left alone): the **claude** engine (both projects) and **`/autopilot_mobile.md`**
(computes epic nesting at its Step 2). Sibling `/sudo-code-review.md` already epic-nests; the `_AP` twins
write to "the shared folder" the engine now nests, so fixing the engine fixed them for free.

## What changed, file by file

**Code (the actual bug):**
- `Projects/AGY_AVIATIONCHAT/scripts/autopilot-dev-story-opencode.ps1` — ported the epic-parent block from
  the claude engine: derive `$parent = epic_<leading-number>` from the story id, dual reuse-glob (search the
  epic bucket **then** the root so pre-fix runs still resume), and mint the folder under `$parent`. `$Folder`
  is the single upstream var — it feeds `$LogDir`, `$decisionsLog`, `_RUN-STATUS.md`, the artifact-presence
  checks, and all four stage prompts, so this one change propagates everywhere.
- `Projects/Fresh_Workspace_BMAD/scripts/autopilot-dev-story-opencode.ps1` — same port (engines kept in parity).

**Command (master `.agents/`, synced to all surfaces):**
- `.agents/commands/sudo-dev-story-tests.md` — new **Step 0.5** resolves + creates
  `ARTIFACT_DIR = PROJECT_ROOT/_artifacts/epic_<E>/<story>/` (TEA/non-numeric → `tea/`, true one-off → dated
  root), echoes it, and passes it to every sub-step; Steps 1, 2 and 5 now write into `ARTIFACT_DIR` instead
  of "the story's artifact folder" / a Step-5-only assertion.

**Docs (project-local, per-surface):**
- `Projects/AGY_AVIATIONCHAT/_artifacts/README.md` — fixed the self-contradiction (banner said "no `_main`
  bucket inside a project" while rule #2 + disk use `_main/`); documented the `tea/` bucket.
- `Projects/Fresh_Workspace_BMAD/_artifacts/README.md` — same `_main` fix + routed system work to `_main/`
  (was going to root) and reshaped the placement list to story→epic / system→`_main` / one-off→root / retired.
- `Projects/Fresh_Workspace_BMAD/_artifacts/INDEX.md` — header placement line aligned.
- `Projects/AGY_AVIATIONCHAT/_artifacts/INDEX.md` — session row for this fix + `tea/` added to the epic-bucket table.
- `_artifacts/INDEX.md` (lobby) — session row for this fix.
- Lobby `_artifacts/README.md` — **already correct** (documents local `_main/`); left untouched.

**Data relocations (git mv, history preserved):**
- `_artifacts/2026-07-03_autopilot-11-18/` → `_artifacts/epic_11/2026-07-03_autopilot-11-18/` (13 files)
- `_artifacts/tea-17-p1-unit-stragglers/` → `_artifacts/tea/tea-17-p1-unit-stragglers/`

**Propagation:** `/sync-agents` vendored the master command edit into lobby + AGY + Fresh (`.agents/commands`,
`.opencode/commands`, the Antigravity `.agents/workflows/` mirror) and the machine-global caches.

## Test output (actual, pasted)

opencode engine now nests (AGY `-DryRun` for story 11.18):
```
 AUTOPILOT DRY RUN - resume plan (opencode engine)
   Story  : ...\Projects\AGY_AVIATIONCHAT\_bmad\bmm\stories\story-11-18-terms-warning-color.md
   Folder : ...\Projects\AGY_AVIATIONCHAT\_artifacts\epic_11\2026-07-03_autopilot-11-18
```
Fresh engine parses clean (identical code):
```
Fresh opencode engine: PARSE OK
```
Step 0.5 propagated to every synced copy (grep -c "Step 0.5"):
```
.agents/commands/sudo-dev-story-tests.md                       -> 3
Projects/AGY_AVIATIONCHAT/.agents/commands/sudo-dev-story-tests.md   -> 3
Projects/AGY_AVIATIONCHAT/.opencode/commands/sudo-dev-story-tests.md -> 3
Projects/AGY_AVIATIONCHAT/.agents/workflows/sudo-dev-story-tests.md  -> 3
Projects/Fresh_Workspace_BMAD/.agents/commands/sudo-dev-story-tests.md -> 3
.agents/workflows/sudo-dev-story-tests.md                      -> 3
```
`_artifacts/` root after relocation — no story/autopilot folders left at root:
```
INDEX.md  README.md  _archived  _autopilot-run-11-18*.log  _main  epic_11  epic_12
epic_13  epic_14  epic_15  epic_8  tea
```

## AC → evidence
| Goal | Evidence |
|---|---|
| opencode engine nests under `epic_<E>/` | AGY dry-run prints `…\epic_11\…`; Fresh parses OK (same code) |
| Interactive dev flow nests from the start | Step 0.5 present ×3 in all 6 synced copies |
| "Any agent/workflow knows where to put things" | claude + mobile engines already correct; opencode fixed; command hardened; rule (`artifacts-always-first`) is the single source |
| README + INDEX correct (all 3 surfaces) | `_main` contradiction removed in AGY + Fresh READMEs; `tea/` documented; INDEX rows + headers reconciled; lobby README already correct |
| Misplaced folders relocated | `git mv` renames (history preserved); root clean |

## Task Checklist
- [x] Fix AGY opencode engine (epic nesting) — verified via dry-run
- [x] Fix Fresh opencode engine — verified via parse
- [x] Harden `/sudo-dev-story-tests.md` Step 0.5 + Steps 1/2/5 → `ARTIFACT_DIR`
- [x] Verify siblings (`sudo-code-review` already nests; `_AP` twins use shared folder; mobile already correct)
- [x] Fix AGY README (`_main` contradiction + `tea/` bucket) + INDEX (row + bucket table)
- [x] Fix Fresh README (`_main` + system→`_main/`) + INDEX header
- [x] Add lobby INDEX row (lobby README already correct — no change)
- [x] Relocate 11-18 → epic_11/, tea-17 → tea/ (git mv)
- [x] `/sync-agents` → lobby + AGY + Fresh + globals; Step 0.5 verified in every copy

## Your Actions
Three separate repos, all on **`main_debug`**. Explicit paths only (there is pre-existing uncommitted work
in AGY — `_bmad-output/*` and `epic_8/story-8.22.1/walkthrough.md` — that is **not** part of this task; the
commands below exclude it). The AGY **opencode engine** is already committed on your side (clean tree), so
it's not in the AGY command.

**Lobby** (`Sudo_Hatter_Command`):
```bash
git add .agents/commands/sudo-dev-story-tests.md .agents/workflows/sudo-dev-story-tests.md \
        .opencode/commands/sudo-dev-story-tests.md _artifacts/INDEX.md \
        _artifacts/_main/2026-07-03_artifact-routing-fix/
git commit -m "fix(artifacts): epic-nest artifacts in interactive dev flow; doc reconcile"
```

**AGY** (`Projects/AGY_AVIATIONCHAT`) — the 13 relocations are already staged by `git mv`:
```bash
git add .agents/commands/sudo-dev-story-tests.md .agents/workflows/sudo-dev-story-tests.md \
        .opencode/commands/sudo-dev-story-tests.md _artifacts/README.md _artifacts/INDEX.md
git commit -m "fix(artifacts): nest opencode story runs under epic_<E>/; relocate 11-18 + tea-17; doc reconcile"
```

**Fresh** (`Projects/Fresh_Workspace_BMAD`):
```bash
git add scripts/autopilot-dev-story-opencode.ps1 .agents/commands/sudo-dev-story-tests.md \
        .agents/workflows/sudo-dev-story-tests.md .opencode/commands/sudo-dev-story-tests.md \
        _artifacts/README.md _artifacts/INDEX.md
git commit -m "fix(artifacts): port epic-nesting into opencode engine; doc reconcile"
```

Then **restart opencode** to pick up the refreshed global command cache (the sync updated
`~/.config/opencode/commands` + `~/.gemini/antigravity/global_workflows`, which live outside the repos).
