---
IsArtifact: true
ArtifactMetadata:
  title: "Implementation plan — fix clean-workspace mirroring (todo item 3)"
  type: implementation_plan
  date: 2026-06-27
  todo_item: 3
  status: done
---

# Fix the clean-workspace project mirroring (todo item 3)

## The ask
> "Fix the clean-workspace project, it's not mirroring the other projects correctly."
> *(clean-workspace = `Projects/Fresh_Workspace_BMAD`, artifact bucket `clean-bmad-workspace`)*

## What I verified (so we fix the right thing, not churn)
Compared Fresh against the reference migrated project (`AGY_AVIATIONCHAT`) and the lobby master.

**Already at parity — no action (Daniel's prior cleanup):**
- `.claude/{commands(35), hooks/require-push-approval.py, settings.json, skills}` — present & matching.
- `.opencode/agent/` — Fresh's 13 agents == master's 13 exactly (AGY's extra `autopilot-*` two are AGY-specific, not master).
- `_artifacts/INDEX.md`, adapters (`CLAUDE.md`/`GEMINI.md` one-liners), `_my_resources/open_tasks/todo_list.md`.
- **`.gemini/GEMINI.md` absent is CORRECT** — that file is AGY's own "Wozniak" product persona; Fresh "carries the stack, not a product."
- Fresh `.agents/skills` = 105 (a fuller fresh-BMAD install) vs master 84 — project-owned BMAD skills; re-vendor is additive so these are preserved, not deleted.

**The one real divergence — stale sync engine (pre-item-2):**
| Surface | Fresh now | Target | Cause |
|---|---|---|---|
| `.agents/scripts/sync-agents.ps1` | old (no `GlobalsOnly`/platform filter) | item-2 engine | never re-propagated after the item-2 rewrite |
| `.opencode/commands` | 35 (unfiltered) | 31 (platform-filtered) | old engine copies all, ignores `platforms:` |
| `.agents/commands` | 35 | 36 (+`merge_main_debug`, `sm`) | master grew after last vendor |
| `.claude/commands` | 35 | 35 ✓ | already correct |

The command files were re-tagged with `platforms:`, but the **engine that reads those tags is old**, so opencode still gets the full 35.

## Plan — one re-vendor pass (the unified engine is built for exactly this)
**Step 1.** From the lobby, run the **new** engine against Fresh:
```
& ".agents\scripts\sync-agents.ps1" -Target "Projects\Fresh_Workspace_BMAD"
```
For a PROJECT target this engine:
- robocopies master `.agents/` → `Fresh/.agents/` (**additive `/E`, no purge**) → updates `sync-agents.ps1` to the item-2 engine, adds the 2 missing commands, refreshes skills/opencode-agents (keeps Fresh's extra skills).
- re-syncs `.claude/commands` (claude-filtered → 35) and `.opencode/commands` (opencode-filtered → **31**), plus `.claude/skills` + `.opencode/agent`.
- does **NOT** touch machine-global caches (those mirror the lobby only).

**Step 2.** Verify parity:
- `Fresh/.agents/scripts/sync-agents.ps1` contains `GlobalsOnly` (new engine landed).
- `.opencode/commands` == **31**; `.claude/commands` == **35**; `.agents/commands` == **36**.
- platform filter proof: `autopilot_opencode.md` present in `.opencode/commands`, absent from `.claude/commands`; the 5 claude-only `_AP`/`autopilot_claude` absent from opencode.
- `.opencode/agent` + skills unchanged-or-superset (no Fresh-owned loss).

**Step 3 — ✅ DECIDED: Fresh + AGY (both migrated projects).**
Run the same pass against `-Target "Projects\AGY_AVIATIONCHAT"` so lobby + both migrated projects land on the item-2 standard in lockstep. Additive; AGY's project-specific extras (`autopilot-*` agents, custom skills, `.gemini/GEMINI.md`) are preserved.
- `Ingestion_pipeline_AvCh` is the **old un-migrated** layout (`.agent/`, `_claude_artifacts/`) — a separate migration, **out of scope** here.

## Out of scope (flagged, not in this plan)
- Mobile/desktop rules (todo item 4).
- Renaming project folders to match git repos (todo item 5).
- AGY's `.claude/skills` 56 vs `.agents/skills` 84 internal gap — AGY-local BMAD state, not a Fresh issue.

## Git / safety
- This pass **writes files only** (vendoring + sync). No `git add`/commit/push by me.
- After approval + run, I'll hand you a **surgical, explicit-path** commit command (never `git add -A`); excludes your in-flight ` M _my_resources/README.md` (protected) and anything not part of this work.

## Close-out
On completion: `walkthrough.md` (with real verify output) + `task-list.md` here, and a row on `_artifacts/INDEX.md`.

---

# PHASE 2 — `main_debug → main` as the canonical dev standard (Daniel's directive)

> Daniel: *"this will be our dev standard and all rules need to reflect this"* + chose **Full: canonicalize the hook.**
> He has created `main_debug` on `Sudo_Hatter_Command` (home base), and uses it on aviationChat already.

## Why Phase 1 alone wasn't enough — the audit
Re-vendoring fixed the *toolkit* mirror, but surfaced that the **git branch-model has no single source of truth**, so it drifted:
- **Root AGENTS.md §6** — already `main_debug` ✓ · **AGY AGENTS.md §8** — already `main_debug` ✓ (clean "`main` is LIVE PRODUCTION; all dev on `main_debug`" statement).
- **`.agents/rules/git-policy.md`** — the ONE synced canonical rule — **says nothing about branches** (only "don't run git / delegate / safe-commit"). ← the structural hole.
- **Fresh AGENTS.md §8** — the only project still **main-only** (`/merge_main`); **Fresh hook gates `main` only** (0 `main_debug` refs).
- **The hook (`require-push-approval.py`) is hand-maintained per project** (lives in `.claude/hooks/`, NOT in the synced toolkit) → nothing propagates it → it drifted.
- `settings.json` differences are **legitimate** (per-project paths + BMAD allows); the merge-gating `ask` block is present in all. **No change.**

## The standard (one statement, everything points to it)
`claude/*` session branch → PR → **`main_debug`** (shared integration) → promote **`main_debug` → `main`** (live production, protected) only when Daniel is happy. Write-approval gate keys on the **owner branches (`main_debug` + `main`)**; `main` is extra-protected (never auto-target).

## Changes — canonical first, then propagate
1. **`.agents/rules/git-policy.md`** — ADD a **"Branch model — `main_debug` → `main` (the dev standard)"** section (the single synced source of truth). Mirrors AGY's existing good language.
2. **Canonicalize the hook** — add master source `.agents/hooks/require-push-approval.py` (gates `main_debug` + `main`), and extend **`sync-agents.ps1`** to deploy `.agents/hooks/*` → each target's `.claude/hooks/` (additive, Claude-only surface). So the safety gate is one source, propagated — can't drift again.
3. **Root AGENTS.md §6** — light: point the branch-model lines at the new `git-policy.md` section as canonical (keep wording).
4. **Fresh AGENTS.md §8** — rewrite the main-only GATES to the `main_debug` model (reference `git-policy.md`); **`git rm` the 3 `merge_main.md` copies** (`.agents`/`.claude`/`.opencode`). Fresh then lands at exactly **36/35/31** like AGY/lobby.
5. **Project template** (`.agents/templates/project-template/AGENTS.md`) — has no git section today (defers to home base). Add a one-line GATES pointer to `git-policy.md`'s branch model so new clones are explicitly born standard.
6. **Re-sync** lobby + Fresh + AGY, then **verify:** every `.claude/hooks/require-push-approval.py` gates `main_debug`; Fresh = 36/35/31; no `merge_main.md` anywhere; `git-policy.md` identical across all surfaces.

## Action split
- **Daniel (repo/branch — your call):** create `main_debug` on the **Fresh** repo (`git branch main_debug main && git push -u origin main_debug`); on GitHub set default PR base → `main_debug` and branch-protect `main`. (Home base + AGY already done.)
- **Me (files only; no commit/push):** items 1–6 above. Then hand you **surgical, explicit-path** commit commands per repo (lobby + Fresh + AGY), excluding your in-flight ` M _my_resources/README.md` and anything not mine.

## Out of scope (unchanged)
- Mobile/desktop rules (item 4) · folder renames (item 5) · `Ingestion_pipeline_AvCh` (old un-migrated layout — separate migration).

---
**STOP — awaiting "approved" to execute Phase 2 (items 1–6).**
