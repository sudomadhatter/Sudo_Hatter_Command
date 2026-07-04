---
IsArtifact: true
ArtifactMetadata:
  title: Tier-2 local law — per-folder AGENTS.md + adapters, reading-order rule, check 8
  type: walkthrough
  date: 2026-07-03
---

# Walkthrough — Tier-2 local law (folder-level AGENTS.md)

## What this was
Daniel re-read the folder-as-workspace transcript plan and flagged a missed layer: per-folder
`AGENTS.md` files ("the AI reads AGENTS.md first, INDEX only for more info"). Landed as a **3-tier
model** (not every folder — that would drift and kill the beacon): Tier 1 floors already had brains;
**Tier 2 guarded infrastructure (`_artifacts/`, `_my_resources/`, `docs/`) got new ~15-line local-law
`AGENTS.md` files + 1-line `CLAUDE.md`/`GEMINI.md` adapters**; Tier 3 leaf content stays INDEX-only.
The teeth: harnesses auto-attach a nested memory file at the point of contact (Claude Code: nested
`CLAUDE.md`; Codex: nested `AGENTS.md`; Gemini: hierarchical) — so e.g. the `_my_resources/` READ-ONLY
law now self-enforces the moment any agent touches a file in there.

## What changed, file by file

**New (9 files, the actual feature):**
- `_artifacts/{AGENTS,CLAUDE,GEMINI}.md` — bucket law digest (work-from-cwd, `epic_<E>/<story>/`
  nesting, `tea/`, `_main/`, one-doc close, ledger duties); points at README/INDEX-header/rule as canon.
- `_my_resources/{AGENTS,CLAUDE,GEMINI}.md` — PROTECTED/read-only law + the one `/1_update-maps`
  `## Open Work` exception + the open_tasks/active-project pointers.
- `docs/{AGENTS,CLAUDE,GEMINI}.md` — what each doc is; AUTO-body regen-only; docs/ is NOT synced.

**Rule codified:**
- `AGENTS.md` (root) §1.7 — the reading-order rule: entering any folder, local `AGENTS.md` FIRST;
  `INDEX.md`/`README.md` only for inventory.
- `docs/workspace-standard.md` — new "folder-file tier model" subsection (Part 1) + format-checklist
  row + PATH CONTRACT row.

**Linter (master `.agents/`, synced):**
- `.agents/scripts/check_maps.py` — **check 8 (NON-FATAL hint)**: Tier-2 dirs present must carry
  `AGENTS.md` + both adapters; docstring 7→8 checks. **Plus a found-bug fix:** the stale-AUTO hint
  suggested `--output repo-map.md`, which resolves against **cwd** and silently writes a stray
  root-level `repo-map.md` (proven live during verification — it also mapped `.agents/` as the root).
  Hint now suggests `--root <root>` with no `--output`.
- `.agents/scripts/generate_repo_map.py` — root-resolution hardened to the same logic check_maps.py
  already had (master lives at `.agents/scripts/` → `parent.parent` landed on `.agents/`, not the repo).
- `.agents/workflows/1_update-maps.md` — stale "**six** checks" (was already wrong; there were seven)
  → eight, with the two hint checks named.
- `.agents/commands/1_update-maps.md` — same stale "six checks" → eight.

**Rot fixes:**
- `_artifacts/README.md` — dropped the abolished `task-list.md` row (one-doc rule, 2026-06-27), fixed
  `_docs/`→`docs/`, added the AGENTS.md pointer.
- `docs/repo-map.md` — AUTO body regenerated (new files), mode-preserving.

**Walkthrough deliverable (Daniel-directed, protected-area edit explicitly authorized):**
- `_my_resources/diagrams_guides/system/file_folder_structure+maintaining.md` — new §1b tier-model
  section (reading order + tier table + auto-attach mermaid); linter diagram 7→8 checks **and its
  check labels corrected to the real check list** (old C1/C3/C6 labels described checks that don't
  exist); §5 close step → one-doc model; §8 quick-ref rows; docs/ node fixed
  (master-implementation-plan lives in `_my_resources/docs/`, not `docs/`).

**Propagation:** `/sync-agents` → lobby surfaces + both global caches, then `-Target` AGY + Fresh.

## Test output (actual, pasted)

