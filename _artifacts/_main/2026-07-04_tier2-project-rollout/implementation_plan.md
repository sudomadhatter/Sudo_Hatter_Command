---
IsArtifact: true
ArtifactMetadata:
  title: Tier-2 local law — per-project rollout to AGY_AVIATIONCHAT + Fresh_Workspace_BMAD
  type: implementation_plan
  date: 2026-07-04
  status: PRE-APPROVED (flagged follow-up of 2026-07-03_tier2-local-law; Daniel, in chat — "it also needs
    to be done for aviationchat and fresh-workspace … please finish the job")
---

# Implementation Plan — Tier-2 local law: project rollout (AGY + Fresh)

## Why
The 2026-07-03 tier2-local-law session landed the 3-tier folder-file model in the LOBBY only and
explicitly flagged the per-project pass as the follow-up: *"Per-project Tier-2 rollout: AGY + Fresh get
their own 9 Tier-2 files + vendored `workspace-standard.md` refresh (docs/ is not synced — deliberate
per-project pass). Until then their lints show the check-8 hint."* Daniel has now directed that pass.
The toolkit half (check_maps.py check 8/9, generate_repo_map.py, /1_update-maps) is ALREADY in both
projects via /sync-agents (md5-verified previous session; commits AGY `7e279e22`, Fresh `9d9c44d`).

## Changes

**Per project (`Projects/AGY_AVIATIONCHAT`, `Projects/Fresh_Workspace_BMAD`):**
1. **NEW 9 Tier-2 files** — `_artifacts/`, `_my_resources/`, `docs/` each get a ~15-line local-law
   `AGENTS.md` + the 1-line `CLAUDE.md`/`GEMINI.md` adapters (house byte-pattern, carries the check-8
   `ADAPTER_PHRASE`). Law bodies are **digests of each project's own canon** (its `_artifacts/README.md`
   + INDEX header placement rules, its `_my_resources/README.md` protections, its repo-map regen command)
   — AGY keeps `tea/` + `epic_<E>/` + local `_main/`; Fresh has no `tea/`; Fresh has no GitNexus index.
2. **Vendored `docs/workspace-standard.md` refresh** — byte-copy of the current lobby canon (both copies
   are stale pre-tier-model revisions; verified no project-specific edits in either).
3. **Root `AGENTS.md`** — add the reading-order rule to §2 START HERE (the lobby's §1.7 equivalent:
   folder carries an `AGENTS.md` → read it FIRST; INDEX/README = inventory only).
4. **One-doc close alignment** (same rot the lobby fixed 2026-07-03): `_artifacts/README.md` — merge the
   `walkthrough.md` row to the one-doc form, drop the abolished `task-list.md` row; root `AGENTS.md` §5
   close-out sentence likewise. (The refreshed workspace-standard brings the one-doc canon into the repo;
   without this the new law files would contradict the local README.)
5. **Ledger row** in each project's `_artifacts/INDEX.md` pointing at this lobby write-up (precedent:
   the 2026-07-03 artifact-routing-fix row).
6. **Verify**: `check_maps.py --root <project> --ignore <documented>` → check 8 `[ok]` (+ one negative
   test in AGY); regen repo-map AUTO body per the header's documented command if the new files drift it.

**Lobby:** this session folder + `_artifacts/INDEX.md` row + `_main/INDEX.md` row +
`_main/active-context.md` hand-off. No lobby toolkit/docs changes — everything needed is already synced.

## Out of scope
- The 4 unconverted projects (JETCHAT, B-L-WorldWide, NEXGen-Films, OpenChat-Openrouter) — no Tier-1
  brains yet (pre-existing backlog).
- AGY's known backlog drift (journeys/ + tia/ dirs, 13 depth-3 INDEX gaps, stale GitNexus index) — a
  normal future `/1_update-maps` run's work, not this pass.
- Promoting check 8 hint → fatal (needs all workspaces converted first — after this pass only the 4
  above remain).

## Verification
- Per project: lint exit 0 with `[tier-2 local law] → [ok] … (redirects verified)`; negative test fires
  then restores clean; repo-map freshness `[ok]` after regen.
- Git: hand Daniel the exact `git add`/`commit` commands per repo (desktop git policy — agent never
  commits). Note: Fresh is currently checked out on `main`, not `main_debug` — flagged in Your Actions.
