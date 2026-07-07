---
IsArtifact: true
ArtifactMetadata:
  title: GitNexus → own file + pointer (lobby + AGY) + folder-org guide as a skill
  type: implementation_plan
  date: 2026-07-06
---

# Implementation Plan — GitNexus out of the front door + folder-org guide as a skill

## Goal
Finish leaning the front door per Daniel's preference: **pull the inline GitNexus block out of the lobby +
AGY `AGENTS.md` into its own `docs/gitnexus.md`, leaving a one-line pointer** — and stand up the
**files-&-folders organization strategy** as a thin, auto-surfacing **skill** (single-sourced to
`workspace-standard.md`), then record it in the master plan.

Safe because we already set `skipAgentsMd` on the lobby + AGY `.gitnexusrc` → the generator won't re-inject
the block into `AGENTS.md`, so the block can live wherever we put it.

## Pieces (phased — approve all, or tell me to stop after any)

### 1. Lobby: GitNexus block → `docs/gitnexus.md` + pointer
- **Create** `docs/gitnexus.md` — move the current block (Always Do / Never Do / Resources / CLI) **plus**
  the hand-authored scope note (lobby index is tiny; pass `repo:"AGY_AVIATIONCHAT"` for product work) into it.
- **Edit `AGENTS.md`** — delete the scope note + the `<!-- gitnexus:start -->…<!-- gitnexus:end -->` block,
  replace with a one-line pointer, e.g.:
  `> **GitNexus** — code-intelligence (impact · detect_changes · query · context) for this repo →` `docs/gitnexus.md`.
- Net: AGENTS.md drops another ~50 lines; the block becomes static reference in `docs/`.

### 2. AGY: same move
- **Create** `Projects/AGY_AVIATIONCHAT/docs/gitnexus.md` with AGY's block.
- **Edit** `Projects/AGY_AVIATIONCHAT/AGENTS.md` — replace its block (lines ~124–168) with the same one-line
  pointer. (AGY already has a `docs/` reference shelf, so this fits its structure.)

### 2b. Fresh: set up the READY scaffold (not indexed — it's the empty skeleton)
Fresh has no GitNexus block and no code to index. Daniel: "it needs to be set up and ready for when we name it
a real project, then we'll use GitNexus." So pre-wire the pattern so a future real project inherits it:
- **Create** `Projects/Fresh_Workspace_BMAD/docs/gitnexus.md` — a **ready template**: a top note ("⚠️ Not
  indexed yet — this is the project skeleton. When this becomes a real project: run
  `node .gitnexus/run.cjs analyze` and add a `.gitnexusrc` `{"analyze":{"skipAgentsMd":true}}` so the block
  stays in THIS file, not `AGENTS.md`.") followed by the standard code-intel guidance with a `<PROJECT>`
  placeholder — so it's ready to fill.
- **Edit** `Projects/Fresh_Workspace_BMAD/AGENTS.md` — add the same one-line pointer → `docs/gitnexus.md`.
- **No `.gitnexusrc` yet** (nothing to index; the scaffold note tells the future maintainer to add it).
- Because Fresh is the clone-me skeleton, every new project born from it inherits this ready pattern.

### 3. `.agents/` re-index prevention (no guard file — keep it clean)
Per your "keep the toolkit clean" steer, **no `.gitnexusrc` guard file.** Instead extend the existing
by-design comment in `.agents/AGENTS.md` with one line: *"don't re-index this folder as a GitNexus root; if
you must, pass `--skip-agents-md` so it can't mint stub AGENTS/CLAUDE files here."* Documented prevention,
zero added config.

### 4. `workspace-structure` skill (thin, auto-surfacing)
- **Create** `.agents/skills/workspace-structure/SKILL.md` — a concise **decision guide**, NOT a copy:
  the tier model (which folders get an `AGENTS.md` vs stay `INDEX.md`-only), the reading-order rule, the
  adapter shape (`CLAUDE.md`/`GEMINI.md` one-liners), naming + artifact buckets — each pointing to
  `docs/workspace-standard.md` as the full spec.
- **Description** triggers on the real moment: *"Use when creating, moving, renaming, reorganizing, or adding
  folders/files, scaffolding a workspace, or deciding whether a folder needs an `AGENTS.md`/`INDEX.md`."* →
  the model auto-surfaces it on reorg tasks (a rule wouldn't; skills sit in the model's context).
- **Add a row** to `.agents/skills/INDEX.md`. Note: `/sync-agents` propagates it to all platforms + projects
  (hand to Daniel — I don't run sync/commit).

### 5. `master-implementation-plan.md` — folder-org strategy
Add a **"Folder & file organization strategy"** block to the §8 Evolution log: the tier model + reading-order
rule (folder has `AGENTS.md` → read first; else `INDEX.md` for inventory) + a pointer to the new skill and to
`workspace-standard.md`. This is the "guide" you asked to capture.

## Decisions baked in (override any)
- **No `.agents/.gitnexusrc` guard** (keep the toolkit config-free; documented prevention instead).
- **`docs/gitnexus.md`** as the home (agent-facing reference shelf, both repos) — not `_my_resources/`.
- **Skill name `workspace-structure`** (vs `folder-organization`).

## Verification
- `grep gitnexus:start` → **0** in both `AGENTS.md`; the block present in each `docs/gitnexus.md`; pointer line
  present in each `AGENTS.md`.
- Skill file exists + parses; `skills/INDEX.md` has its row; description names the reorg triggers.
- master-plan shows the folder-org section.
- Byte delta recorded for both `AGENTS.md`.

## Rollback
All git-tracked; revert the two `AGENTS.md`, delete the two `docs/gitnexus.md` + the skill dir, revert the
master plan + `skills/INDEX.md`. No data migration.

## Your Actions (after approval + execution)
- Commit: lobby (`AGENTS.md`, `docs/gitnexus.md`, `.agents/AGENTS.md`, `.agents/skills/workspace-structure/`,
  `.agents/skills/INDEX.md`, `_my_resources/docs/master-implementation-plan.md`, artifacts) and AGY
  (`AGENTS.md`, `docs/gitnexus.md`) — explicit paths, both `main_debug`.
- Run `/sync-agents` to propagate the new skill + the updated `.agents/` law to every project.
