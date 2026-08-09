---
IsArtifact: true
ArtifactMetadata:
  title: Fix artifact placement — BMAD bubble drifts to retired _claude_artifacts/
  type: implementation_plan
  date: 2026-06-27
---

# Fix artifact placement — any agent, any tool, lands in `_artifacts/`

## The bug (root cause, verified)
`/bmad-dev-story` wrote story 14.7's session artifacts to
`Projects/AGY_AVIATIONCHAT/_claude_artifacts/2026-06-27_story-14-7-sully-grading-event/` — the **retired**
store. Why:

- The canonical placement rule (`_artifacts/epic_<E>/<story>/`) is correct in **three** global places:
  the workspace `_artifacts/README.md`, the project `AGENTS.md` §5, and the always-load rule
  `.agents/rules/artifacts-always-first.md` §2.
- **But the BMAD skill flow never loads any of them.** A grep of `.agents/bmad/**` for
  `artifacts-always-first` / `_artifacts/epic` / `_artifacts/<` returns **empty**. The flow's only artifact
  instruction is the custom TOML's path-LESS *"create walkthrough.md + your-action-required.md as artifacts,"*
  and its BMAD config points at a *different* store (`output_folder: _bmad-output`).
- Given "create artifacts" + no folder, the agent grabbed the only artifact-ish string in its context — the
  stale `_claude_artifacts/...` in the story's `source:` frontmatter — and invented the folder.

So it is **not** the autopilot engine (that engine is correct: `_artifacts/epic_<N>/`), and it is **not** a
wrong global doc. It's that the per-tool execution bubbles don't carry the path. Fix = make the path travel
with the instruction **and** make the global docs explicitly reject the dead name — so any agent knows,
regardless of who writes.

## Scope (the workspaces you listed)
Lobby (`Sudo_Hatter_Command/`), `Projects/AGY_AVIATIONCHAT/`, `Projects/Fresh_Workspace_BMAD/`.
*(Out: `Projects/Ingestion_pipeline_AvCh/` — old un-migrated layout, separate migration; you didn't list it.)*

## Changes

### 1. BMAD custom TOMLs — bake in the path (the actual lever)
`bmad-dev-story.toml` + `bmad-quick-dev.toml`: rewrite the artifact `persistent_facts` line and `on_complete`
so they (a) name the explicit folder `_artifacts/epic_<E>/<story>/` (story) or `_artifacts/<date>_<slug>/`
(other), (b) **cite the global rule** (`_artifacts/README.md`) rather than restating it, and (c) add a hard
stop: **NEVER `_claude_artifacts/` (retired) or `_bmad-output/`**. Keeps the existing `walkthrough.md` +
`your-action-required.md` filenames (your workflow uses them — see Flag below).

Files (master + every copy, since `/sync-agents` preserves `bmad-*` and skips `_bmad/custom/`):
- `.agents/bmad/custom/{bmad-dev-story,bmad-quick-dev}.toml` (lobby master — single source)
- `Projects/AGY_AVIATIONCHAT/_bmad/custom/{…}.toml`  ← **the copy the agent actually reads**
- `Projects/AGY_AVIATIONCHAT/.agents/bmad/custom/{…}.toml` (vendored)
- `Projects/Fresh_Workspace_BMAD/.agents/bmad/custom/{…}.toml` (vendored; no active `_bmad/custom/` yet)

### 2. Always-load rule — explicit reject of the dead name
`.agents/rules/artifacts-always-first.md`: add one stop line — *the store is `_artifacts/`; the retired
`_claude_artifacts/` and `_opencode_artifacts/` names are DEAD — never create them.* This catches **non-BMAD**
agents too. Propagates to projects via `/sync-agents` (rules are mirrored).

### 3. The three `_artifacts/README.md` — one-line reject
Add the same "never `_claude_artifacts/`" stop to each workspace's README (these are project-local, edited
per workspace). The positive path is already correct in all three.

### 4. Relocate the misplaced 14.7 folder (aviationchat)
`_claude_artifacts/2026-06-27_story-14-7-sully-grading-event/` →
`_artifacts/epic_14/story-14.7-sully-grading-event/` (matches the README scheme + the existing `epic_14/`).
Fix the `_claude_artifacts/...` path inside that folder's `your-action-required.md` git command (commit is
still OWED), then delete the now-empty `_claude_artifacts/`.

## Deliberate non-changes
- **Story `source:` frontmatter** (~70 files pointing at old `_claude_artifacts/...` planning docs): left as
  historical provenance (dead pointers, not instructions). The path-in-working-memory fix dominates them.
- **aviationchat `AGENTS.md` line ~108** ("old `_claude_artifacts/` … consolidated into `_artifacts/`"):
  correct, *helpful* history — tells an agent NOT to use it. Left as-is.

## Flag for you (not fixing silently)
The always-load rule says **don't** write `your-action-required.md` (fold "Your Actions" into
`walkthrough.md`), but the BMAD TOMLs **mandate** it — a pre-existing contradiction. Your live workflow uses
`your-action-required.md`, so I'm **keeping** it and leaving the rule reconciliation as a separate decision.
Say the word and I'll align them either way.

## Verification
- `grep -rI _claude_artifacts` over `.agents/**` + `_bmad/custom/**` → only history, **zero** live
  instructions.
- Each patched TOML contains `_artifacts/epic_` and the never-`_claude_artifacts` stop.
- aviationchat: folder is at `_artifacts/epic_14/story-14.7-…`, `_claude_artifacts/` gone.
- Re-list the 3 workspaces' READMEs + rule copies carry the stop line.
