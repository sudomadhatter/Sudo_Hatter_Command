---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — artifact-parent-routing rolled out to main + fresh-workspace
  type: walkthrough
  date: 2026-06-27
---

# Walkthrough — "story artifacts nest under their epic" rolled out to `main` + `Fresh_Workspace_BMAD`

Applied the AGY fix to the two remaining workspaces. **Result: the three shared `.agents/` files are now
byte-identical to AGY in both targets**, and the fresh-ws autopilot script mints story runs under
`_artifacts/epic_<E>/` instead of the dated root. Both repos are on `main_debug`. **Nothing committed — your
commit commands are below (desktop git policy).**

## What changed, by workspace

### `main` (home base — Sudo_Hatter_Command, branch `main_debug`)
No autopilot ps1 here, so this was docs/commands only:
- `.agents/commands/autopilot_mobile.md` — Step 2 rewritten to derive the epic + nest under `epic_<epic>/`,
  with a dual reuse-glob (epic bucket + pre-fix root).
- `.agents/commands/autopilot_claude.md` — both `_artifacts/<date>_autopilot-<id>/` path strings →
  `_artifacts/epic_<epic>/<date>_autopilot-<id>/` (the unrelated `_RUN-STATUS.md` PID block was left untouched).
- `.agents/rules/artifacts-always-first.md` — generalized to **Story → `epic_<E>/<story>/` (any tool) ·
  System/infra → `_main/` · Random → root**, and fixed the "no `_main` inside a project" line to "no
  *cross-project* `_main`; a project keeps a local `_main/` for system/infra work."
- `_artifacts/README.md` + `_artifacts/INDEX.md` — placement summaries updated to match.
- `.claude/commands/autopilot_mobile.md` + `.claude/commands/autopilot_claude.md` — re-synced from `.agents/`
  (claude-only commands; `cp` + diff-verified identical).

### `Fresh_Workspace_BMAD` (clean-bmad-workspace, branch `main_debug`)
Same five doc/command edits as above **plus the actual code fix**:
- `scripts/autopilot-dev-story.ps1` — replaced the minting block: derive `$parent = epic_<n>` from the story
  id's leading number (else root), dual reuse-glob (epic bucket **then** root so pre-fix/in-flight runs still
  resume), mint under `$parent`. The existing `New-Item -Force` (after the `-DryRun exit 0`) creates `epic_<E>/`,
  so **dry runs stay inert**.

## Verification (real output)

**1. ps1 parses + epic logic is correct + inert** (run against the real fresh-ws `_artifacts/` root):
```
PARSE OK (no syntax errors)
StoryId : 1-1   FolderRel : _artifacts\epic_1\2026-06-27_autopilot-1-1    FolderExistsAfter : False
StoryId : 14-6  FolderRel : _artifacts\epic_14\2026-06-27_autopilot-14-6  FolderExistsAfter : False
StoryId : abc   FolderRel : _artifacts\2026-06-27_autopilot-abc          FolderExistsAfter : False
```
(epic derived for numeric ids · non-numeric falls back to root · nothing created = inert.) A full
`-DryRun` of the script itself isn't runnable here — the skeleton has no `_bmad/bmm/stories/*.md`, so the script
throws at story-resolution *before* the fixed code. The isolated test exercises exactly the changed block.

**2. Grep gates (both targets):** `epic_` tokens present in all three files (mobile 4 / claude 2 / rule 3);
**zero** leftover bare `_artifacts/<date>_autopilot-<id>/` or root-mint mobile lines.

**3. Byte-parity with AGY (the reference):**
```
autopilot_mobile.md         AGY vs MAIN: IDENTICAL ✅   AGY vs FRESH-WS: IDENTICAL ✅
autopilot_claude.md         AGY vs MAIN: IDENTICAL ✅   AGY vs FRESH-WS: IDENTICAL ✅
artifacts-always-first.md   AGY vs MAIN: IDENTICAL ✅   AGY vs FRESH-WS: IDENTICAL ✅
```

**4. Mirrors:** `.claude/commands/autopilot_{mobile,claude}.md` byte-identical to their `.agents/` sources in
both repos.

## Decisions taken (the plan's defaults — none flipped)
1. **`epic_<E>` underscore** everywhere (no epic folders on disk to force hyphen; matches AGY + the ps1 literal).
2. **Targeted `cp`** for the two claude-only mirrors, not a full `/sync-agents`.
3. **Resolved the README "no `_main`" contradiction** to match the authoritative rule wording.

## ⚠️ NOT MINE — exclude from the fresh-ws commit
Two files were already modified (uncommitted, from a prior session — traced to commit `1db7c18`) before this work
and are **unrelated** to the fix; I left them untouched and they carry **none** of my edits:
- `Projects/Fresh_Workspace_BMAD/.agents/workflows/autopilot_claude.md`
- `Projects/Fresh_Workspace_BMAD/.claude/settings.json`

The commit commands below use **explicit paths** that exclude both.

## Out of scope (flagged, not done)
- `autopilot_opencode.md` (`@26`) + `autopilot_bmad_dev_loop.md` (`@138`, `@268`) still reference the dated-root
  path in **all three** workspaces — AGY left them too. A later "align the opencode lane + workflow doc" pass can
  close this parity gap if you want it.

## Your Actions — commit (desktop git policy: you run these; both repos on `main_debug`)

**Home base** (`Sudo_Hatter_Command/`):
```bash
git add .agents/commands/autopilot_mobile.md .agents/commands/autopilot_claude.md \
  .agents/rules/artifacts-always-first.md \
  .claude/commands/autopilot_mobile.md .claude/commands/autopilot_claude.md \
  _artifacts/README.md _artifacts/INDEX.md \
  _artifacts/_main/2026-06-27_artifact-parent-routing-rollout/
git commit -m "feat(artifacts): nest story runs under their epic — roll out to home base

Generalize artifacts-always-first + both autopilot commands so a story's artifacts
land in _artifacts/epic_<E>/<story>/ (any tool), system/infra in _main/, random at root.
Re-sync .claude/ command mirrors. Matches the AGY reference fix byte-for-byte.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

**Fresh workspace** (`Projects/Fresh_Workspace_BMAD/`) — note the explicit paths exclude the two not-mine files:
```bash
git add scripts/autopilot-dev-story.ps1 \
  .agents/commands/autopilot_mobile.md .agents/commands/autopilot_claude.md \
  .agents/rules/artifacts-always-first.md \
  .claude/commands/autopilot_mobile.md .claude/commands/autopilot_claude.md \
  _artifacts/README.md _artifacts/INDEX.md
git commit -m "feat(artifacts): autopilot mints story runs under their epic, not the dated root

Derive epic from the story id in autopilot-dev-story.ps1 (dual reuse-glob = epic bucket
+ root for resume), update both autopilot commands + artifacts-always-first/README/INDEX.
Matches the AGY reference fix. Excludes pre-existing unrelated changes to
.agents/workflows/autopilot_claude.md and .claude/settings.json.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
