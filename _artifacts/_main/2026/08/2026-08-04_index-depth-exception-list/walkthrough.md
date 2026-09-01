# Walkthrough — Named INDEX-depth exception lists, `.agents/` linting, and the `adk-prompting` retirement

- **Date:** 2026-08-04
- **Workspace:** home base (lobby)
- **Plan:** [`implementation_plan.md`](implementation_plan.md) — approved by Daniel

---

## What this was

The INDEX-coverage rule stops at **level 2**, with `_artifacts/` hardcoded as its one deeper exception.
Daniel has more folders that need depth-3 indexing and asked whether `.agents/` should be one of them.

**It shouldn't** — and the audit is the interesting part of this session. `.agents/` already carried an
`AGENTS.md`, an `INDEX.md`, both adapters, and an `INDEX.md` in all ten subfolders. What it lacked was
**enforcement**: check 2.5 blanket-skipped every dot-dir, a guard written for `.ruff_cache` that also made
the entire master toolkit invisible to the linter. Depth wasn't the need; being checked at all was.

Measuring before recommending settled it — six of the ten subfolders are completely flat, so there is no
depth 3 to index:

| Subfolder | Subdirs | Max depth | | Subfolder | Subdirs | Max depth |
|---|---|---|---|---|---|---|
| `commands/` | 0 (55 files) | 2 | | `skills/` | 44 | 5 |
| `workflows/` | 0 (25 files) | 2 | | `bmad/` | 6 | 5 |
| `rules/` | 0 (21 files) | 2 | | `scripts/` | 3 | 3 |
| `opencode-agents/` | 0 (13 files) | 2 | | `templates/` | 1 | 4 |
| `hooks/` · `reference/` | 0 (2 each) | 2 | | | | |

The four deep ones don't want INDEXes either: `skills/` is self-describing through `SKILL.md` frontmatter
(the harness publishes all 44 descriptions into every session — a hand-written duplicate would only drift),
`bmad/` is regenerated on update, and `templates/project-template/` is a scaffold carrying its own control
files.

## What changed

### 1. Named exception lists — `.agents/scripts/check_maps.py`

The exception was hardcoded in two places. It is now two named sets, so opting a folder in is a one-line
edit rather than a code change:

```python
DEPTH3_DIRS = {"_artifacts"}        # index one level deeper: skipped by check 2.5, walked by check 7
DOT_CONTENT_DIRS = {".agents"}      # dot-dirs that are CONTENT, not tool cache — scanned normally
```

Three call sites rewired:
- **check 2.5 level-1 dot-skip** → `startswith(".") and name not in DOT_CONTENT_DIRS`
- **check 2.5 depth-3 skip** → `name in DEPTH3_DIRS` (was `== "_artifacts"`)
- **check 7** → now loops `DEPTH3_DIRS` (body extracted to `_check_depth3_tree`) instead of walking a single
  hardcoded `root / "_artifacts"`

The **level-2 dot-skip stays blanket** — that is what keeps `.agents/.claude` and `.agents/.gitnexus`
correctly exempt while `.agents/` itself gets scanned.

### 2. `.agents/` Tier-1 law now enforced — check 6

`workspace-standard.md` has listed `.agents/` as a Tier-1 floor since the tier model landed, but nothing
verified it. Added four assertions: `.agents/AGENTS.md` · `INDEX.md` · `CLAUDE.md` · `GEMINI.md`.

### 3. `adk-prompting` retired — 4 directories deleted

Investigating the duplicate turned up that **neither copy was about Google ADK**. Both were Antigravity
prompt-authoring guides misfiled in an ADK bucket; the long one's frontmatter said so outright
(`name: antigravity-master-architect`). Deleted:

| Path | Size | State |
|---|---|---|
| `.agents/skills/adk-prompting/SKILL.md` | 1,824 B | loaded; lossy trim of the long one |
| `.agents/skills/5_adk_skills/adk-prompting/SKILLS.md` | 5,206 B | **plural filename → never loadable** |
| `.claude/skills/adk-prompting/` | 1,824 B | mirror |
| `.claude/skills/5_adk_skills/adk-prompting/` | 5,206 B | mirror |

**The sync manifest was NOT touched** — and an earlier edit removing `"adk-prompting"` from it was reverted.
`.agents/.sync-manifest.json` is the record of what the *last* sync wrote, so the *next* run can purge its
own retired output (`Invoke-ManifestPurgeDir`, sync-agents.ps1 §PURGE POLICY; the file's own header says
"Do not hand-edit"). Deleting the entry destroys the proof that a prior sync created those directories,
which would have silently disabled the very purge that propagates this deletion outward. Left intact, the
next `/sync-agents` computes `was − now` and removes the retired skill dir everywhere it wrote one.

