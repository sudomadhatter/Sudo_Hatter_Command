---
IsArtifact: true
ArtifactMetadata:
  title: Artifact Placement Standard — clean-up + _home→_main rename
  type: implementation_plan
  date: 2026-06-26
---

# Artifact Placement Standard — clean-up

## Goal
Codify ONE clear placement standard for where artifacts go, and make it consistent everywhere
(Claude **and** opencode, home base **and** projects). Three rules:

1. **Project work** → a per-project bucket; **create it if missing**, else reuse it.
2. **Main / home-base / cross-project work** → the home-base bucket, **renamed `_home` → `_main`**.
3. **Stories** (inside a project) → nested under their **epic folder**; create the epic folder if missing.

Plus the clarification from this chat: **opencode** writes under its own `_artifacts/opencode/`
namespace, and applies the **exact same three rules inside it** (`opencode/<project>/`,
`opencode/_main/`, stories → `opencode/<project>/<epic>/<story>/`).

Net behavior change is small (rules 1 & 3 already exist); the real work is the **`_home`→`_main`
rename**, mirroring the logic under `opencode/`, and scrubbing the term everywhere it's still live.

## Decision: what is "main level"?
- At the **home base**, `_main` is the bucket for the command-center's own work (the standard, the
  `.agents/` toolkit, routing, multi-project work) — the rename of today's `_home`.
- **Inside a project** there is no `_main` — every task there *is* that project's work, so general
  (non-story) work goes to `Projects/<name>/_artifacts/<YYYY-MM-DD>_<slug>/` and stories to
  `<epic>/<story>/`. (`_main` is a home-base-only bucket.)

## Files to change

### A. Rename the folder (history-preserving)
- `git mv _artifacts/_home _artifacts/_main` — moves `active-context.md` + all ~16 session folders.
  (Note: this session's own plan folder moves with it.)

### B. Live standard / canonical docs — `_home`→`_main`, tighten the 3 rules, add opencode mirror note
| File | Change |
|---|---|
| `AGENTS.md` | §5 + §7: `_home`→`_main`; state the 3 rules crisply; one line on opencode's `_artifacts/opencode/` mirror |
| `.agents/rules/artifacts-always-first.md` | **master rule** — intro callout + §2 placement: `_home`→`_main`; add opencode same-logic note |
| `_docs/workspace-standard.md` | Part 2 placement block: `_home`→`_main`; opencode note |
| `_artifacts/README.md` | `_home`→`_main` (2×); opencode note |
| `_artifacts/INDEX.md` | header placement rules `_home`→`_main`; Workspace-column label `_home`→`_main` for consistency; new session row at close |
| `_docs/repo-map.md` | curated header line 16: `_home/` → `_main/` |
| `.claude/settings.json` | **CRITICAL** — SessionStart hook path `_artifacts/_home/active-context.md` → `_artifacts/_main/active-context.md` (breaks otherwise) |

### C. opencode namespace
| File | Change |
|---|---|
| `_artifacts/opencode/README.md` | rewrite to state the 3 rules **inside `opencode/`**: project→`opencode/<project>/`, main→`opencode/_main/`, story→`opencode/<project>/<epic>/<story>/`; one row per session into the relevant INDEX |
- Do **not** pre-create empty `opencode/_main/` — created on first opencode session (lazy, per convention).

### D. Propagate to converted projects ("the new standard, for all projects")
The standard docs are vendored. Update the master, then re-vendor to the **2 converted** projects
(aviationChat-AGY, clean-bmad-workspace — the other 5 aren't converted yet, per memory):
- `Projects/{aviationChat-AGY,clean-bmad-workspace}/.agents/rules/artifacts-always-first.md` (2× `_home`)
- `Projects/{aviationChat-AGY,clean-bmad-workspace}/docs/workspace-standard.md` (`_home`)
- Method: edit masters in §B, then copy the two vendored files into each project (direct copy, not
  `/sync-agents` — that pulls the whole lobby set; we want just these two files re-vendored).

## Out of scope (flagged, not touched)
- **History prose** inside `_artifacts/_main/<date>_<slug>/*.md` (old walkthroughs/plans) — frozen records; left as-is.
- **`_my_resources/` diagrams** that mention `_home` (`gitnexus-usage-guide.md`,
  `complete-system-overview.md`, `updated_folder_file_structure_diagram.md`) — PROTECTED personal area;
  I'll flag them as stale but not edit unless you say so.
- **`_docs/master-implementation-plan.md`** — historical rollout doc (1 ref); leave as history.
- `Projects/aviationChat-AGY/docs/file_structure_rules/*` — project-internal doc copies; flag, don't touch.
- The 5 unconverted projects (B&L, NEXGen, jetChat, NEXGen Films, ingestion, openCode).

## Execution order
1. `git mv _artifacts/_home _artifacts/_main`.
2. Edit `.claude/settings.json` (hook path) — restore continuity before anything else relies on it.
3. Edit masters: `AGENTS.md`, `.agents/rules/artifacts-always-first.md`, `_docs/workspace-standard.md`,
   `_artifacts/README.md`, `_artifacts/INDEX.md`, `_docs/repo-map.md`, `_artifacts/opencode/README.md`.
4. Re-vendor the 2 files into the 2 converted projects (§D).
5. Verify: `grep -r "_home"` over live docs returns only history/protected/out-of-scope hits.
6. Close: `walkthrough.md` + `task-list.md`, update `_artifacts/_main/active-context.md`, append INDEX row.

## Verification
- `_artifacts/_main/` exists with all prior content; `_artifacts/_home/` gone.
- SessionStart hook resolves the new path (Test-Path passes).
- No live/canonical doc references `_home` (only frozen history + protected `_my_resources/` remain).
- Both converted projects' vendored copies say `_main`.

## Open questions
1. **INDEX Workspace column** — relabel historical `_home` rows to `_main` (consistent) or leave them as
   the name-at-the-time (literal history)? Plan assumes **relabel** (cleaner). Say the word to leave them.
2. **opencode `_main`** — confirm opencode's home-base-itself bucket should be `opencode/_main/`
   (parallel to Claude's `_main`). Assumed yes.
3. **Protected `_my_resources/` diagrams** go stale on the term — leave for a later explicit pass? (Assumed yes.)