Check 8 green with the new files (lobby lint):
```
[tier-2 local law]  (hint only - does not fail the lint)
  [ok] guarded dirs carry AGENTS.md + adapters
```
Negative test — removed `docs/GEMINI.md`, hint fires with the exact file, then restored:
```
[tier-2 local law]  (hint only - does not fail the lint)
  [hint] docs/: no local law - missing GEMINI.md (tier model, workspace-standard.md Part 1)
```
Regen bug proven then fixed — the linter's own suggested command wrote a stray root map titled
`# Repo Map — .agents`; after the fix, regen lands at `docs/repo-map.md` and freshness is clean:
```
repo-map written: C:\...\Sudo_Hatter_Command\docs\repo-map.md  (mode=content, threshold=8)
[AUTO block freshness]
  [ok] clean
```
Sync verified byte-identical (md5) across master + AGY + Fresh:
```
a62ca0aadc1d4c4f788914ce999a1ab0  check_maps.py        (x3)
0e9b9f7650bdbe86b9db0fc5c479ea0a  generate_repo_map.py (x3)
```
Final full lobby lint after close-out ledger rows: exit 0 (pasted in chat).

## Found along the way (not this session's scope)
- The 2026-07-03 `artifact-routing-fix` session forgot its depth-3 `_main/INDEX.md` row — added it
  (the linter caught it; bookkeeping only).
- The diagram doc's old linter labels (C1–C7) described checks that never existed — corrected.

## Follow-ups (flagged, not done)
- **Per-project Tier-2 rollout**: AGY + Fresh get their own 9 Tier-2 files + vendored
  `workspace-standard.md` refresh (docs/ is not synced — deliberate per-project pass). Until then
  their lints show the check-8 hint (non-fatal by design).
- Promote check 8 → fatal conformance (check 6) once every workspace carries the files.
- 4 unconverted projects (JETCHAT, B-L-WorldWide, NEXGen-Films, OpenChat-Openrouter) still lack
  Tier-1 brains — pre-existing backlog.

## Task Checklist
- [x] Read newest artifact-routing-fix walkthrough + source files
- [x] implementation_plan.md written (pre-approved by Daniel in chat)
- [x] 9 Tier-2 files created (_artifacts/, _my_resources/, docs/)
- [x] Reading-order rule in root AGENTS.md §1.7
- [x] Tier model in workspace-standard.md (subsection + checklist + PATH CONTRACT)
- [x] check_maps.py check 8 + regen-hint bugfix; generate_repo_map.py root bugfix
- [x] Stale check-counts fixed (workflow + command); _artifacts/README.md rot fixed
- [x] repo-map AUTO regenerated; lint green incl. negative test
- [x] /sync-agents lobby + globals + AGY + Fresh (md5-verified)
- [x] Diagram doc updated (Daniel-directed)
- [x] Close-out: INDEX rows (incl. missed routing-fix depth-3 row), active-context hand-off

## Your Actions
Three repos, all on **`main_debug`**. Explicit paths only. Pre-existing NOT-mine work excluded by
these commands: lobby `_my_resources/migrations/` (untracked, Daniel's); AGY
`_my_resources/open_tasks/sprint-dependency-map.md`, `scripts/autopilot-dev-story.ps1`, and the
untracked `autopilot_glm.md` pair. Fresh is clean apart from this sync.

**Lobby** (`Sudo_Hatter_Command`):
```bash
git add AGENTS.md docs/workspace-standard.md docs/repo-map.md \
        docs/AGENTS.md docs/CLAUDE.md docs/GEMINI.md \
        _artifacts/AGENTS.md _artifacts/CLAUDE.md _artifacts/GEMINI.md _artifacts/README.md \
        _my_resources/AGENTS.md _my_resources/CLAUDE.md _my_resources/GEMINI.md \
        "_my_resources/diagrams_guides/system/file_folder_structure+maintaining.md" \
        .agents/scripts/check_maps.py .agents/scripts/generate_repo_map.py \
        .agents/workflows/1_update-maps.md .agents/commands/1_update-maps.md \
        .claude/commands/1_update-maps.md .opencode/commands/1_update-maps.md \
        _artifacts/INDEX.md _artifacts/_main/INDEX.md _artifacts/_main/active-context.md \
        _artifacts/_main/2026-07-03_tier2-local-law/
git commit -m "feat(routing): tier-2 local-law AGENTS.md + adapters; reading-order rule; check 8; regen bugfixes"
python .agents/scripts/check_maps.py --set-anchor
```

**AGY** (`Projects/AGY_AVIATIONCHAT`):
```bash
git add .agents/scripts/check_maps.py .agents/scripts/generate_repo_map.py \
        .agents/workflows/1_update-maps.md .agents/commands/1_update-maps.md \
        .claude/commands/1_update-maps.md .opencode/commands/1_update-maps.md
git commit -m "chore(toolkit): sync check_maps check-8 + regen bugfixes from lobby master"
```

**Fresh** (`Projects/Fresh_Workspace_BMAD`):
```bash
git add .agents/scripts/check_maps.py .agents/scripts/generate_repo_map.py \
        .agents/workflows/1_update-maps.md .agents/commands/1_update-maps.md \
        .claude/commands/1_update-maps.md .opencode/commands/1_update-maps.md
git commit -m "chore(toolkit): sync check_maps check-8 + regen bugfixes from lobby master"
```
