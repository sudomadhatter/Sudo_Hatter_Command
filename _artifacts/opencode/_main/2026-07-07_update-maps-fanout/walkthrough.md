---
title: /1_update-maps fan-out — lobby + AGY + Fresh — Walkthrough
date: 2026-07-07
workflow: .agents/workflows/1_update-maps.md
workspace: opencode/_main
status: complete (2 deferred code-fix items flagged for Daniel)
---

# Walkthrough — /1_update-maps fan-out (2026-07-07)

## What changed

Executed the `/1_update-maps` maintenance workflow from the home base (`--all` fan-out): reconciled the
lobby + every conformant project (`AGY_AVIATIONCHAT`, `Fresh_Workspace_BMAD`). `RAG_Pipeline_AC` flagged
NOT conformant — out of scope (conformance first). Edits docs/markdown only — no code, no commits.

### Lobby (Sudo_Hatter_Command) — 14 files
- `docs/repo-map.md` — AUTO block regenerated (mode=content, `--ignore Projects,_my_resources`).
  +3/-3 lines (file-count summaries updated after new INDEX.md files landed).
- 12 new level-2 `INDEX.md` files: `.agent/skills/`, `.agents/{bmad,hooks,opencode-agents,scripts,templates}/`,
  `.claude/{commands,hooks}/`, `.opencode/{agent,commands}/`, `_routing-canary/{control,skills}/`.
- `_artifacts/opencode/_main/INDEX.md` — added this session's row (+ fixed the prior row's format to use
  a backticked folder-name token so the depth-3 linter matches it).

### AGY_AVIATIONCHAT — 42 files
- `docs/repo-map.md` — AUTO block regenerated (mode=content, `--ignore _bmad,_my_resources`). +37/-32 lines
  (removed stale `_artifacts/epic-15/`; added `backend/__about_video_infographics/` +
  `frontend/public/assets/about/`; file-count summaries updated for new INDEX.md files).
- `_my_resources/open_tasks/todo_list.md` — `## Open Work` manifest refreshed (Step 3.6, the one surgical
  `_my_resources/` carve-out): `fix_list.md` → `fix_list_admin_sudoadmin.md` (file renamed on disk);
  added `tdad_stack_install_guide.md` (task file on disk, was missing from manifest). Daniel's `## Todo list`
  prose + the task files themselves untouched.
