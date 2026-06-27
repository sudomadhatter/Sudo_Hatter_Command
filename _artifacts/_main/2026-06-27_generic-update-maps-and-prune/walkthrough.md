---
IsArtifact: true
ArtifactMetadata:
  title: "Walkthrough — generic /1_update-maps + path contract + context-hygiene prune"
  type: walkthrough
  date: 2026-06-27
---

# Walkthrough — one generic maps tool, a structure contract, and a prune

## What I built (the 4 parts, all approved)

**Part A — the PATH CONTRACT (`_docs/workspace-standard.md`).** Added a machine-checkable table: every standard
element (repo-map · structure standard · scripts · continuity brief · INDEX · open_tasks · `.agents/` · BMAD)
with its **exact path in each of two modes** — *home base* (lobby) and *project*. Documented the only legitimate
home↔project differences (`_docs/` vs `docs/`; bucketed `_artifacts/` vs flat; and the continuity brief living at
`_bmad-output/active-context/active-context.md` in a BMAD project). Also added a "Context hygiene" upkeep section
stating the prune window (keep ~10 blocks, nag at 12; INDEX keep ~25).

**Part B — `check_maps.py` made generic.** It already took `--root`; now it:
- **auto-detects the mode** (home base = has `Projects/`; BMAD = has `_bmad-output/`) and the **map path**
  (`_docs/repo-map.md` vs `docs/repo-map.md`) and the **state file** beside it;
- adds **check 6 — structure conformance** (fatal): the workspace carries the standard files in the standard
  places. This is the "verify the structures stay standard" gate that makes one generic tool *safe*;
