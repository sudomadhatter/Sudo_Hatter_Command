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
`autopilot_mobile`, `sudo-mobile-error-team` → `[claude]`; `autopilot_opencode` → `[opencode]`; the `_AP` trio → `[claude, opencode]`;
`security_team_aviationchat` → `[opencode, antigravity, codex]` (deliberately NOT in the Claude menu);
`sudo-adviser-board` → `[claude, opencode, codex]` (25k body exceeds Antigravity's 12k workflow limit — AG gets the hand-authored thin launcher `.agents/workflows/sudo-adviser-board.md`, prune-protected in the sync's `$excluded` list).
**Robot-lane rule (2026-07-14):** `*_AP` commands vendor ONLY into project tool dirs (where the autopilot
engines read them) — the sync skips them for the lobby menus and the global caches.

| Group | Commands | Reach for it when… |
|---|---|---|
| **BMAD agent personas** | `analyst` (Mary) · `architect` (Winston) · `dev` (Amelia) · `pm` (John) · `qa`/`tea` (Murat) · `sm` · `tech-writer` (Paige) · `ux-designer` (Sally) | you want a specific BMAD role to drive (planning, design, story dev, QA). |
| **BMAD routing** | `bmad-help` · `bmad-master` | unsure which agent/workflow — ask for a recommendation. |
| **BMAD test architecture** (commands) | `testarch-atdd` · `testarch-automate` · `testarch-ci` · `testarch-framework` · `testarch-nfr` · `testarch-test-design` · `testarch-test-review` · `testarch-trace` | thin slash-command wrappers that invoke the matching `bmad-testarch-*` skill (ATDD red-phase, automate coverage, CI pipeline, framework init, NFR audit, test design, test review, traceability matrix). |
| **Autopilot (Claude-only engine)** | `autopilot_claude` · `autopilot_deepseek4` · `sudo-dev-story-tests_AP` · `sudo-self-audit_AP` · `sudo-code-review_AP` | run the autonomous Dev/QA loop on one story (`/autopilot_claude <story>`). `_AP` = headless robot-lane variants; never invoked by a human, live only inside project tool dirs. |
| **Autopilot (opencode engine)** | `autopilot_opencode` | the opencode-native sibling of `/autopilot_claude` — a real, built pipeline (`scripts/autopilot-dev-story-opencode.ps1`, ~826 lines): same 4 stages via the same `_AP` commands, same artifact contract, session continuity, retries, cost caps, independent test gate and story→review flip. Drives `opencode run` instead of `claude -p` (Dev on the selected default model, QA pinned to GLM 5.2 at max). Only gap vs the Claude engine: no per-story concurrency lockfile. |
| **Autopilot (cloud/mobile)** | `autopilot_mobile` | the web/mobile port of `/autopilot_claude` — runs the same 4-stage Dev/QA pipeline on the in-environment Workflow engine (no PowerShell/CLI), so it works on Claude Code web + mobile. |
| **Sudo dev flow** (TEA-gated, human lane) | `sudo-boot-sprint-memory` · `sudo-create-epic-sprint` · `sudo-write-story-tests` · `sudo-bdd-tests` · `sudo-dev-story-tests` · `sudo-self-audit` · `sudo-code-review` · `sudo-update-sprint-memory` | two phases — **epic kickoff** (`sudo-create-epic-sprint`: create epic + stories → sprint → interactive P0–P3 risk-score, once per epic) then the **per-story loop** with testing baked in: boot/pick-up → write red tests (Vision Lock inside) → plan+self-audit+implement+automate → review+gate → close-out save. Run in that order; `sudo-self-audit` auto-runs inside `sudo-dev-story-tests`. The gate (suite + TEA trace/nfr/test-review → PASS/CONCERNS/FAIL/WAIVED) lives inside `sudo-code-review`. |
| **Sudo quick-fix flow** (fast track) | `sudo-quick-dev` | fast-track dev flow — write the story, develop the fix directly, run a light post-dev sanity audit, and close out to log it. Bypasses strict ATDD tests and code reviews. |
| **Shipping** (the e2e gate) | `sudo-e2e` · `sudo-push-e2e` · `merge_main_debug` | `sudo-e2e` runs the hermetic end-to-end suite (emulators + seeded users) → GREEN/RED verdict, solo or as the gate; `sudo-push-e2e` is the ONE shipping command — push `main_debug` (path A), full merge → `main` (B), or cherry-pick features → `main` (C); **B/C refuse to run until `sudo-e2e` is GREEN**, then CI/CD + Cloud Run deploy + live verify + ledger. `merge_main_debug` — merge a reviewed PR into `main_debug` (the per-action approval button). |
| **Live debugging** | `sudo-live-testing-team` | boots backend+frontend, watches backend logs while the human flies the app, coaches the DevTools check, and files researched bug docs that feed the story loop. Writes no code. |
| **Session / project ops** | `update-maps-indexes` · `sudo-switch-machine` | `update-maps-indexes` refreshes the repo map + every INDEX + context hygiene + open-tasks list; from the top it **fans out across the lobby + maintained projects**. `sudo-switch-machine` is the desktop⇄laptop⇄mobile handoff — **park** (commit + sync + push every story worktree branch and both repos, write a resume card) before closing a lid, **resume** (fetch + re-create the worktrees the new machine cannot see) after opening one. Branches travel, worktrees don't; it never lands anything on `main_debug`. |
| **Adviser board** (ideation) | `sudo-adviser-board` | convene the open-table board of historical minds (5 challenge teams + Real-World marketing squad) for an operator-chaired Brainstorm → Plan → Market session; closes with a self-contained brief in `_my_resources/board_sessions/`, ready to seed whatever build workflow the operator calls next. Deep roster reference: `_my_resources/research_docs/sudo-adviser-board-REFERENCE.md`. |
| **Security / error team** | `sudo-mobile-error-team` · `security_team_aviationchat` | **`sudo-mobile-error-team` is the LIVE responder** — the command an incident page tells you to run (`/sudo-mobile-error-team AVIATIONCHAT-42`). It picks up where the machine lane stops: re-verifies the auto-triage report, weighs rollback vs fix-forward with time-to-recovery for both, writes a minimal fix + regression test on `claude/incident-<id>`, gates it on real CI via a draft PR to `main` (the documented hotfix carve-out), and stops twice for Daniel. Never merges on its own initiative. Claude-only (mobile-first). `security_team_aviationchat` is the separate quarterly **DRILL** harness for the same runbook — not the live lane, not in the Claude menu. |
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
