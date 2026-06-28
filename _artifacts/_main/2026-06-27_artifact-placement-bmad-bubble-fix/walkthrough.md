---
IsArtifact: true
ArtifactMetadata:
  title: Walkthrough — artifact placement fix (BMAD bubble → _artifacts/)
  type: walkthrough
  date: 2026-06-27
---

# Walkthrough — stop agents writing to the retired `_claude_artifacts/`

## What changed & why
`/bmad-dev-story` (run by hand for story 14.7) wrote its session artifacts to
`Projects/AGY_AVIATIONCHAT/_claude_artifacts/2026-06-27_story-14-7-sully-grading-event/` — the **retired**
store. Root cause (verified, not guessed):

- The canonical placement rule (`_artifacts/epic_<E>/<story>/`) is correct in **three** global docs already:
  the workspace `_artifacts/README.md`, `AGENTS.md` §5, and the always-load rule `artifacts-always-first.md`.
- **The BMAD skill flow loads none of them.** `grep` over `.agents/bmad/**` for any reference to the global
  rule or the `_artifacts/` path returns **empty**. Its only artifact instruction was the custom TOML's
  path-LESS *"create walkthrough.md + your-action-required.md,"* and its BMAD config points at a different
  store (`_bmad-output`). With no folder in working memory, the agent grabbed the only artifact-ish string in
  its context — the stale `_claude_artifacts/...` in the story's `source:` frontmatter.

So the engine wasn't broken and the global docs weren't wrong — the **path never travelled with the
instruction** into the per-tool bubble. Fix = put the explicit path *into* the instruction the agent can't
forget, and make every global doc explicitly **reject** the dead name so any agent (any tool) knows.

## Files changed (lobby master = single source; copies are exact mirrors)

| File | Change |
|------|--------|
| `.agents/bmad/custom/bmad-dev-story.toml` | `persistent_facts` + `on_complete` now name the exact folder `_artifacts/epic_<E>/story-<E.S>-<slug>/`, cite `_artifacts/README.md`, and hard-reject `_claude_artifacts/` + `_bmad-output/`. Added a dated FIX comment. |
| `.agents/bmad/custom/bmad-quick-dev.toml` | Same treatment (story → `epic_<E>/<story>/`, other work → `<date>_<slug>/`). |
| `.agents/rules/artifacts-always-first.md` | Added a ⛔ stop in the shared-memory blockquote: the store is ALWAYS `_artifacts/`; `_claude_artifacts/`+`_opencode_artifacts/` are retired — never create them. Catches **non-BMAD** agents too. |
| `_artifacts/README.md` (×3: lobby, aviationchat, fresh-workspace) | Added the same one-line ⛔ stop near the top. |
| **Propagated** to `Projects/AGY_AVIATIONCHAT/_bmad/custom/` (the active copy the agent reads), and the vendored `.agents/bmad/custom/` + `.agents/rules/` in **both** projects. | 8 TOML copies + 2 rule copies, each verified byte-identical to master. |
| `Projects/AGY_AVIATIONCHAT/_artifacts/epic_14/story-14.7-sully-grading-event/` | **Relocated** here from `_claude_artifacts/…`; the empty `_claude_artifacts/` dir removed; the 2 stale `_claude_artifacts/` paths inside its `your-action-required.md` (the OWED git command + the status note) repointed to the new path. |

## Why this honors "make it global, any agent should know"
The **rule** still lives in the global docs (README + always-load rule). The TOMLs don't restate it — they
**cite** the README and carry just the path token + the reject, which is the only way the BMAD bubble (which
never opens those docs) can obey it. Belt (global doc) **and** suspenders (path in the un-forgettable
close-out instruction).

## Verification (real output)
```
CHECK 1 — live "_claude_artifacts" write-instructions remaining:  NONE
  (only hits left = the new "RETIRED/never create/MOVE them" stops + the
   python_inter_venv_fix skill's historical origin-session paths, kept as accurate history)
CHECK 2 — explicit _artifacts/epic_ path present in all 8 TOML copies:
  3 hits dev-story / 2 hits quick-dev  ×  {master, avch _bmad/custom, avch vendored, fresh vendored}  ✓
CHECK 3 — aviationchat relocation:
  _claude_artifacts/ exists? NO (gone) · 14.7 at correct path? YES · stale ref inside moved folder? NO
CHECK 4 — "never _claude_artifacts" stop in all 3 READMEs:  OK / OK / OK
CHECK 5 — SAMENESS across lobby + aviationchat + fresh-workspace (after one-doc reconcile):
  artifacts-always-first.md  → 2/2 copies byte-identical to master
  bmad-dev-story.toml        → 3/3 copies (avch _bmad/custom, avch vendored, fresh vendored) identical
  bmad-quick-dev.toml        → 3/3 copies identical
  RESULT: ALL IDENTICAL ✓
```

