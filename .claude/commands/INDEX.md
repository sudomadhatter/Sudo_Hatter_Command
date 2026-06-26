# Commands INDEX — when to use which

Router for `.agents/commands/`. **Scan to dispatch.** Each command is invoked as `/<name>` (or by
natural-language intent) and carries its own frontmatter `description:`; this groups them by purpose.
Synced into `.claude/commands/` + `.opencode/commands/` by `/sync-agents`.

| Group | Commands | Reach for it when… |
|---|---|---|
| **BMAD agent personas** | `analyst` (Mary) · `architect` (Winston) · `dev` (Amelia) · `pm` (John) · `qa`/`tea` (Murat) · `sm` · `tech-writer` (Paige) · `ux-designer` (Sally) · `quick-flow-solo-dev` (Barry) | you want a specific BMAD role to drive (planning, design, story dev, QA). |
| **BMAD routing** | `bmad-help` · `bmad-master` | unsure which agent/workflow — ask for a recommendation. |
| **Autopilot (Claude-only engine)** | `autopilot` · `bmad-dev-story_AP` · `1_self-audit-stress-test_AP` · `bmad-code-review_AP` | run the autonomous Dev/QA loop on one story (`/autopilot <story>`). `_AP` = headless agent-to-agent variants; don't invoke directly. |
| **Session / project ops** | `1_ccps_boot-context` · `1_ccps_update-active-context` · `1_run-restart-dev-env` · `1_run-all-tests-back_front` · `1_check-for-tech-stack-updates` · `1_clean-test-scripts` · `1_live_testing_team` · `1_make-workflow-from-chat` · `1_update-maps` · `1_self-audit-stress-test` · `1_firebase-user-cleanup` · `1_push-to-main-and-deploy` | boot/save context, restart the dev env, run tests, live-debug, tidy, reconcile the repo-map + every INDEX (`1_update-maps`) — the day-to-day project chores. |
| **System builder** (lobby) | `new-project` · `sync-agents` · `slash_command_updating` | scaffold a workspace, push the master toolkit into a target, or refresh global command caches. |
| **Media** | `webm-alpha-video` | convert a green-screen MP4 to alpha WebM. |

**Adding a command:** create `<name>.md` with a `description:` frontmatter stating when it fires, add it
to the right group above, and re-run `/sync-agents`.
