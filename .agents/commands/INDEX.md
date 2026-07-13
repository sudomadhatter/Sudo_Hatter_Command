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

**Platform reach.** A command may add `platforms: [claude, opencode, antigravity]` to its frontmatter to
limit where it syncs. **Absent = universal** (all three). Tagged today: `autopilot_claude`, `autopilot_mobile`,
`sudo-dev-story-tests_AP`, `sudo-self-audit_AP`, `sudo-code-review_AP` → `[claude]`; `autopilot_opencode`
→ `[opencode]`.

| Group | Commands | Reach for it when… |
|---|---|---|
| **BMAD agent personas** | `analyst` (Mary) · `architect` (Winston) · `dev` (Amelia) · `pm` (John) · `qa`/`tea` (Murat) · `sm` · `tech-writer` (Paige) · `ux-designer` (Sally) | you want a specific BMAD role to drive (planning, design, story dev, QA). |
| **BMAD routing** | `bmad-help` · `bmad-master` | unsure which agent/workflow — ask for a recommendation. |
| **BMAD test architecture** (commands) | `testarch-atdd` · `testarch-automate` · `testarch-ci` · `testarch-framework` · `testarch-nfr` · `testarch-test-design` · `testarch-test-review` · `testarch-trace` | thin slash-command wrappers that invoke the matching `bmad-testarch-*` skill (ATDD red-phase, automate coverage, CI pipeline, framework init, NFR audit, test design, test review, traceability matrix). |
| **Autopilot (Claude-only engine)** | `autopilot_claude` · `sudo-dev-story-tests_AP` · `sudo-self-audit_AP` · `sudo-code-review_AP` | run the autonomous Dev/QA loop on one story (`/autopilot_claude <story>`). `_AP` = headless agent-to-agent variants; don't invoke directly. |
| **Autopilot (opencode engine)** | `autopilot_opencode` *(stub — not built yet)* | the opencode-native sibling of `/autopilot_claude`. Separate pipeline (opencode CLI, not headless `claude -p`); currently a spec placeholder that just tells you to use `/autopilot_claude`. |
| **Autopilot (cloud/mobile)** | `autopilot_mobile` | the web/mobile port of `/autopilot_claude` — runs the same 4-stage Dev/QA pipeline on the in-environment Workflow engine (no PowerShell/CLI), so it works on Claude Code web + mobile. |
| **Sudo dev flow** (TEA-gated, human lane) | `sudo-boot-sprint-memory` · `sudo-create-epics-stories-sprint` · `sudo-write-story-tests` · `sudo-dev-story-tests` · `sudo-self-audit` · `sudo-code-review` · `sudo-update-sprint-memory` | two phases — **epic kickoff** (`sudo-create-epics-stories-sprint`: create epic + stories → sprint → interactive P0–P3 risk-score, once per epic) then the **per-story loop** with testing baked in: boot/pick-up → write red tests → plan+self-audit+implement+automate → review+gate → close-out save. Run in that order; `sudo-self-audit` auto-runs inside `sudo-dev-story-tests`. The gate (suite + TEA trace/nfr/test-review → PASS/CONCERNS/FAIL/WAIVED) lives inside `sudo-code-review`. |
| **Sudo quick-fix flow** (fast track) | `sudo-quick-dev` | fast-track dev flow — write the story, develop the fix directly, run a light post-dev sanity audit, and close out to log it. Bypasses strict ATDD tests and code reviews. |
| **Session / project ops** | `1_run-restart-dev-env` · `1_run-all-tests-back_front` · `1_check-for-tech-stack-updates` · `1_clean-test-scripts` · `1_live_testing_team` · `1_make-workflow-from-chat` · `1_firebase-user-cleanup` · `1_push-to-main-and-deploy` · `merge_main_debug` · `1_update-maps` | restart the dev env, run the full test suite (also invoked by `sudo-code-review`'s gate), live-debug, tidy, refresh the repo map + INDEXes + open-tasks list — the day-to-day project chores. `1_update-maps` from the top **fans out across the lobby + every project** (open-tasks list included); `merge_main_debug` — merge a reviewed PR into `main_debug` (the per-action approval button). |
| **System builder** (lobby) | `new-project` · `sync-agents` · `slash_command_updating` | scaffold a workspace, push the master toolkit into a target, or refresh global command caches. |
| **Media** | `webm-alpha-video` | convert a green-screen MP4 to alpha WebM. |

**Adding a command:** create `<name>.md` with a `description:` frontmatter stating when it fires (add an
optional `platforms:` line only if it's not universal), add it to the right group above, and re-run
`/sync-agents` to propagate to all platforms + the global caches.