- adds **check 5 — context hygiene** (NON-fatal hint): continuity brief over the block window / INDEX over the
  row cap → a nudge, never a failed exit (won't surprise CI/hooks);
- **robust root-detection** so a byte-identical vendored copy self-roots from `.agents/scripts/` *or* a legacy
  `scripts/` location.

**Part D — `/1_update-maps` workflow** reframed from "LOBBY only" to **"any conformant workspace via `--root`"**,
with a new **Step 3.5 — Context hygiene (prune)**: keep newest ~10 blocks, archive the rest (a **move**, verbatim,
never a summarise-away) to `active-context-archive.md` (lobby) or `_bmad-output/active-context/_archive/` (BMAD);
same for INDEX rows → `INDEX-archive.md`. Report template + guardrails updated.

**Part C — propagation.** Synced the updated `check_maps.py`, `generate_repo_map.py`, workflow, and
`workspace-standard.md` **byte-identical** into both projects, and **gave fresh-workspace its missing**
`.agents/scripts/check_maps.py` + `generate_repo_map.py` (it had neither — the "mess" you flagged).

## What fought back
- **Root-detection bug, caught by testing.** My first "walk up until AGENTS.md/.agents" approach matched
  `.agents/` itself (it contains an `AGENTS.md`), so a no-`--root` run mis-rooted to `.agents`. Replaced with a
  deterministic strip (`<root>/.agents/scripts/` or `<root>/scripts/` → root). Re-tested: correct everywhere.
- **Console mojibake.** An em-dash in a `print()` rendered as `�` on the Windows cp1252 console → switched to ASCII.
- **Your mid-flight edits refined decision 3.** You edited fresh-workspace's `AGENTS.md` to declare the **BMAD
  `_bmad-output/active-context/active-context.md` as the live pickup/handoff brief** (with `_artifacts/` holding
  history). I took that as the model — BMAD active-context is the continuity + **prune target** for BMAD projects
  (it matches existing practice: aviationChat already archives to `_bmad-output/active-context/_archive/`). The
  contract + tool encode that.

## Test output (actual, pasted)

Generic detection across all three workspaces:
```
$ python .agents/scripts/check_maps.py                            → MAP & INDEX DRIFT LINT  (home base: Sudo_Hatter_Command)
$ python .agents/scripts/check_maps.py --root Projects/AGY_AVIATIONCHAT      → (BMAD project: AGY_AVIATIONCHAT)
$ python .agents/scripts/check_maps.py --root Projects/Fresh_Workspace_BMAD  → (BMAD project: Fresh_Workspace_BMAD)
```

Conformance gate caught the fresh-workspace gap, then confirmed the fix:
```
# BEFORE the sync:
[structure conformance]
  [x] NOT conformant - missing maintenance script (`.agents/scripts/check_maps.py`)
  [x] NOT conformant - missing map generator (`.agents/scripts/generate_repo_map.py`)
# AFTER the sync:
[structure conformance]
  [ok] clean
```

Vendored copy self-roots standalone (no `--root`, run from inside the project):
```
$ python Projects/Fresh_Workspace_BMAD/.agents/scripts/check_maps.py
MAP & INDEX DRIFT LINT  (BMAD project: Fresh_Workspace_BMAD)
```

Byte-identical sync verified (all copies == master md5): `check_maps.py` `a8e25cbd…`, `generate_repo_map.py`
`f37f8d0f…`, workflow `04b97f38…`, `workspace-standard.md` `aef2af04…`.

> Note: the home-base run still reports its OWN pre-existing drift (stale AUTO block; dead path
> `_docs/master-implementation-plan.md` — that file was deleted by earlier uncommitted work, not me). That's a
> real reconcile for a `/1_update-maps` run, separate from this build.

## Deviations from plan
- Decision 3 landed as "BMAD active-context is the continuity/prune target" (per your edit), not the
  `_artifacts/active-context.md` framing in the plan. Everything else matched the approved plan.
- Kept existing legacy `scripts/` copies byte-identical rather than deleting them (deletion = item 3).

## Flagged for item 3 (fix clean-workspace / mirroring) — NOT done here
- **Legacy `scripts/` duplicates** of `check_maps.py`/`generate_repo_map.py` coexist with the canonical
  `.agents/scripts/` ones (kept identical for now; consolidate to one location later).
- **Stray `Projects/AGY_AVIATIONCHAT/docs/file_structure_rules/workspace-standard.md`** — an older drifted dup;
  only referenced from that project's own `_artifacts/` history, not live routing. Reconcile/remove later.
- **fresh-workspace** still carries unrelated uncommitted churn (`.claude/`, `.opencode/`, `README`,
  `_claude_artifacts/`) from prior work — left untouched.

## Your Actions (commit — surgical, explicit paths only; pre-existing unrelated changes deliberately excluded)

**Home base** (`Sudo_Hatter_Command/`):
```bash
git add AGENTS.md _docs/workspace-standard.md \
  .agents/scripts/check_maps.py .agents/workflows/1_update-maps.md .agents/templates/project-template/AGENTS.md \
  _artifacts/INDEX.md _artifacts/_main/2026-06-27_pickup-open-tasks-wiring/ _artifacts/_main/2026-06-27_generic-update-maps-and-prune/
git commit -m "feat(maps): generic /1_update-maps + structure path-contract + context-hygiene prune; wire open_tasks into pickup" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
# do NOT add: .agents/commands/1_*.md or the _docs/master-implementation-plan.md deletion (not mine)
```

**aviationChat** (`Projects/AGY_AVIATIONCHAT/`, branch `main_debug`):
```bash
git add AGENTS.md docs/workspace-standard.md \
  .agents/scripts/check_maps.py .agents/scripts/generate_repo_map.py .agents/workflows/1_update-maps.md \
  scripts/check_maps.py scripts/generate_repo_map.py \
  _my_resources/open_tasks _my_resources/_open_tasks
git commit -m "feat(maps): vendor generic update-maps tool + path-contract; normalize open_tasks; wire pickup + what's-next" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

**fresh-workspace** (`Projects/Fresh_Workspace_BMAD/`):
```bash
git add AGENTS.md docs/workspace-standard.md \
  .agents/scripts/check_maps.py .agents/scripts/generate_repo_map.py .agents/workflows/1_update-maps.md \
  scripts/generate_repo_map.py
git commit -m "feat(maps): add missing check_maps.py + generator; vendor generic update-maps tool + path-contract" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
# do NOT `git add -A` — .claude/.opencode/README/_claude_artifacts churn is pre-existing, not mine
```

> `.agents/*` are MASTER at the home base → after committing, a `/sync-agents` pass is the canonical way to keep
> the `.claude/`/`.opencode/` command mirrors aligned (I synced the project copies directly this time).
