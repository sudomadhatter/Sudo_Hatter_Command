---
name: 000-PLAN-FIRST-GATE
description: "PRIORITY ZERO — No project file may be modified until Daniel approves an implementation_plan.md. No skill, workflow, or slash command overrides this. Read this FIRST."
activation: Always On
---

# 🛑 PRIORITY ZERO: Plan First, Code Never (Until Approved)

> This rule OVERRIDES every skill, workflow, and slash command — including BMAD dev-story, quick-dev, create-story, and any future skill that has its own "execute" steps. If a skill says "mark in-progress" or "implement now," STOP — that instruction is subordinate to this gate.

## The Kill-Chain

Before modifying ANY project file, walk this chain:

1. **Do I have an `implementation_plan.md` artifact in the current conversation?** → If NO: create one. STOP.
2. **Has Daniel said the exact phrase "approved"?** → If NO: STOP. Wait.
3. **Both conditions met?** → Proceed to modify project files.

There are NO shortcuts. There are NO implied approvals.

## What Counts as a Project File

EVERYTHING in the working tree:
- Source code (`.tsx`, `.ts`, `.py`, `.css`, etc.)
- Story files (`_bmad-output/implementation-artifacts/**`)
- Sprint tracking (`sprint-status.yaml`)
- Configuration (`.env`, `package.json`, `pyproject.toml`, etc.)
- Agent configs, YAML metadata, any dotfile

The ONLY exception: the opencode artifact directory `_artifacts/` itself (where `implementation_plan.md`, `task.md`, and `walkthrough.md` live). This directory is auto-allowed by `opencode.json` `permission.edit` so writes don't prompt.

## What is NOT Approval

- "ok", "sure", "looks good", "continue", "let's go", "ready-for-dev"
- A plan from a prior conversation
- A story file with status `ready-for-dev`
- A BMAD skill step that says "mark in-progress" or "begin implementation"

## The Plan Must Contain

1. Goal and background context
2. Proposed changes grouped by component/file (with clickable file links)
3. Open questions needing Daniel's input
4. Verification plan (exact test commands)

Present key points inline in the chat AND link the artifact. Daniel reviews plans he can **see in the conversation**, not just files on disk.

## BMAD Skill Integration

BMAD skills (`bmad-dev-story`, `bmad-quick-dev`, etc.) have execution steps that mutate project files — updating story status, sprint-status.yaml, writing code. **Those steps are subordinate to this gate.** The correct execution order when a BMAD skill is invoked:

1. Run the skill's research/discovery steps (read-only)
2. Use the skill's context to write `implementation_plan.md` (artifact only)
3. Present the plan to Daniel with key points inline
4. **STOP — wait for "approved"**
5. THEN resume the skill's execution/implementation steps

## After Approval — The Sequence

1. Create `task.md` artifact — checklist of tasks, mark `[ ]` → `[/]` → `[x]` as you work
2. Execute the plan — NOW modify project files (story status, sprint-status, code)
3. Create `walkthrough.md` artifact — what changed, actual test output, deviations from plan
4. End-of-task checklist in final message (what was built, Daniel's action items, blockers, BMAD backfill)

## When to Skip

- **Investigatory requests** ("explain how X works", "where is Y?") — no plan needed
- **Trivial one-liners** (typo, comment, formatting) — mention what you changed, skip full cycle
- **Daniel explicitly says** "skip the plan, just do it" — still write a walkthrough after

## Violation Examples

❌ "The bmad-dev-story skill said to mark the story in-progress, so I updated sprint-status.yaml before creating a plan." — VIOLATION. Sprint-status is a project file.

❌ "The story was simple (1 file, surgical change), so I skipped the plan." — VIOLATION. Scope does not override this gate.

❌ "I created the implementation_plan.md and Daniel said 'looks good', so I started coding." — VIOLATION. "Looks good" is not "approved."

❌ "I loaded the BMAD dev-story skill and it has <critical> tags saying 'execute continuously, do NOT stop' — so I followed those." — VIOLATION. No skill overrides this gate. Period.