## Resolved mid-session — the one-doc closing model
While this was in flight you updated `artifacts-always-first.md` to the **one-doc** model: a single
`walkthrough.md` ending with a `## Task Checklist` section then a `## Your Actions` section — **no** separate
`your-action-required.md` or `task-list.md`. That settles the contradiction I'd flagged. I reconciled **both
BMAD TOMLs** (dev-story + quick-dev) to mandate exactly that one doc (keeping the folder-path fix), updated
their header comments, re-propagated the updated rule + TOMLs to every copy, and confirmed all
**byte-identical** across the three workspaces (sameness check below). This session's own close-out follows the
new model — checklist + actions are sections here, not separate files.

## Deliberate non-changes
- ~70 story `source:` frontmatter lines pointing at old `_claude_artifacts/…` planning docs — historical
  provenance (dead pointers, not instructions); the path-in-memory fix dominates them.
- `python_inter_venv_fix` skill's origin-session paths — kept as accurate history (per the workspace standard).
- aviationchat `AGENTS.md` line ~108 ("…consolidated into `_artifacts/`") — correct, *helpful* history.
- `Projects/Ingestion_pipeline_AvCh/` — old un-migrated layout; you didn't list it; separate migration.

## Task Checklist
- [x] Root-caused: the BMAD flow never loads the global placement rule, so a path-less "create artifacts"
      instruction let `/bmad-dev-story` grab `_claude_artifacts` from the story's `source:` frontmatter.
- [x] Baked explicit `_artifacts/epic_<E>/<story>/` path + never-`_claude_artifacts` reject into both BMAD TOMLs.
- [x] Hardened the always-load rule + all 3 `_artifacts/README.md` with the same stop.
- [x] Reconciled both TOMLs to your one-doc model after the rule update (no separate `your-action-required.md`/`task-list.md`).
- [x] Propagated rule + TOMLs to every copy; verified **byte-identical** across the 3 workspaces.
- [x] Relocated the misplaced 14.7 folder → `_artifacts/epic_14/story-14.7-sully-grading-event/`; fixed its
      handoff git paths; deleted the empty `_claude_artifacts/`.
- [ ] (Daniel) Commit the 3 repos below; commit the corrected 14.7 commit from its own handoff doc.

## Your Actions
*(I don't commit — git-policy; branch must be `main_debug`, never `main`.)*
Three separate repos. Stage **explicit paths only** — each repo has unrelated pre-existing churn, so do **not**
`git add -A`. The relocated 14.7 folder is **not** here — it rides with your already-OWED 14.7 commit (whose
command I corrected inside `_artifacts/epic_14/story-14.7-sully-grading-event/your-action-required.md`).

**1) Lobby repo** (`Sudo_Hatter_Command/`):
```bash
cd "c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command"
git add \
  .agents/bmad/custom/bmad-dev-story.toml \
  .agents/bmad/custom/bmad-quick-dev.toml \
  .agents/rules/artifacts-always-first.md \
  _artifacts/README.md \
  _artifacts/INDEX.md \
  _artifacts/_main/2026-06-27_artifact-placement-bmad-bubble-fix/
git commit -m "fix(artifacts): bake _artifacts/ path into BMAD overlays; reject retired _claude_artifacts/ globally" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

**2) aviationChat repo** (`Projects/AGY_AVIATIONCHAT/`):
```bash
cd "c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/AGY_AVIATIONCHAT"
git add \
  .agents/bmad/custom/bmad-dev-story.toml \
  .agents/bmad/custom/bmad-quick-dev.toml \
  .agents/rules/artifacts-always-first.md \
  _bmad/custom/bmad-dev-story.toml \
  _bmad/custom/bmad-quick-dev.toml \
  _artifacts/README.md
git commit -m "fix(artifacts): vendor _artifacts/ path fix into BMAD overlays + rule; reject _claude_artifacts/" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
# (Story 14.7's relocated folder is committed by its OWN corrected command in
#  _artifacts/epic_14/story-14.7-sully-grading-event/your-action-required.md)
```

**3) fresh-workspace repo** (`Projects/Fresh_Workspace_BMAD/`):
```bash
cd "c:/Users/dlohn/.gemini/antigravity/scratch/Sudo_Hatter_Command/Projects/Fresh_Workspace_BMAD"
git add \
  .agents/bmad/custom/bmad-dev-story.toml \
  .agents/bmad/custom/bmad-quick-dev.toml \
  .agents/rules/artifacts-always-first.md \
  _artifacts/README.md
git commit -m "fix(artifacts): vendor _artifacts/ path fix into BMAD overlays + rule; reject _claude_artifacts/" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```
