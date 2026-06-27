---
IsArtifact: true
ArtifactMetadata:
  title: "Walkthrough — clean-workspace mirror fix + main_debug as the dev standard"
  type: walkthrough
  date: 2026-06-27
  todo_item: 3
---

# Walkthrough — Fresh now mirrors the standard; `main_debug` → `main` codified everywhere

Two phases. Phase 1 fixed the literal ask (clean-workspace mirroring). Phase 2 (Daniel's directive mid-task)
made `main_debug` → `main` the canonical dev standard so the drift that caused it can't recur.

## Phase 1 — re-vendor the item-2 sync engine into the migrated projects
**Found:** the projects carried the **old pre-item-2 sync engine** (no `GlobalsOnly`, no platform filter), so
`.opencode/commands` was unfiltered (35) and the toolkit was stale. **Fix:** ran the new `/sync-agents -Target`
against both migrated projects — additive vendor of the whole master `.agents/`, then platform-filtered
re-sync of `.claude`/`.opencode`.

The re-vendor surfaced that the projects' vendored `.agents/` was **substantially stale** (not just the
engine: `constitution.md`, many commands, scripts, the new `mobile-mode.md` rule, `sm.md` /
`merge_main_debug.md` commands, etc.) — so the diff is large but correct: it's the mirror being brought current.

## Phase 2 — `main_debug` → `main` as THE dev standard
**Why Phase 1 wasn't enough:** the merge command `merge_main.md` (Fresh-only) revealed Fresh ran a different
**git branch model** (main-only) from home base + AGY (`main_debug` → `main`). The audit found the root cause:
**the branch model had no single source of truth.** It lived only in AGENTS.md prose + the hook, and the one
*synced* rule (`git-policy.md`) said nothing about branches — so projects drifted, and Fresh's hook gated
`main` only.

Daniel's calls: *"this will be our dev standard and all rules need to reflect this"* + **Full: canonicalize the hook.**

### The standard (one statement, everything points to it)
`claude/*` session branch → PR → **`main_debug`** (shared integration) → promote **`main_debug` → `main`**
(live production, protected) only when Daniel is happy. Write-approval gate keys on the owner branches
(`main_debug` + `main`); `main` is extra-protected (reach it only via the deliberate manual promotion).

### Changes
1. **`.agents/rules/git-policy.md`** — NEW "Branch model — `main_debug` → `main` (THE dev standard)" section
   incl. the write-approval gate. This is now the **single synced source of truth**; AGENTS GATES point here.
2. **Canonicalized the hook** — added master `.agents/hooks/require-push-approval.py` (gates `main_debug`+`main`)
   and extended `sync-agents.ps1` to deploy `.agents/hooks/*` → every target's `.claude/hooks/`. The safety gate
   is now one source, propagated — **it can't drift again.**
3. **Root `AGENTS.md` §6** — points the branch-model lines at the new `git-policy.md` section; hook ref updated
   to the canonical `.agents/hooks/` source.
4. **Fresh `AGENTS.md` §8** — rewritten from main-only to the `main_debug` model; **deleted the 3 `merge_main.md`
   copies** (`.agents`/`.claude`/`.opencode`). Fresh now lands at exactly **36/35/31** like AGY/lobby.
5. **Project template** (`.agents/templates/project-template/AGENTS.md`) — added a GATES section pointing at the
   standard, so **new clones are born on `main_debug`**.
6. **Re-synced** lobby + Fresh + AGY.

## Verification (actual output)
```
Re-sync counts:  lobby 35/31 · Fresh 35/31 · AGY 35/31   (Fresh dropped 36/32 → 35/31: merge_main.md gone)
Hook gates main_debug (refs):  lobby 4 · Fresh 4 · AGY 4   (Fresh was 0 before)
git-policy.md byte-identical to master:  Fresh IDENTICAL · AGY IDENTICAL   (Branch-model section present x1 each)
merge_main.md anywhere (non-debug):  (none — clean)
Fresh command counts:  .agents 36 · .claude 35 · .opencode 31   ✓ standard
lobby .claude/hooks == master .agents/hooks:  IDENTICAL
```

## Your Actions

> **Branch:** per the new standard these infra commits belong on **`main_debug`**, not `main`. If you're on
> `main`, switch first (`git switch main_debug`, or `git switch -c claude/main-debug-standard` → PR). For the
> **Fresh** repo, first create the branch as you mentioned: `git branch main_debug main && git push -u origin main_debug`.

Three separate repos — commit each on its own. **Verify the staged set** (`git diff --cached --stat`) shows only
the intended paths before committing (the `_my_resources/` changes below are YOURS — keep them out).

**1 — Lobby (`Sudo_Hatter_Command`)** — explicit paths; excludes your `D _my_resources/.../gitnexus-usage-guide.md`:
```bash
git add \
  .agents/rules/git-policy.md .agents/scripts/sync-agents.ps1 \
  .agents/templates/project-template/AGENTS.md .agents/hooks/ \
  AGENTS.md .claude/hooks/require-push-approval.py \
  .claude/commands/1_update-maps.md .claude/commands/INDEX.md \
  .opencode/commands/1_update-maps.md .opencode/commands/INDEX.md \
  _artifacts/_main/2026-06-27_clean-workspace-mirror-fix/ _artifacts/INDEX.md
git diff --cached --stat   # confirm ONLY the above; no _my_resources/
git commit -m "feat(git): codify main_debug→main as the dev standard; canonical synced hook; clean-workspace mirror fix" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

**2 — Fresh (`Projects/Fresh_Workspace_BMAD`)** — the whole toolkit mirror + adapter (excludes your `_my_resources/README.md`):
```bash
cd Projects/Fresh_Workspace_BMAD
git add .agents .claude .opencode AGENTS.md
git diff --cached --stat   # confirm: NO _my_resources/README.md in the list
git commit -m "chore(toolkit): vendor current .agents standard; adopt main_debug git model; retire merge_main" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

**3 — AGY (`Projects/AGY_AVIATIONCHAT`)** — toolkit mirror brought current (no AGENTS.md change; it was already main_debug):
```bash
cd Projects/AGY_AVIATIONCHAT
git add .agents .claude .opencode
git diff --cached --stat   # confirm: only .agents/.claude/.opencode toolkit paths
git commit -m "chore(toolkit): re-vendor current .agents standard (sync engine, hook, git-policy branch model)" -m "Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

> After committing Fresh/AGY, **restart opencode** so it reloads the refreshed global command cache.

## Flagged (separate items)
- Mobile/desktop rules (todo item 4 — `mobile-mode.md` now vendored into both projects by this pass).
- Folder renames to match git repos (todo item 5).
- `Ingestion_pipeline_AvCh` — old un-migrated layout (`.agent/`, `_claude_artifacts/`); a separate migration.
