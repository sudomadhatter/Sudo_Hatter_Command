# Implementation Plan — Named exception lists for INDEX depth + `.agents/` visibility

- **Date:** 2026-08-04
- **Workspace:** home base (lobby) — master `.agents/` + canonical `docs/workspace-standard.md`
- **Owner:** Daniel (chair) · engineer: Claude
- **Status:** AWAITING APPROVAL

---

## 1. Why

`check_maps.py` enforces INDEX coverage to **level 2**, with `_artifacts/` hardcoded as the one
depth-3 exception. Two problems:

1. **The exception is hardcoded in two places** ([check_maps.py:374](../../../.agents/scripts/check_maps.py#L374)
   and [:392](../../../.agents/scripts/check_maps.py#L392)), so adding a folder that needs deeper
   indexing means a code change in both spots. Daniel has more folders to add.
2. **`.agents/` is invisible to the linter.** Check 2.5 blanket-skips any dir starting with `.`
   ([:372](../../../.agents/scripts/check_maps.py#L372)) — a guard added for build caches
   (`.ruff_cache/0.15.21/`) that also exempts the master toolkit. All 10 of its subfolder INDEXes
   and its Tier-1 law files are maintained on trust alone.

Audit finding (from the depth measurement): `.agents/` does **not** need deeper indexing — 6 of its
10 subfolders are completely flat, `skills/` is self-describing via SKILL.md frontmatter, `bmad/` is
foreign-owned, and `templates/project-template/` is a scaffold. Depth 2 is correct. It needs
*enforcement*, not depth.

## 2. Scope — what changes

### A. Named exception lists (`.agents/scripts/check_maps.py`)

Replace both hardcodes with module-level named sets beside the other config constants (~line 100):

```python
# Dirs that index to DEPTH 3 instead of stopping at level 2 (see workspace-standard.md PATH CONTRACT).
# Each is skipped by check 2.5 and walked by check 7 instead. Add a folder here to opt it in.
DEPTH3_DIRS = {"_artifacts"}

# Dot-dirs that are CONTENT, not tool cache — scanned by check 2.5 like any normal folder.
# Everything else starting with "." stays skipped (.ruff_cache, .pytest_cache, .gitnexus, ...).
DOT_CONTENT_DIRS = {".agents"}
```

- `check_level2_indexes` line 374: `if p1.name == "_artifacts"` → `if p1.name in DEPTH3_DIRS`
- `check_level2_indexes` line 372: dot-skip becomes
  `p1.name.startswith(".") and p1.name not in DOT_CONTENT_DIRS`
- `check_depth3_indexes` line 392: loop over `DEPTH3_DIRS` instead of the single `root / "_artifacts"`

**Level-2 dot-skip (line 377) stays blanket** — that keeps `.agents/.claude` and `.agents/.gitnexus`
correctly exempt while `.agents/` itself is scanned.

### B. `.agents/` Tier-1 law verified (`check_conformance`, ~line 520)

Add four `need()` assertions next to the existing `.agents` toolkit-dir check:
`.agents/AGENTS.md` · `.agents/INDEX.md` · `.agents/CLAUDE.md` · `.agents/GEMINI.md`.
The standard already declares `.agents/` a Tier-1 floor ([workspace-standard.md:77](../../../docs/workspace-standard.md#L77));
nothing enforced it.

### C. Documentation (`docs/workspace-standard.md`)

- PATH CONTRACT: retitle the "Depth-3 epic INDEX" row to name `DEPTH3_DIRS` as the opt-in mechanism
  rather than describing `_artifacts/` as the sole hardcoded case.
- Tier model (Part 1): one line stating `.agents/` is a scanned dot-dir, and that dot-dirs are
  otherwise treated as caches.

### D. Bug fix — misnamed skill file

`.agents/skills/5_adk_skills/adk-prompting/SKILLS.md` → `SKILL.md` (plural typo). The Agent Skills
standard requires `SKILL.md`, so **the master copy is currently unloadable**; its two siblings in the
same folder are named correctly.

## 3. Blast radius — verified zero new drift

Baseline `check_maps.py` run today: **level-2 INDEX, depth-3 INDEX, and structure conformance all
`[ok] clean`.** After the change:

- All 10 `.agents/` subfolders (`bmad`, `commands`, `hooks`, `opencode-agents`, `reference`, `rules`,
  `scripts`, `skills`, `templates`, `workflows`) already have an `INDEX.md` → check 2.5 still clean.
- All 4 `.agents/` law files already exist → check 6 still clean.

This is pure future-proofing: it catches the *next* subfolder added without an INDEX, and catches
BMAD's regeneration wiping `.agents/bmad/INDEX.md`.

## 4. Explicitly OUT of scope — needs your call

Two things I found that are **not** small, so I am not touching them:

1. **Flattening `skills/5_adk_skills/`.** It is the only dir under `skills/` with no `SKILL.md` — a
   grouping bucket, not a skill, and undescribed by the standard. But it is registered in
   `.agents/.sync-manifest.json:61`, so moving it ripples through the sync engine, four platform
   caches, and every project's vendored copy. Recommend a separate task.
2. **Duplicate `adk-prompting` skill.** `.claude/skills/` contains **two**: `adk-prompting/SKILL.md`
   (1,824 B) and `5_adk_skills/adk-prompting/SKILLS.md` (mirror of the 5,206 B master). The harness is
   loading the 1,824 B one — which is *not* the master. That inverts the "master is the only source of
   authorship" law and needs you to say which is canonical before anything is deleted.

## 5. Steps

1. Add `DEPTH3_DIRS` + `DOT_CONTENT_DIRS` constants; rewire the three call sites (A).
2. Add the four `need()` assertions (B).
3. Rename `SKILLS.md` → `SKILL.md` (D).
4. Update `docs/workspace-standard.md` (C).
5. Run `python .agents/scripts/check_maps.py` — confirm the three checks stay `[ok] clean`.
6. Run `python .agents/scripts/check_maps.py --root Projects/Fresh_Workspace_BMAD` — confirm the
   template is clean under the new rules too.
7. Propagate: `check_maps.py` rides `/sync-agents` (living-template-sync rule) — flag for Daniel to run.
8. Close with `walkthrough.md` + `_artifacts/INDEX.md` row + `active-context.md` hand-off.

## 6. Files touched

| File | Change |
|---|---|
| `.agents/scripts/check_maps.py` | 2 new constants, 3 rewired call sites, 4 new `need()` lines |
| `docs/workspace-standard.md` | PATH CONTRACT row + 1 tier-model line |
| `.agents/skills/5_adk_skills/adk-prompting/SKILLS.md` | renamed to `SKILL.md` |

No behavior change to `/update-maps-indexes`, `/sync-agents`, or any command.

---

**STOP — awaiting "approved".**
