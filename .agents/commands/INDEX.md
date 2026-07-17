---
description: Commands INDEX — catalog of the invocable command set (not a slash command itself)
platforms: []
---

# Commands INDEX — when to use which

Router for `.agents/commands/`. **Scan to dispatch.** Each command is invoked as `/<name>` (or by
natural-language intent) and carries its own frontmatter `description:`; this groups them by purpose.
This is the **single canonical invocable set** — `/sync-agents` mirrors it to every platform: Claude
(`.claude/commands/`), opencode (`.opencode/commands/` + global `~/.config/opencode/commands`), and
Antigravity/Gemini (global `~/.gemini/antigravity/global_workflows` — it calls our commands "workflows").

**Platform reach.** A command may add `platforms: [claude, opencode, antigravity, codex]` to its
frontmatter to limit where it syncs. **Absent = universal** (all four). Tagged today: `autopilot_claude`,
`autopilot_mobile` → `[claude]`; `autopilot_opencode` → `[opencode]`; the `_AP` trio → `[claude, opencode]`;
`security_team_aviationchat` → `[opencode, antigravity, codex]` (deliberately NOT in the Claude menu).
**Robot-lane rule (2026-07-14):** `*_AP` commands vendor ONLY into project tool dirs (where the autopilot
engines read them) — the sync skips them for the lobby menus and the global caches.

| Group | Commands | Reach for it when… |
|---|---|---|
| **BMAD agent personas** | `analyst` (Mary) · `architect` (Winston) · `dev` (Amelia) · `pm` (John) · `qa`/`tea` (Murat) · `sm` · `tech-writer` (Paige) · `ux-designer` (Sally) | you want a specific BMAD role to drive (planning, design, story dev, QA). |
| **BMAD routing** | `bmad-help` · `bmad-master` | unsure which agent/workflow — ask for a recommendation. |
| **BMAD test architecture** (commands) | `testarch-atdd` · `testarch-automate` · `testarch-ci` · `testarch-framework` · `testarch-nfr` · `testarch-test-design` · `testarch-test-review` · `testarch-trace` | thin slash-command wrappers that invoke the matching `bmad-testarch-*` skill (ATDD red-phase, automate coverage, CI pipeline, framework init, NFR audit, test design, test review, traceability matrix). |
| **Autopilot (Claude-only engine)** | `autopilot_claude` · `sudo-dev-story-tests_AP` · `sudo-self-audit_AP` · `sudo-code-review_AP` | run the autonomous Dev/QA loop on one story (`/autopilot_claude <story>`). `_AP` = headless robot-lane variants; never invoked by a human, live only inside project tool dirs. |
| **Autopilot (opencode engine)** | `autopilot_opencode` *(stub — not built yet)* | the opencode-native sibling of `/autopilot_claude`. Separate pipeline (opencode CLI, not headless `claude -p`); currently a spec placeholder that just tells you to use `/autopilot_claude`. |
| **Autopilot (cloud/mobile)** | `autopilot_mobile` | the web/mobile port of `/autopilot_claude` — runs the same 4-stage Dev/QA pipeline on the in-environment Workflow engine (no PowerShell/CLI), so it works on Claude Code web + mobile. |
| **Sudo dev flow** (TEA-gated, human lane) | `sudo-boot-sprint-memory` · `sudo-write-epics-stories-sprint` · `sudo-write-story-tests` · `sudo-bdd-tests` · `sudo-dev-story-tests` · `sudo-self-audit` · `sudo-code-review` · `sudo-update-sprint-memory` | two phases — **epic kickoff** (`sudo-write-epics-stories-sprint`: create epic + stories → sprint → interactive P0–P3 risk-score, once per epic) then the **per-story loop** with testing baked in: boot/pick-up → write red tests (Vision Lock inside) → plan+self-audit+implement+automate → review+gate → close-out save. Run in that order; `sudo-self-audit` auto-runs inside `sudo-dev-story-tests`. The gate (suite + TEA trace/nfr/test-review → PASS/CONCERNS/FAIL/WAIVED) lives inside `sudo-code-review`. |
| **Sudo quick-fix flow** (fast track) | `sudo-quick-dev` | fast-track dev flow — write the story, develop the fix directly, run a light post-dev sanity audit, and close out to log it. Bypasses strict ATDD tests and code reviews. |
| **Shipping** (the e2e gate) | `sudo-e2e` · `sudo-push-e2e` · `merge_main_debug` | `sudo-e2e` runs the hermetic end-to-end suite (emulators + seeded users) → GREEN/RED verdict, solo or as the gate; `sudo-push-e2e` is the ONE shipping command — push `main_debug` (path A), full merge → `main` (B), or cherry-pick features → `main` (C); **B/C refuse to run until `sudo-e2e` is GREEN**, then CI/CD + Cloud Run deploy + live verify + ledger. `merge_main_debug` — merge a reviewed PR into `main_debug` (the per-action approval button). |
| **Live debugging** | `sudo-live-testing-team` | boots backend+frontend, watches backend logs while the human flies the app, coaches the DevTools check, and files researched bug docs that feed the story loop. Writes no code. |
| **Session / project ops** | `update-maps-indexes` | refresh the repo map + every INDEX + context hygiene + open-tasks list; from the top it **fans out across the lobby + maintained projects**. |
| **Security / error team** | `security_team_aviationchat` | DRILL the incident-triage runbook against a Sentry issue (interactive lane). The always-live pipeline is the GitHub Action — this is only its quarterly fire-drill harness. Not in the Claude menu. |
| **System builder** (lobby) | `new-project` · `sync-agents` · `slash_command_updating` | scaffold a workspace, push the master toolkit into a target, or refresh global command caches. |
| **Media** | `webm-alpha-video` | convert a green-screen MP4 to alpha WebM. |

**Renamed / retired (2026-07-14):** `sudo-incident-response` → `security_team_aviationchat` ·
`1_update-maps` → `update-maps-indexes` · `1_live_testing_team` → `sudo-live-testing-team` (revamped) ·
`1_push-to-main-and-deploy` → `sudo-push-e2e` (now carries the mandatory e2e gate) · deleted:
`1_run-all-tests-back_front` (③ runs suites directly), `1_run-restart-dev-env` (absorbed into
`sudo-live-testing-team`), `1_check-for-tech-stack-updates`, `1_clean-test-scripts`,
`1_firebase-user-cleanup`, `1_make-workflow-from-chat` (all recoverable from git history).

**Adding a command:** create `<name>.md` with a `description:` frontmatter stating when it fires (add an
optional `platforms:` line only if it's not universal), add it to the right group above, and re-run
`/sync-agents` to propagate to all platforms + the global caches.