**Why deleted rather than repaired.** Three independent reasons:
1. Its substance is already covered, better, by `v3-prompt-architecture` — 20 named failure modes against
   its 4, with direct overlaps ("Instruction Drift" → #1 Pink Elephant, "Contextual Amnesia" → #2 Tool
   Amnesia). Worse, **v3 #10 contradicts and corrects it**: Flash Lite treats XML tags as lower-salience
   than markdown headings, so its blanket "always use XML for Gemini 3.0" is wrong advice we'd be storing
   next to the correction.
2. It taught the exact misconception the house standard exists to prevent — that `.agents/workflows/` holds
   the active invocable playbooks. `workspace-standard.md` §"Command sync": *"Antigravity confusingly calls
   its invocable units 'workflows,' but our source is always `commands/` — name-matching that to
   `.agents/workflows/` is the exact bug this rule prevents."*
3. Its "Reference Fetching" section pointed at `examples/golden-workflow.md` and `references/xml-schema.md`.
   Neither exists; the folder held one file.

**Salvage:** the one idea not already in `v3-prompt-architecture` — sampling parameters as part of the
prompt artifact — was grafted in as **#21 Sampling Parameters Are Part of the Prompt** (temperature 1.0
baseline, thinking level High/Low by task, cross-referenced to #10).

### 4. Documentation — `docs/workspace-standard.md`

- PATH CONTRACT: the single "Depth-3 epic INDEX" row became three — the level-2 house rule, then
  `DEPTH3_DIRS` and `DOT_CONTENT_DIRS` as its two named exception lists.
- Tier model: a paragraph stating `.agents/` is a Tier-1 floor that gets linted like one, why dot-dirs are
  otherwise skipped, and why it stops at depth 2.

## Verification — real output

Baseline before any edit: `level-2 INDEX`, `depth-3 INDEX`, `structure conformance` all `[ok] clean`.
After, across all three conformant workspaces (`check_maps.py --all`):

```
MAP & INDEX DRIFT LINT  (home base: Sudo_Hatter_Command)
[level-2 INDEX presence]      [ok] clean
[depth-3 _artifacts INDEX]    [x] _artifacts/_main/INDEX.md: missing row for `2026-08-04_index-depth-exception-list/`
[structure conformance]       [ok] clean

MAP & INDEX DRIFT LINT  (BMAD project: AGY_AVIATIONCHAT)
[level-2 INDEX presence]      [ok] clean
[depth-3 _artifacts INDEX]    [x] _artifacts/epic_14/INDEX.md: missing row for `2026-06-26_autopilot-14-5/`
[structure conformance]       [ok] clean

MAP & INDEX DRIFT LINT  (BMAD project: Fresh_Workspace_BMAD)
[level-2 INDEX presence]      [ok] clean
[depth-3 _artifacts INDEX]    [ok] clean
[structure conformance]       [ok] clean
```

**Zero new drift.** The lobby hit is this session's own folder (resolved by the INDEX row below); AGY's
`epic_14` hit and the stale AUTO blocks / dead paths reported elsewhere in the run are **pre-existing** and
untouched by this work — they belong to `/update-maps-indexes`.

`.agents/` is now inside the scan and passes: all ten subfolder INDEXes present, all four law files present.

## Open items — need Daniel's call

Found during the housecleaning sweep, **not** actioned:

1. **`5_adk_skills/` nesting hides two good skills.** The harness does not recurse into nested skill dirs,
   so `adk-agent-development` and `adk-testing-patterns` are **invisible** — absent from the session's skill
   roster. Both are genuine and current (each declares *"Updated for ADK 1.26.0"*, matching
   `backend/requirements.txt:13` exactly). Flattening them up into `skills/` would restore them, but it
   touches `.sync-manifest.json`, four platform caches, and three vendored project copies.
