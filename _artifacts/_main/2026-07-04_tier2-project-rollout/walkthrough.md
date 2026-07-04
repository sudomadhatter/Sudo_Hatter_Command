---
IsArtifact: true
ArtifactMetadata:
  title: Tier-2 local law — per-project rollout to AGY_AVIATIONCHAT + Fresh_Workspace_BMAD
  type: walkthrough
  date: 2026-07-04
---

# Walkthrough — Tier-2 local law: project rollout (AGY + Fresh)

## What this was
The flagged follow-up of [`2026-07-03_tier2-local-law/`](../2026-07-03_tier2-local-law/walkthrough.md),
directed by Daniel ("it also needs to be done for aviationchat and fresh-workspace … please finish the
job"). The lobby already had the 3-tier model; both live projects now carry it too: **9 Tier-2 files
each** (`_artifacts/`, `_my_resources/`, `docs/` → local-law `AGENTS.md` + 1-line `CLAUDE.md`/`GEMINI.md`
adapters) + the **vendored `workspace-standard.md` refresh** (docs/ is not synced — this was the
deliberate per-project pass). The toolkit half (check 8/9, regen fixes) was already in both repos from
the previous session's `/sync-agents` (AGY `7e279e22`, Fresh `9d9c44d` — both were clean at session start).

## What changed, file by file

**AGY_AVIATIONCHAT (12 files):**
- **NEW** `_artifacts/{AGENTS,CLAUDE,GEMINI}.md` — bucket law digested from AGY's own canon: epic
  nesting `epic_<E>/<story>/`, **`tea/` bucket**, local `_main/` for system/infra, dated one-offs,
  one-doc close, continuity brief = `_bmad-output/active-context/active-context.md`, home-base twin
  bucket `_artifacts/aviationChat-AGY/`.
- **NEW** `_my_resources/{AGENTS,CLAUDE,GEMINI}.md` — PROTECTED/read-only law + the one `/1_update-maps`
  `## Open Work` exception + the "excluded from `--ignore _bmad,_my_resources` regen + `.gitnexusignore`
  — don't fix it" note.
- **NEW** `docs/{AGENTS,CLAUDE,GEMINI}.md` — verified-shelf law: repo-map CURATED/AUTO split + the
  project's documented regen command, vendored-standard "never hand-edit, refreshed from canon"
  rule, `.maps-state.json`, `file_structure_rules/`, promotion-only.
- `docs/workspace-standard.md` — refreshed to current lobby canon (was a stale pre-tier-model revision;
  verified no project-specific edits before overwrite — the old copy's only delta vs Fresh's was
  vintage, not adaptation).
- `AGENTS.md` — §2 START HERE gained the reading-order rule (lobby §1.7 twin); §5 close-out switched to
  the one-doc model (ONE `walkthrough.md` ending in `## Task Checklist` + `## Your Actions`, **no
  separate `task-list.md`**).
- `_artifacts/README.md` — same one-doc alignment (merged the walkthrough row, dropped the abolished
  `task-list.md` row) + the `AGENTS.md` law pointer (lobby-README parity).
- `_artifacts/INDEX.md` — session row appended.
- `docs/repo-map.md` — AUTO body regenerated (mode=content; picks up the new law files AND the
  pre-existing `journeys/`+`tia/` drift the last fan-out surfaced).

**Fresh_Workspace_BMAD (12 files):** same set, adapted — clean-bmad-workspace naming, **no `tea/`**
bucket (not in its canon), **no GitNexus** notes (no index in that repo), docs shelf lists
`tech-stack.md` + `skills-registry.md`, regen command `--ignore _bmad`, home-base twin bucket
`_artifacts/clean-bmad-workspace/`. Its INDEX placeholder row ("no project-local sessions yet") was
replaced by the real first row + a residual pointer line. repo-map regenerated mode=auto.

**Lobby (5 files):** this session folder (plan + walkthrough), `_artifacts/INDEX.md` row,
`_main/INDEX.md` row, `_main/active-context.md` hand-off block. (Lobby repo-map: see Test output —
regenerated only if the lint flagged it.)

## Test output (actual, pasted)

Check 8 green in BOTH projects (each with its documented ignore set):
```
[tier-2 local law]  (hint only - does not fail the lint)
  [ok] guarded dirs carry AGENTS.md + adapters (redirects verified)
```
Negative test (AGY) — removed `docs/GEMINI.md`, exact hint fired, restored:
```
[tier-2 local law]  (hint only - does not fail the lint)
  [hint] docs/: no local law - missing GEMINI.md (tier model, workspace-standard.md Part 1)
```
Vendored standard hash-identical ×3 after refresh (lobby canon + AGY + Fresh):
```
67C1317DC20FC6F8678F7D3A944D08901D26E17E795AA21A76D0E8B3B5B748D6  (x3)
```
repo-map AUTO regen, mode-preserving, freshness clean after:
```
repo-map written: ...\AGY_AVIATIONCHAT\docs\repo-map.md  (mode=content, threshold=8)
repo-map written: ...\Fresh_Workspace_BMAD\docs\repo-map.md  (mode=auto, threshold=8)
[AUTO block freshness]
  [ok] clean        (both projects)
```

## Deliberately NOT touched (pre-existing backlog — a future `/1_update-maps` run)
- AGY: 14 depth-3 INDEX gaps (epic_8/epic_11/tea/_main rows), the 243-line active-context hint, and the
  stale GitNexus index (`1fc85d1` vs HEAD — re-index AFTER committing, per the standing rule).
- Fresh: dead CURATED path `_bmad/bmm/stories` in repo-map.md (curated prose = a human/update-maps call).
- The 4 unconverted projects (JETCHAT, B-L-WorldWide, NEXGen-Films, OpenChat-Openrouter) — still no
  Tier-1 brains; check 8 stays a NON-FATAL hint until they convert (then promote to conformance).

## Found along the way (not this session's scope)
- **Fresh is checked out on `main`, not `main_debug`** (both branches exist; lobby + AGY sit on
  `main_debug`). Flagged rather than switched — and the commit that landed (`52a5c93`) went to `main`.
- AGY `_my_resources/README.md` still lists `_Open_Task/` among its subfolders — renamed to
  `open_tasks/` on 2026-06-25. Protected area, not corrected without direction.
- **Two lanes converged in AGY (again — cf. 8.22.2):** while this session closed out, the live story-8.23.2
  lane committed `dc58a20e`, sweeping this session's 14 tier-2 files into its story commit (16:54:01;
  Fresh's `52a5c93` landed 8s earlier). Content diff-verified intact — the law files at HEAD are
  byte-identical to what this session wrote; no harm, just a mixed-concern commit for the record.

## Task Checklist
- [x] Read commit 1bb738e + parent tier2-local-law plan/walkthrough (scope = the flagged follow-up)
- [x] implementation_plan.md written (pre-approved: parent session + Daniel's direction in chat)
- [x] AGY: 9 Tier-2 files created, law digested from AGY canon (tea/, _main/, BMAD brief)
- [x] Fresh: 9 Tier-2 files created, law digested from Fresh canon (no tea/, no GitNexus)
- [x] Vendored workspace-standard.md refreshed ×2 (hash-verified against canon)
- [x] Reading-order rule → both root AGENTS.md §2; one-doc close → both §5 + _artifacts/README.md
- [x] repo-map AUTO regenerated ×2 (mode-preserving); AUTO freshness [ok] ×2
- [x] check 8 [ok] (redirects verified) ×2 + negative test fired/restored (AGY)
- [x] Ledgers: AGY + Fresh INDEX rows; lobby INDEX + _main/INDEX + active-context hand-off

## Your Actions
**AGY + Fresh are already committed** (your lane did it mid-close-out: AGY `dc58a20e` on `main_debug`,
bundled with story 8.23.2; Fresh `52a5c93` on `main`). What's left:

**Lobby** (`Sudo_Hatter_Command`) — the 5 session files are already **staged**; the lobby repo-map
needed no regen (lint came back clean), so the staged set is complete:
```bash
git commit -m "feat(routing): tier-2 rollout session ledger — AGY + Fresh carry the local law"
python .agents/scripts/check_maps.py --set-anchor
```

**AGY** (`Projects/AGY_AVIATIONCHAT`) — after the story-8.23.2 lane settles (it was still writing
`ExamInsightsPanel` files when this closed):
```bash
python .agents/scripts/check_maps.py --root Projects/AGY_AVIATIONCHAT --ignore _bmad,_my_resources --set-anchor
node .gitnexus/run.cjs analyze     # from the AGY root — clears the stale-index hint
```
(`--set-anchor` dirties the tracked `docs/.maps-state.json` — fold it into the lane's next commit.)

**Fresh** (`Projects/Fresh_Workspace_BMAD`):
```bash
python .agents/scripts/check_maps.py --root Projects/Fresh_Workspace_BMAD --ignore _bmad --set-anchor
```
(Same `.maps-state.json` note; and `52a5c93` sits on `main` — cherry-pick/merge to `main_debug` if you
want the branch model observed there.)
