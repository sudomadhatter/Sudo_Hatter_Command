---
name: command-surface-restructure-2026-07-14
description: "The 2026-07-14 command renames (security_team_aviationchat, update-maps-indexes, sudo-live-testing-team, sudo-push-e2e, new /sudo-e2e), the robot-lane _AP vendor rule, and the guide split — old names are ghosts everywhere."
metadata: 
  node_type: memory
  type: project
  originSessionId: 2cea4173-7206-4a2e-bcc0-2ce0ab82231c
---

2026-07-14 restructure (Daniel: "menus confusing; need e2e before main; guide unusable"). The map:
`sudo-incident-response` → **`security_team_aviationchat`** (platforms `[opencode, antigravity, codex]` — deliberately NOT claude; reverts the Gemini agent's e4d51de claude-add; it is the DRILL harness, the always-live pipeline never invokes it) · `1_update-maps` → **`update-maps-indexes`** · `1_live_testing_team` → **`sudo-live-testing-team`** (revamped: boots dev env + log-watch + DevTools coaching + researched bug docs) · `1_push-to-main-and-deploy` → **`sudo-push-e2e`** (paths A debug-push / B full-merge / C cherry-pick; **B/C hard-require `/sudo-e2e` GREEN before touching main**; C ends with back-merge main→main_debug per [[git-branch-model-standard]]) · NEW **`/sudo-e2e`** wraps the TEA-16 harness ([[agy-learner-e2e-harness]]). Deleted: `1_run-all-tests-back_front` (③ runs suites directly — sudo-code-review Step 3 patched), `1_run-restart-dev-env` (absorbed), + 4 more stale `1_*`.

**Why:** two lanes — human commands vs robot commands; robot/rare stuff must not sit in the typing menus.

**How to apply:**
- **Robot-lane rule:** `sync-agents.ps1 Sync-CommandDir -SkipAP` — `*_AP` vendors ONLY into project tool dirs (engines `Push-Location` into the project; verified in `Projects/*/scripts/autopilot-dev-story*.ps1`). Lobby menus + global caches skip `_AP` and auto-purge strays each sync. Never re-add `_AP` files to lobby `.claude/.opencode`.
- The wrapper-guard in the AG mirror is now `$excluded = @('update-maps-indexes.md')` (command is a wrapper; the real workflow differs — don't let the mirror clobber it).
- Old names may linger in unmaintained projects (JETCHAT, BRKN — expected), historical ledgers, and `tea_deep_reference.md` (its header carries the old→new map — the 825-line guide was split: quick reference `sudo_workflows_testing.md` ~280 lines + that deep companion).
- Known owed: AGY `backend/routers/incident.py` docstring still claims routines=primary (as-built primary = GitHub Actions lane); 1-line fix, Daniel's call.
