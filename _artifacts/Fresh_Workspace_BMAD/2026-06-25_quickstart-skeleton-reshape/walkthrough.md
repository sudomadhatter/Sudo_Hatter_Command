---
title: clean-bmad → AGY Quick-Start Project Skeleton (+ hybrid auto-updating repo-map hook) — Walkthrough
type: walkthrough
workspace: clean-bmad-workspace
date: 2026-06-25
status: COMPLETE (agent-side) — 1 Daniel-applied step (settings.json hook) + commits pending
plan: ./implementation_plan.md
---

# Walkthrough — clean-bmad quick-start skeleton reshape

## What this was
Re-purpose `clean-bmad-workspace` from an "aviationChat clone" into the **AGY quick-start project skeleton** —
the repo Daniel clones to start a new project — organized/indexed/governed like the `Sudo_Hatter_Command` home
base, and add the **hybrid auto-updating repo-map** feature (SessionStart hook: inject the map + drift nag).

## Steer that shaped it (mid-plan corrections)
- **Keep the AGY tech stack** ("I use that on almost all projects") — so this reverses the "REMOVED: backend/
  frontend/ firebase…" line from the option menu. The stack scaffold + configs **stayed**; only the aviationChat
  *product* identity was stripped.
- **"add the hybrid auto-updating feature we added to the sudohattercommand"** → became WS7 (post-approval).

## What changed — authored files only (`Projects/clean-bmad-workspace/`)
| WS | Change | Files |
|---|---|---|
| WS1 | AGENTS.md ROOT LAW + MAP + routing re-cast to the skeleton (kept the 9-section structure + stack rows; added a re-index/drift routing row) | `AGENTS.md` |
| WS2 | Rewrote the stale README to the real tree + sharpened the clone→rename→build flow; fixed `.agent/`→`.agents/`, dropped `.gemini/gemini.md` / "633 skills" cruft | `README.md` |
| WS5 | Genericized the dead `.agent/gemini.md` refs (→ `.agents/rules/constitution.md` + `constitution.project.md`); kept the `{{PLACEHOLDER}}` tokens (they're the template fill-ins) | `_bmad-output/project-context.md` |
| WS3 | Regenerated the AUTO body (now lists `check-repo-map-drift.ps1`) + rewrote the CURATED header to the new identity | `docs/repo-map.md` |
| WS7 | **New drift script** — detect-only, nags when a top-level folder is on disk but absent from `docs/repo-map.md`; never edits; always exit 0 | `scripts/check-repo-map-drift.ps1` |
| WS4 | Verified the stack is untouched; reviewed `docs/skills-registry.md` → left as-is (generic, stack-aligned) | — (no-op) |

## What changed — home base (`Sudo_Hatter_Command/`)
- `router.md` row re-labelled: "Clean BMAD baseline / clone-template" → **"AGY quick-start project skeleton
  (FastAPI/ADK · Next/React · Firebase) — clone to start a new project"**; status → "quick-start skeleton ·
  standard-compliant · repo-map indexed + drift hook".
- This session's artifacts: `implementation_plan.md`, this `walkthrough.md`, `task-list.md`, `settings.json.proposed`;
  `active-context.md` + `INDEX.md` updated.

## ⚠️ ONE thing I could NOT do (auto-mode guardrail) — Daniel applies it
Editing `.claude/settings.json` to add a SessionStart hook (with `-ExecutionPolicy Bypass`) was blocked as
"self-modifying startup config." **You apply the hook** — replace the file's contents with the saved
`./settings.json.proposed` (it preserves your existing `permissions` block and only adds `hooks`). The drift
*script* it calls is already in place and tested.

## Verification (real output)
- **Drift script — no false positives:** `check-repo-map-drift.ps1` → silent, `exit=0` (map current).
- **Drift script — nag fires:** created `_drifttest/` → printed
  `[repo-map drift] top-level folders on disk but NOT in docs/repo-map.md:  - _drifttest/` → `exit=0`; folder removed.
- **Hook commands proven** (with `CLAUDE_PROJECT_DIR` = clean-bmad): `cmd1 active-context resolves: True`,
  `cmd1 repo-map resolves: True`; `cmd2` drift call → `exit=0`.
- **Repo-map generator:** `python scripts/generate_repo_map.py --ignore _bmad` → `exit=0`, AUTO body now lists
  `check-repo-map-drift.ps1`.
- **git status (clean-bmad):** `M AGENTS.md`, `M README.md`, `M _bmad-output/project-context.md`,
  `M docs/repo-map.md`, `?? scripts/check-repo-map-drift.ps1`.
- **Product-residue grep** (authored files, excl. `_bmad/.agents/.claude/.opencode/_my_resources`): clean —
  only a false positive (a `package-lock.json` hash) + one example slug `sully` in an autopilot-engine comment
  (`scripts/autopilot-dev-story.ps1:168`, optional to genericize). **Stack kept; product DNA gone.**

## ⚠️ Your Actions (I do not commit/push — git-policy)

**0) Apply the SessionStart hook (clean-bmad):** copy `./settings.json.proposed` over
`Projects/clean-bmad-workspace/.claude/settings.json` (review first; drop `-ExecutionPolicy Bypass` if your
policy already allows local scripts). Open a fresh session in clean-bmad to confirm the map injects + drift runs.

**1) clean-bmad repo:**
```bash
cd "c:/Sudo_Hatter_Command/Projects/clean-bmad-workspace"
git add -A
git status                      # AGENTS.md, README.md, _bmad-output/project-context.md, docs/repo-map.md,
                                # scripts/check-repo-map-drift.ps1, .claude/settings.json (after step 0)
git commit -m "feat: re-purpose into the AGY quick-start project skeleton (home-base-aligned) + hybrid auto-updating repo-map hook (SessionStart inject + drift nag)"
git push
```

**2) home-base repo:**
```bash
cd "c:/Sudo_Hatter_Command"
git add -A
git status
git commit -m "docs: clean-bmad is now the AGY quick-start skeleton (router row); reshape artifacts"
git push
```

## Open / next
- **WS7 follow-up (offered):** promote `check-repo-map-drift.ps1` → master `.agents/scripts/` and wire the
  *home base's* own SessionStart hook to it (keeps home base ↔ projects on one mechanism, no divergence).
- **Prune aviationChat skills** from the vendored `.agents/` set (generic-skeleton sync profile at master +
  `/sync-agents`) — the biggest remaining aviationChat-DNA removal; anti-fork, so it's master-level, not here.
- `_claude_artifacts/` full retirement (pending master pass; check the autopilot `$RepoRoot` first).
