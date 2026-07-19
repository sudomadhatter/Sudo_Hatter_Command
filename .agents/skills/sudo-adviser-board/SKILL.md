---
name: sudo-adviser-board
description: 'Convene the Adviser Board — open-table brainstorm of historical minds in 5 challenge teams (First Principles, Ground Truth, Ruin & Ripple, Unconventional Leverage, Human Needs) + an on-call Real-World marketing squad anchored by Hormozi. Flips assumptions, sees around corners, surfaces what people NEED not what they want. Phased: Brainstorm → Plan → Market → BMAD build handoff. Use when the user says "convene the board" / "adviser board" / "sudo adviser board <topic>".'
---

# /sudo-adviser-board — command center launcher

Lobby entry point for the Adviser Board — the open-table challenger brainstorm. Runs IN the command
center (no child-project targeting); session briefs land in `_my_resources/board_sessions/`.

**Execute now:** read `.agents/commands/sudo-adviser-board.md` (relative to the repo root) and follow it
END TO END — activation, phased arc (Brainstorm → Plan → Market → BMAD handoff), real-subagent spawns per
team unless `--solo`. Pass `$ARGUMENTS` through verbatim (topic + optional `--solo` / `--model <m>` flags).