- 40 new level-2 `INDEX.md` files: `.agent/skills/`, `.agents/{bmad,hooks,opencode-agents,scripts,templates}/`,
  `.claude/{commands,hooks,memory}/`, `.github/workflows/`, `.opencode/{agent,commands}/`,
  `backend/{agents,core,data,evals,middleware,observability,routers,schemas,scripts,services,tests,tia,tools,utils}/`,
  `docs/file_structure_rules/`, `firebase/tests/`, `frontend/{e2e,public,src,tests}/`, `load/{lib,scenarios}/`,
  `_bmad-output/{active-context,brainstorming,component-specs,implementation-artifacts,planning-artifacts,test-artifacts}/`.
  (3 additional INDEX.md files created in gitignored folders — `backend/_test_scripts/`,
  `backend/__about_video_infographics/`, `frontend/_test_scripts/` — live on disk only; linter sees them,
  git doesn't track them. No action needed.)

### Fresh_Workspace_BMAD — 22 files
- `docs/repo-map.md` — AUTO block regenerated (mode=auto, `--ignore _bmad,_my_resources`). +14 lines
  (added `_bmad-output/component-specs/` + `docs/gitnexus.md`; file-count summaries updated).
- 21 new level-2 `INDEX.md` files: `.agents/{bmad,hooks,opencode-agents,scripts,templates}/`,
  `.claude/{commands,hooks}/`, `.opencode/{agent,commands}/`, `backend/{agents,routers,schemas,services,tests,tools}/`,
  `docs/file_structure_rules/`, `_bmad-output/{active-context,component-specs,implementation-artifacts,planning-artifacts,test-artifacts}/`.

## Verification — `python .agents/scripts/check_maps.py --all`

| Workspace | AUTO | paths | coverage | INDEX paths | level-2 INDEX | depth-3 | conformance | hygiene |
|---|---|---|---|---|---|---|---|---|
| Lobby | clean | clean | clean | clean | **clean** | clean | clean | clean |
| AGY_AVIATIONCHAT | 🚩 | clean | clean | clean | 🚩 | clean | clean | hint |
| Fresh_Workspace_BMAD | clean | clean | clean | clean | **clean** | clean | clean | clean |
| RAG_Pipeline_AC | — | — | — | — | — | — | 🚩 NOT conformant | — |

**Lobby + Fresh = fully clean.** AGY has 2 pre-existing flags that are **code fixes** (outside this
doc-only workflow's scope) + 1 hint.

## 🚩 Deferred — 2 trivial code fixes (need Daniel's go-ahead; outside "docs only" scope)

These are pre-existing issues (not introduced by this run) that keep AGY from a fully clean lint. Both are
1-line additions to master maintenance scripts. The workflow guardrail says "edits docs/markdown only —
never code," so I did NOT apply them. Exact fixes:

### Fix 1 — `coverage/` AUTO-freshness flap (vendoring drift)
- **Symptom:** `--all` linter reports AGY AUTO block STALE on `coverage/`, but AGY's own `--root .` run is clean.
- **Root cause:** AGY's vendored `generate_repo_map.py` has `"coverage"` in `DEFAULT_IGNORES`; the lobby
  MASTER `.agents/scripts/generate_repo_map.py` does NOT. The `--all` linter uses the lobby master generator
  for every workspace's freshness comparison → it sees `frontend/coverage/` (istanbul build output) → STALE.
- **Fix:** add `"coverage"` to `DEFAULT_IGNORES` in lobby master `.agents/scripts/generate_repo_map.py`
  (line ~25, matching the vendored AGY/Fresh copies which already have it), then `/sync-agents` to push
  the fix to all project vendored copies.
- **After:** re-run `python .agents/scripts/check_maps.py --all` → AGY AUTO-freshness goes clean.

### Fix 2 — `.ruff_cache/` level-2 INDEX flag
- **Symptom:** linter flags `.ruff_cache/0.15.12/INDEX.md: missing` (level-2 folder requires an INDEX.md).
- **Root cause:** `.ruff_cache/` is a versioned build cache (the `0.15.12/` segment changes with the ruff
  version). It's not in `SCAN_IGNORES`, so the level-2 check flags it. Creating an INDEX there is futile —
  it re-flags when the version changes.
- **Fix:** add `".ruff_cache"` to `SCAN_IGNORES` in lobby master `.agents/scripts/check_maps.py` (line ~47),
  then `/sync-agents`.
- **After:** re-run linter → AGY level-2 INDEX presence goes clean.

### 🚩 Hint — AGY `active-context.md` (243 lines, no dated blocks)
- The prune logic keys on dated `**YYYY-MM-DD: …**` blocks; this file has none detectable. Can't
  mechanically archive. Flagged for Daniel's review (restructure into dated blocks, or trim manually).
  Not auto-pruned.

### 🚩 RAG_Pipeline_AC — NOT conformant
- Missing `GEMINI.md`, `.agents/`, scripts, `_artifacts/INDEX.md`, `docs/repo-map.md`,
  `workspace-standard.md`, open-tasks list, continuity brief. Per Guardrails "conformance first", no
  reconcile until it's standard. Separate build-out task.

## Task Checklist (final TodoWrite snapshot)
- [x] Step 0: run `check_maps.py --all` linter — drift detected across 4 workspaces
- [x] Step 0.5: fan-out worklist — lobby + AGY + Fresh (RAG flagged non-conformant)
- [x] Step 1: regenerate AUTO blocks (lobby mode=content; AGY mode=content; Fresh mode=auto)
- [x] Step 2: curated block drift-check — no curated edits needed (all changes are subfolders of documented top-level folders)
- [x] Step 3: audit INDEXes — lobby `_artifacts/INDEX.md` already reconciled for renames; depth-3 `_artifacts/opencode/_main/INDEX.md` fixed (2 rows, backticked folder names)
- [x] Step 3.5: context hygiene — lobby + Fresh within window; AGY hint (no dated blocks, can't auto-prune)
- [x] Step 3.6: open-tasks refresh — AGY `todo_list.md` `## Open Work` manifest updated (fix_list→fix_list_admin_sudoadmin, +tdad_stack_install_guide); lobby + Fresh already correct
- [x] Step 4: findings report + approval (Daniel directed completion: "finish the list" / "dont stop")
- [x] Step 5: applied edits (repo-maps, open-tasks manifest, 76 level-2 INDEXes, depth-3 INDEX)
- [x] Step 5.7: re-regenerated all 3 AUTO blocks after INDEX creation (file-count summaries changed)
- [x] Step 6: re-ran linter — lobby + Fresh clean; AGY has 2 deferred code-fix flags + 1 hint
- [x] Flagged 2 trivial code fixes (coverage + .ruff_cache) with exact diffs for Daniel

## Your Actions

**Do not `git add -A`** — there are pre-existing untracked/modified files in each repo that are NOT mine
(see notes below). Use the surgical `git add` commands.

### 1. Lobby (Sudo_Hatter_Command) — from `C:\Sudo_Hatter_Command`

```powershell
git add docs/repo-map.md `
  _artifacts/opencode/_main/INDEX.md `
  _artifacts/opencode/_main/2026-07-07_update-maps-fanout/ `
  .agent/skills/INDEX.md `
  .agents/bmad/INDEX.md .agents/hooks/INDEX.md .agents/opencode-agents/INDEX.md `
  .agents/scripts/INDEX.md .agents/templates/INDEX.md `
  .claude/commands/INDEX.md .claude/hooks/INDEX.md `
  .opencode/agent/INDEX.md .opencode/commands/INDEX.md `
  _routing-canary/control/INDEX.md _routing-canary/skills/INDEX.md

git commit -m "docs: /1_update-maps — refresh lobby repo-map + 12 level-2 INDEXes + opencode depth-3 INDEX"
```

**NOT mine (leave staged/unstaged as-is):** `.agents/scripts/check_maps.py` (pre-existing mod),
`.agents/workflows/1_update-maps.md` (pre-existing mod — the workflow update you mentioned),
`Projects/AGY_AVIATIONCHAT` + `Projects/Fresh_Workspace_BMAD` (submodule pointers),
`.agents/skills/1_update-maps/` (pre-existing untracked),
`_my_resources/open_tasks/tdad_stack_install_guide.md` (your task file — protected),
`requirements-tdad.txt` + `requirements.txt` (pre-existing untracked).

### 2. AGY_AVIATIONCHAT — from `C:\Sudo_Hatter_Command\Projects\AGY_AVIATIONCHAT`

```powershell
git add docs/repo-map.md `
  _my_resources/open_tasks/todo_list.md `
  ':(glob)**/INDEX.md'

git commit -m "docs: /1_update-maps — refresh repo-map + open-tasks manifest + 40 level-2 INDEXes"
```

**NOT mine:** the `D _my_resources/open_tasks/tdad_stack_install_guide.md` deletion is your file move
(rename to `admin_graph_rag_2.6.md` per the linter's rename detection) — handle it separately or include
it in this commit if you want the rename to land together with the manifest fix. The
`:(glob)**/INDEX.md` pathspec adds all 40 new INDEX.md files git sees; the 3 in gitignored folders
(`backend/_test_scripts/`, `backend/__about_video_infographics/`, `frontend/_test_scripts/`) stay local
(linter reads disk, so it's happy).

### 3. Fresh_Workspace_BMAD — from `C:\Sudo_Hatter_Command\Projects\Fresh_Workspace_BMAD`

```powershell
git add docs/repo-map.md ':(glob)**/INDEX.md'

git commit -m "docs: /1_update-maps — refresh repo-map + 21 level-2 INDEXes"
```

### 4. Re-anchor AFTER committing (so the next run's git-diff starts clean)

```powershell
python .agents/scripts/check_maps.py --set-anchor --all
```

### 5. Optional — apply the 2 deferred code fixes (makes AGY fully clean)

If you want AGY's lint fully clean, say "apply the 2 code fixes" and I'll amend the plan to cover them:
- Add `"coverage"` to `DEFAULT_IGNORES` in `.agents/scripts/generate_repo_map.py` (lobby master)
- Add `".ruff_cache"` to `SCAN_IGNORES` in `.agents/scripts/check_maps.py` (lobby master)
- Then `/sync-agents` to push both to project vendored copies, and re-run `check_maps.py --all`.

No `/sync-agents` needed from THIS run's doc edits — I did not modify any `.agents/*/INDEX.md` that
differs from what sync would produce (the 5 `.agents/{bmad,hooks,opencode-agents,scripts,templates}/INDEX.md`
I created at the lobby master are the canonical source; project vendored copies were created directly by
the subagents with identical content, so they're already in sync).
