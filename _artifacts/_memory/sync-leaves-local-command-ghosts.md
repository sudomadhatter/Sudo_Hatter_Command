---
name: sync-leaves-local-command-ghosts
description: FIXED 2026-07-20 — /sync-agents now auto-purges renamed/deleted commands everywhere via .agents/.sync-manifest.json. No more hand-purging three dirs; project-owned files are structurally safe.
metadata:
  node_type: memory
  type: project
  originSessionId: 14571419-b1d2-4334-908f-ce5f376c7fd6
  modified: 2026-07-20T23:32:30.633Z
---

**Status: FIXED 2026-07-20.** `/sync-agents` now retires deleted/renamed master commands by itself across all
surfaces. Each target carries a generated `.agents/.sync-manifest.json` recording what the last run wrote; the
next run deletes what IT wrote and the master no longer owns. Verified end-to-end (probe command propagated to
11 surfaces, deleted from master, auto-purged from all 11; `autopilot_glm.md`, project rules, and BMAD installs
survived). **You no longer hand-purge after a rename — just run the sync.**

**Why the old bug existed (worth keeping — it explains the shape of the fix):** the vendored `.agents/` is
copied additively, and for a PROJECT that same vendored copy is the SOURCE for its `.claude`/`.opencode` menus.
So a deleted master command survived in the vendor and got re-published into the menus on every sync. The
name-based purge couldn't catch it either: once the master drops the name, the file reads as "project-own, leave
alone" — indistinguishable from a genuine project command. That ambiguity is exactly what the manifest resolves,
by recording authorship instead of inferring it.

**Reconcile layer (same day).** The manifest can only retire what it recorded, so anything retired BEFORE it
existed (or dropped in by hand) is invisible to it. Two switches close that:
`-Status` = read-only, git-status-style view of the invocable surfaces (`M` differs from master · `?` orphan,
master has no such command · `own` claimed by the keep-list). `-Reconcile` = resolve the `?`s, never guessing:
with no `.agents/project-own.txt` it STAGES one listing every orphan and deletes nothing; you delete a line to
mark that file a ghost; the next `-Reconcile` purges it everywhere. `git add` semantics — a second run is always
required before anything is destroyed. Scope is invocable surfaces only; `rules/` + `skills/` are excluded
because they're legitimately hybrid. Check everything with `-Maintained -Status`.

**How to apply:** trust the sync for retirement; don't hand-delete. Invariants to preserve if you touch
`sync-agents.ps1`: (1) purge ONLY from the manifest or a curated keep-list, never from a bare "not in master"
test — that test deletes project-authored commands like `/autopilot_glm`; (2) a missing/corrupt manifest must
fail safe to purging nothing; (3) `Get-OwnAllowList` must `return ,$items` — PowerShell unrolls a returned empty
array to `$null`, which silently turns a fully-curated "purge everything" list back into "no list yet" and
stages forever (this bug was live and caught in testing). A project sync prints `project-owned file(s), left
alone` — informational, not drift. Related:
[[toolkit-sync-covers-agents-not-docs]], [[grep-skips-gitignored-projects]], [[fresh-workspace-living-template]].
