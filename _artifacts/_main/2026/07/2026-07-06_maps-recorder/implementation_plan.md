# Implementation Plan — Map-drift Recorder (commit-time journal)

**Approval:** Daniel authorized in-session ("build it now the MVP a working hook and updated
workflows to use it") after a 4-turn design conversation. This artifact is the trail, not a stop gate.

> **Note:** a separate, unfinished `_artifacts/_main/implementation_plan.md` (a pending `/1_update-maps`
> reconcile) is untouched and still awaits Daniel's approval — do not confuse it with this task.

## Problem

Today the maps/INDEX system detects drift two ways: at **SessionStart** (the drift nag +
`check_maps.py --depth3-only`) and **on demand** (`/1_update-maps`). Both re-derive "what changed"
from scratch every time. Nothing captures change **at the moment it happens** (commit time), so:
- the nag can only say "*something* is undocumented", not *what/when*;
- `/1_update-maps` re-walks to rediscover drift before applying the prose fixes (the slow, token-costing layer).

## Idea (Daniel's)

A **recorder**: a non-blocking `post-commit` hook that classifies each commit's changes into the
linter's judgment categories and appends them to a machine-local journal. The existing consumers
(the nag, `/1_update-maps`) read the journal for a **pre-scoped worklist** instead of re-deriving it.

## Design principles

1. **Cache, not truth.** The journal is a hint that *accelerates*. `git diff <anchor>..HEAD` stays
   ground truth. Every consumer runs a **freshness guard** (journal's last sha == HEAD?) and, if
   stale (commit made without the hook / another machine / rebase), **falls back to the full derivation**.
   Same discipline as the GitNexus machine-local index rule.
2. **Machine-local.** Journal is gitignored (like `.gitnexus/`). The committed `.maps-state.json`
   anchor stays the shared reconcile baseline; the journal is a local accelerator rebuilt as you commit.
3. **Non-blocking.** `post-commit` fires *after* the commit is sealed — it can never block or corrupt a commit.
4. **Reuses the anchor model.** The anchor (`docs/.maps-state.json` `reconciled_at`) defines the
   "consumed up to here" boundary. `--set-anchor` rolls consumed journal lines into an archive.

## Files

| File | Change |
|---|---|
| `.agents/scripts/record_map_changes.py` | **NEW** — recorder/classifier. Modes: `--commit <ref>` (append one line), `--nag` (print classified tail since anchor, freshness-guarded, always exit 0), `--consume <sha>` (roll consumed lines to archive). |
| `.githooks/post-commit` | **NEW** — POSIX sh, calls `record_map_changes.py --commit HEAD`, swallows all errors (`|| true`). Tracked + shareable. |
| `core.hooksPath` | set to `.githooks` (per-repo git config; `.git/hooks` had only `.sample` files). |
| `.gitignore` | ignore `docs/.maps-journal*.jsonl` (machine-local). |
| `.claude/settings.json` | add a 4th SessionStart hook: `record_map_changes.py --nag`. |
| `.agents/scripts/check_maps.py` | `set_anchor()` also calls `rmc.consume(root, head)` (import beside it, like `generate_repo_map`). |
| `.agents/workflows/1_update-maps.md` | new Step 0 pre-read of the journal (with the fallback caveat); document the journal + consume-on-anchor. |

## Classification (from `git diff --name-status` alone — reliably derivable)

- `toolkit-change` — add/del/rename under `.agents/{commands,skills,workflows,rules}/*.md` (not INDEX.md) → **needs INDEX row + `/sync-agents`**
- `rename` — status `R` whose first segment is a real top-level dir → **curated/INDEX row may be stale**
- `session-added` — add under `_artifacts/**/<session>/` matching the session-folder pattern → **needs depth-3 INDEX row**
- `toplevel-added` — add whose top segment is a non-noise dir → **candidate new top-level folder (consumer verifies)**
- `delete` — delete whose first segment is top-level → **may leave a dead map/INDEX row**

Every commit appends exactly one line (even empty `changes:[]`) so the freshness guard (last sha == HEAD) is trivial.

## Out of scope (clean second step)

`check_maps.py` *reading* the journal as a fast-path (kept as ground-truth fallback for the MVP);
propagating the hook to `Projects/<name>` repos (one `git config core.hooksPath .githooks` per repo).

## Verify

`python record_map_changes.py --commit HEAD` → one journal line; `--nag` → classified tail;
corrupt the last sha → nag reports "behind HEAD, falling back". No commit made (git-policy: hand Daniel the command).