2. **DONE — all 12 vendored copies deleted by hand** (Daniel authorized, same session). `git rm -r` by
   explicit path in each repo, so removal + staging were one operation and no other lane's files were
   touched (all three trees verified clean beforehand: AGY `main_debug`, Fresh `main_debug`,
   B-L-WorldWide `main`, 0 dirty files each). **16 directories gone total** — 4 lobby + 12 project — with
   the two genuine ADK skills intact in all 8 `5_adk_skills/` locations and no empty dirs orphaned.
   Commits are Daniel's (⚠️ B-L-WorldWide is on `main` — OWNER-ONLY per git-policy).

   Kept for the record, because it governs every future skill retirement — deletion propagation is
   **surface-specific**, not the blanket "additive, nothing propagates" stated earlier:

   | Surface | Deletion propagates? | Mechanism |
   |---|---|---|
   | `.claude/skills/` (lobby + every project) | **YES** | manifest-tracked per skill FOLDER — Claude Code turns every `SKILL.md` into a typeable slash command, so a retired skill dir is a command ghost and gets the ownership-proven purge |
   | `.claude/commands` · `.opencode/commands` | **YES** | ownership-proven name purge |
   | opencode / Antigravity / Codex global caches | **YES** | mirror-exact (except `bmad-*`) |
   | `Projects/<name>/.agents/skills/` (vendored source) | **NO** | vendor is additive `/E` **by design** — the vendored `.agents` is a HYBRID holding project-owned `rules/` and `skills/`; a blanket purge there would delete each project's own files |

   So one `/sync-agents` removes the *loadable* copies everywhere. What survives is the dormant vendored
   source dir in each project, which needs a manual delete per repo. Note B-L-WorldWide's manifest has **0**
   references — it is a pre-manifest ghost there, so only the manual delete reaches it.
3. ~~Two orphan mirrors~~ — **retracted, both were false positives.** The scan compared `.agents/skills/`
   against `.claude/skills/` only, and missed two legitimate master locations:
   - `sudo-merge-epic-workingtrees` — master is `.agents/commands/sudo-merge-epic-workingtrees.md`
     (9,878 B). The sync generates the 832 B `.claude/skills/<name>/SKILL.md` stub from it; timestamps match
     the last sync run. Correctly wired, actively used.
   - `gitnexus` — a 6-sub-skill bundle whose master is `.agents/.claude/skills/gitnexus/`.

   Nothing to promote, nothing to delete.
4. **Frontmatter drift, cosmetic:** 9 skills have no `name:` field and 4 have `name:` ≠ folder name. Proven
   harmless — the harness keys on the **folder** name (`3_voice-ai-development` appears under its numeric
   prefix though its frontmatter says `voice-ai-development`). Normalize or leave.

## Task Checklist

- [x] `DEPTH3_DIRS` + `DOT_CONTENT_DIRS` added; 3 call sites rewired
- [x] `.agents/` Tier-1 law files asserted in check 6
- [x] 4 `adk-prompting` dirs deleted + dropped from the sync manifest
- [x] Parameter-tuning salvage grafted into `v3-prompt-architecture` as #21
- [x] `docs/workspace-standard.md` PATH CONTRACT rows + tier-model note
- [x] `check_maps.py --all` — zero new drift across all 3 conformant workspaces
- [x] `walkthrough.md` + `_artifacts/INDEX.md` row + `_main/INDEX.md` row + `active-context.md`

## Your Actions

`v3-prompt-architecture`'s mirror in `.claude/skills/` is now stale by one section — the master was edited,
per the never-edit-a-mirror rule. Re-sync, then commit:

```powershell
/sync-agents
git add .agents/scripts/check_maps.py .agents/.sync-manifest.json .agents/skills/v3-prompt-architecture/SKILL.md docs/workspace-standard.md .agents/skills/5_adk_skills .claude/skills _artifacts/_main/2026-08-04_index-depth-exception-list _artifacts/INDEX.md _artifacts/_main/INDEX.md _artifacts/_main/active-context.md
git commit -m "feat(maps): named INDEX-depth exception lists + lint .agents/ as the Tier-1 floor it is

DEPTH3_DIRS and DOT_CONTENT_DIRS replace the _artifacts hardcode at 3 call
sites, so opting a folder into deeper indexing is a one-line edit. .agents/
was invisible to check 2.5 via a dot-dir guard meant for .ruff_cache; it is
now scanned and its four Tier-1 law files are asserted. Retires the
adk-prompting skill (4 copies) - an Antigravity guide misfiled as ADK, whose
content v3-prompt-architecture already covers and partly corrects; its one
unique idea survives as v3 #21. Zero new drift across all 3 workspaces."
```

### Then the three project repos (deletions already staged by `git rm -r`)

```powershell
git -C Projects\AGY_AVIATIONCHAT commit -m "chore(skills): retire adk-prompting (Antigravity guide misfiled as ADK)"
git -C Projects\Fresh_Workspace_BMAD commit -m "chore(skills): retire adk-prompting (Antigravity guide misfiled as ADK)"
```

⚠️ **B-L-WorldWide is checked out on `main`** — OWNER-ONLY under `.agents/rules/git-policy.md`, so that one
is yours to run directly (or branch it first):

```powershell
git -C Projects\B-L-WorldWide commit -m "chore(skills): retire adk-prompting (Antigravity guide misfiled as ADK)"
```

Its 4 deletions are staged and waiting either way. Note B-L-WorldWide's sync manifest had **0**
`adk-prompting` references (pre-manifest ghost), which is why the manual delete was the only thing that
could reach it — a sync alone never would have.
