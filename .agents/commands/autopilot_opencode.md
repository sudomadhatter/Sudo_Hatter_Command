---
description: "[STUB — not yet implemented] Autopilot Dev-Story Loop, opencode-native variant. The opencode-native sibling of /autopilot_claude — a separate pipeline that drives opencode (not headless `claude -p`) for the same 4-stage Dev/QA relay (Plan → Audit → Implement → Review+Fix). Does NOT exist yet; this file is the spec/placeholder."
platforms: [opencode]
---

# /autopilot_opencode — Autonomous Story Pipeline (opencode-native) — **STUB**

> **STATUS: NOT IMPLEMENTED.** This is a placeholder/spec. There is no opencode orchestrator script
> behind it yet. Running it should do nothing but print this notice and stop. Use
> `/autopilot_claude` for live autopilot runs today.

This is the **opencode-native** sibling of `/autopilot_claude`. It is intentionally a *separate
pipeline*, not a mirror: `/autopilot_claude` drives headless `claude -p` subprocesses with exact
`--model` pinning and session continuity (`--session-id` / `--resume`) — none of which exist under
opencode. The opencode variant must be authored against opencode's own CLI / session model.

## What to do (until implemented)

1. Tell Daniel this command is a **stub**: the opencode-native autopilot is not built yet.
2. Point him at `/autopilot_claude` for autonomous runs under the Claude CLI.
3. Stop. Do not attempt to launch any orchestrator.

## Intended design (to be built)

Same 4-stage Dev/QA relay as the Claude engine, handing off via artifacts in one shared folder
`_artifacts/<date>_autopilot-<id>/`. The model-agnostic reference for the loop lives at
`.agents/workflows/autopilot_bmad_dev_loop.md` — the opencode engine is a new **Engine Adapter** under
that contract.

| Stage | Teammate | Command → artifact |
|---|---|---|
| 1 Plan | Amelia (Dev) | `/sudo-dev-story-tests_AP plan` → `implementation_plan.md` |
| 2 Audit | Murat (QA) | `/sudo-self-audit_AP` → `self-audit-stress-test.md` |
| 3 Implement | Amelia (Dev) | `/sudo-dev-story-tests_AP implement` → `walkthrough.md` |
| 4 Review+Fix | Murat (QA) | `/sudo-code-review_AP` → `code-review.md` |

### Open design questions before building
- **Session continuity:** does opencode expose a resume/continue primitive equivalent to
  `claude --session-id` / `--resume`? If not, how is per-team chat continuity preserved across a
  team's two stages (or is each stage a fresh session that re-researches)?
- **Model pinning:** how to pin Dev/QA models per stage under opencode (the analogue of `--model`).
- **Headless invocation + autonomy:** the opencode equivalent of `claude -p ... --permission-mode
  bypassPermissions`, and how its output is streamed so the orchestrator can detect stage completion.
- **Orchestrator host:** reuse a PowerShell driver like `scripts/autopilot-dev-story.ps1`, or author
  an opencode-native runner? Keep the same artifact contract + `_RUN-STATUS.md` / resume semantics.

## When implemented, replace this file with the real command and add the orchestrator script.
