# Commands INDEX — when to use which

Router for `.agents/commands/`. **Scan to dispatch.** Each command is invoked as `/<name>` (or by
natural-language intent) and carries its own frontmatter `description:`; this groups them by purpose.
Synced into `.claude/commands/` + `.opencode/commands/` by `/sync-agents`.

| Group | Commands | Reach for it when… |
|---|---|---|
| **BMAD agent personas** | `analyst` (Mary) · `architect` (Winston) · `dev` (Amelia) · `pm` (John) · `qa`/`tea` (Murat) · `sm` · `tech-writer` (Paige) · `ux-designer` (Sally) · `quick-flow-solo-dev` (Barry) | you want a specific BMAD role to drive (planning, design, story dev, QA). |
| **BMAD routing** | `bmad-help` · `bmad-master` | unsure which agent/workflow — ask for a recommendation. |
| **Autopilot (Claude-only engine)** | `autopilot_claude` · `bmad-dev-story_AP` · `1_self-audit-stress-test_AP` · `bmad-code-review_AP` | run the autonomous Dev/QA loop on one story (`/autopilot_claude <story>`). `_AP` = headless agent-to-agent variants; don't invoke directly. |
| **Autopilot (opencode engine)** | `autopilot_opencode` *(stub — not built yet)* | the opencode-native sibling of `/autopilot_claude`. Separate pipeline (opencode CLI, not headless `claude -p`); currently a spec placeholder that just tells you to use `/autopilot_claude`. |
| **Autopilot (cloud/mobile)** | `autopilot_mobile` | the web/mobile port of `/autopilot_claude` — runs the same 4-stage Dev/QA pipeline on the in-environment Workflow engine (no PowerShell/CLI), so it works on Claude Code web + mobile. |
| **Session / project ops** | `boot-sprint-context` · `update-sprint-context` · `1_run-restart-dev-env` · `1_run-all-tests-back_front` · `1_check-for-tech-stack-updates` · `1_clean-test-scripts` · `1_live_testing_team` · `1_make-workflow-from-chat` · `1_self-audit-stress-test` · `1_firebase-user-cleanup` · `1_push-to-main-and-deploy` · `1_update-maps` | boot/save context, restart the dev env, run tests, live-debug, tidy, refresh the repo map + INDEXes — the day-to-day project chores. |
| **System builder** (lobby) | `new-project` · `sync-agents` · `slash_command_updating` | scaffold a workspace, push the master toolkit into a target, or refresh global command caches. |
| **Media** | `webm-alpha-video` | convert a green-screen MP4 to alpha WebM. |

**Adding a command:** create `<name>.md` with a `description:` frontmatter stating when it fires, add it
to the right group above, and re-run `/sync-agents`.
