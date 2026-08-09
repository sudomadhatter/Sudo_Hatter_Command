---
IsArtifact: true
ArtifactMetadata:
  title: "Implementation plan — fix the mobile & desktop rules (todo item 4)"
  type: implementation_plan
  date: 2026-06-27
  todo_item: 4
  status: done
---

# Fix the mobile & desktop rules — `main` + `clean-workspace` (todo item 4)

## The ask
> "Fix the mobile and desktop rules for both **main** and **clean-workspace** projects. Reference: `.agents/rules/mobile-mode.md`"
> *(main = home base `Sudo_Hatter_Command`; clean-workspace = `Projects/Fresh_Workspace_BMAD`. Note: AGY is **not** named — it's the one that's already correct.)*

## What I verified (so we fix the right thing, not churn)
The mobile-mode **rule file** is fine — item 3's re-vendor already made it byte-identical everywhere:
- `mobile-mode.md` md5 `d3cd9a0…` — **identical** across master + AGY + Fresh.
- `git-policy.md` md5 `a175cf0…` — **identical** across master + AGY + Fresh.
- There is **no `desktop-mode.md`** anywhere — "desktop" is the *implicit default* in `git-policy.md` + `artifacts-always-first.md`. (That's by design; mobile-mode supersedes those defaults.)

So item 4 is **not** a mirroring fix. The real gap is in **how each workspace's `AGENTS.md` WIRES the mobile/desktop split** — the trigger that activates the lane and the label that names the desktop default. That wiring lives in each `AGENTS.md` (per-workspace, NOT synced), and it has drifted three different ways:

| Element | **AGY** (reference ✅) | **`main`** / home base (partial ⚠️) | **`clean-workspace`** / Fresh (missing ❌) |
|---|---|---|---|
| Web/mobile **load pointer** | §5 — full block, names the concrete trigger `CLAUDE_CODE_REMOTE=true` | §3 — vague ("remote container"), **no env-var trigger** | **none at all** |
| GIT gate **"desktop default" label** + mobile pointer | §8 — explicit `**GIT — desktop default**` + web/mobile pointer | §6 — git gate has **no desktop label, no mobile pointer** | §8 — git gate has **no desktop label, no mobile pointer** |
| **Branch-model** web/mobile note | §8 — "(Web/mobile clone/fork → mobile-mode.md)" | none | none |

And the **canonical rule itself is under-specified**: `mobile-mode.md` describes activation only *qualitatively* ("runs in a remote / cloud container"), while the concrete trigger `CLAUDE_CODE_REMOTE=true` actually lives scattered in **AGY's AGENTS.md** and **`autopilot_mobile.md`**. The rule that *owns* the lane never states its own trigger — that's the root inconsistency that let the AGENTS.md files drift.

## Root cause (same shape as item 3)
The mobile/desktop boundary has **no single source of truth for its activation trigger**. The lane override-behaviour is well-specified in `mobile-mode.md`, but *when it turns on* (`CLAUDE_CODE_REMOTE=true`) and *what "desktop" means when it's off* are restated ad-hoc per `AGENTS.md` — so `main` got a vague version and Fresh got none. Fix it the way item 3 fixed the branch model: **canonicalize the trigger + boundary in the rule, then make every `AGENTS.md` a consistent pointer.**

## Plan — canonical first, then propagate

**1. Canonicalize the trigger in `.agents/rules/mobile-mode.md`** (the rule that owns the lane; synced):
   - In "When this lane is active", make the **Auto** trigger concrete: *auto-on when env `CLAUDE_CODE_REMOTE=true`* (the var Claude Code sets on web/mobile — already used by `autopilot_mobile.md`), keep "or Daniel says 'mobile'", and state the **Off** case crisply: *var unset → desktop, the defaults in `git-policy.md` + `artifacts-always-first.md` apply unchanged.* This makes the rule the single source for the lane boundary; AGENTS files stop inventing their own phrasing.
   - Light touch only — overrides 1–4 and hard-stops are already correct. (One small reconcile: Override 1 says "the designated feature branch" — align it to the now-canonical branch model: push your own `claude/*` branch, PR targets `main_debug`, never `main`.)

**2. Bring `main` (home base) `AGENTS.md` up to the AGY pattern:**
   - §3 web/mobile block → name the concrete trigger `CLAUDE_CODE_REMOTE=true` and point at `mobile-mode.md` as canonical (replaces the vague "remote container" wording).
   - §6 GATES → add a one-line **`GIT — desktop default`** framing on the git gate + a web/mobile pointer ("on `CLAUDE_CODE_REMOTE=true` the agent owns git delivery → `mobile-mode.md`; on desktop, ignore it"). No behaviour change to the desktop gate itself.

**3. Bring `clean-workspace` (Fresh) `AGENTS.md` up to the AGY pattern (it's missing the lane entirely):**
   - §4 ALWAYS-LOAD → add the web/mobile load pointer (mirror AGY §5's block, BMAD-flavoured).
   - §8 GATES → add the **`GIT — desktop default`** label + web/mobile pointer on the git gate, and the "(Web/mobile → `mobile-mode.md`)" note on the BRANCH MODEL line.

**4. Project template** (`.agents/templates/project-template/AGENTS.md`) — add the same web/mobile pointer + desktop-default label so **new clones are born with the lane wired** (today they'd inherit Fresh's gap).

**5. Re-sync + verify:**
   - `mobile-mode.md` is a rule → re-vendor to both projects (`/sync-agents -Target …`); confirm md5 identical across all three.
   - AGENTS.md files are per-workspace (not synced) → edited in place; verify each contains the trigger + desktop label.
   - Verify: `CLAUDE_CODE_REMOTE` now appears in `mobile-mode.md` (was 0) and in `main` + Fresh AGENTS.md (was 0); AGY unchanged (already had it).

## Why AGY is left alone
AGY's `AGENTS.md` is already the gold standard (explicit trigger, desktop-default label, mobile pointers in §5 + §8). Once `mobile-mode.md` owns the trigger, AGY is automatically consistent — no edit needed (matches the todo naming only `main` + `clean-workspace`).

## Out of scope (flagged, not in this plan)
- Renaming project folders to match git repos (todo item 5).
- `Ingestion_pipeline_AvCh` — old un-migrated layout; separate migration.
- No change to the desktop git behaviour, the approval gate mechanics, or the hook — this is wiring/labeling, not new policy.

## Git / safety
- Writes files only (one rule + 3 AGENTS.md + template). No `git add`/commit/push by me.
- After approval + run, I hand you **surgical, explicit-path** commit commands per repo (home base + Fresh; AGY only if its vendored `mobile-mode.md` changes via re-sync) — on `main_debug`, never `main`; excludes your in-flight `_my_resources/` edits.

## Close-out
On completion: `walkthrough.md` (with real verify output) + `task-list.md` here, and a row on `_artifacts/INDEX.md`.

---
**STOP — awaiting "approved" to execute steps 1–5.**
