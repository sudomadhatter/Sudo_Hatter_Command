---
title: Finish the artifacts-policy rollout (instructions + reconcile stale refs) + clean-bmad artifacts migration + WS7 repo-map drift on the home base
type: implementation_plan
workspace: _home
date: 2026-06-25
status: AWAITING-APPROVAL
owner: Daniel
author: Claude (Opus 4.8)
related:
  - _artifacts/INDEX.md                      # Daniel's new placement policy (header)
  - memory: artifacts-live-with-the-work     # the codified rule
  - _docs/workspace-standard.md              # canonical doc (partially updated)
---

# Finish the artifacts setup + WS7 drift on the home base

## 0. Goal (your Msg D, restated — working from main, on clean-bmad)
Finish the `_artifacts/` setup: **organize it + write the how-to instructions** (story work nests under an
**epic folder, created if missing**, as `<epic>/<story>/`; **system / cross-project → `_home/`**; project work →
project-local), **reconcile the canonical docs** to the policy you already set, and give the **home base the same
hybrid auto-updating repo-map** (drift) that aviationChat already has. clean-bmad's reshape is done and left as-is.

## 1. Verified current state
- ✅ New policy (**artifacts-live-with-the-work**) already in `AGENTS.md §5/§7`, `workspace-standard.md` Part-2
  block, and `INDEX.md` header (your edits).
- ❌ **Stale old `_artifacts/<workspace>/` refs still live in:** `AGENTS.md` §3 gate + §4 table;
  `workspace-standard.md` lines **58, 71, 84, 180**; master `.agents/rules/artifacts-always-first.md` (whole rule).
- ❌ **No `_artifacts/README.md`** anywhere — the "how to structure" doc you asked for doesn't exist.
- ❌ **Home base has no repo-map** (no `docs/` folder) → its drift hook has nothing to check yet. The **master
  drift script already exists** (`.agents/scripts/check-repo-map-drift.ps1`).
- ◻️ **clean-bmad** reshape done + left as-is; its history still sits at home-base `_artifacts/clean-bmad-workspace/`
  (per the new policy it should be project-local — that's WS-C, flagged below).
- ⛔ **aviationChat = OUT OF SCOPE** — already migrated project-local + its drift hook already wired. Don't touch it.

---

## 2. Workstreams

### WS-A — Write the artifacts instructions  ← the headline ask  [inside `_artifacts/`, no gate]
New **`_artifacts/README.md`**: the placement test ("what the work is ABOUT, not where you launched it");
**project → project-local `Projects/<name>/_artifacts/`**, **system / cross-project → `_home/`**; **story →
`<epic>/<story>/`, create the epic folder if it isn't there**; random task → `<YYYY-MM-DD>_<slug>/`; retired →
`_archived/`; the session-folder set (`implementation_plan` → `walkthrough` + `task-list`); naming. INDEX.md header
gets a one-line pointer to it.

### WS-B — Reconcile the stale refs (finish propagating your policy)  [gated]
- `AGENTS.md` §3 gate ("into `_artifacts/<workspace>/…`") + §4 table → new model.
- `workspace-standard.md` lines **58, 71, 84, 180** → new model.
- master `.agents/rules/artifacts-always-first.md` → rewrite its placement model (intro blockquote + §2 bucket/folder
  naming + §6/§7 path examples) to project-local vs `_home/`. *(Its vendored project copies re-sync via `/sync-agents`
  later — separate propagation task, flagged not done.)*

### WS-C — ⚠️ Migrate clean-bmad history to project-local  [touches clean-bmad + cross-repo — APPROVE or DEFER]
Move `_artifacts/clean-bmad-workspace/*` → `Projects/clean-bmad-workspace/_artifacts/*` (mirror aviationChat:
`active-context.md` at root + the dated session folders), remove the emptied home-base bucket, verify clean-bmad
`.gitignore` **tracks** `_artifacts/`, and repoint clean-bmad's `AGENTS.md`/`repo-map`/`settings.json.proposed` off
the home-base path. **This is the one part that edits clean-bmad — say the word to include or defer it.**

### WS-D — Home base's own hybrid repo-map + drift  [gated; hook = hand-off]
Generate `docs/repo-map.md` (`generate_repo_map.py --root <home> --output docs/repo-map.md --ignore Projects,_my_resources`)
+ hand-author its curated header. Then **propose** the home-base `.claude/settings.json` hook (inject the map + an
inline top-level drift nag, like aviationChat's) — **auto-mode blocks me editing startup config, so this is a
hand-off** (`settings.json.proposed`). Master drift script already exists, no promotion needed.

### WS-E — Verify + hand off
Run the generator + confirm drift behavior; update `_home` `active-context.md`, append an `INDEX.md` row, write
`walkthrough.md` (+ exact git commands) + `task-list.md`.

---

## 3. What I CANNOT do (hand-offs)
- **Apply the home-base SessionStart hook** (`settings.json`) — auto-mode blocks startup-config edits. Proposed file provided.
- **Commit/push** — git-policy; exact commands in the walkthrough.

## 4. Out of scope (deferred / not now)
aviationChat (already done) · clean-bmad reshape (done, left as-is) · pruning vendored skills · re-syncing
`artifacts-always-first.md` to every project · `_claude_artifacts/` retirement.

## ✋ STOP — awaiting "approved"
One call to make: **WS-C** (migrate clean-bmad's artifacts) is the only part that touches clean-bmad — **approve
the whole plan, or say "approved, defer WS-C"** and I'll do everything except that.
