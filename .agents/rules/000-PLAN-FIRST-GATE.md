---
name: 000-PLAN-FIRST-GATE
description: "PRIORITY ZERO — No project file may be modified until Daniel approves an implementation_plan.md. No skill, workflow, or slash command overrides this. Read this FIRST."
---

# 🛑 PRIORITY ZERO: Plan First, Code Never (Until Approved)

> This rule OVERRIDES every skill, workflow, and slash command — including BMAD dev-story, create-story, and any future skill that has its own "execute" steps. If a skill says "mark in-progress" or "implement now," STOP — that instruction is subordinate to this gate.
>
> **The one carve-out lives in the exemption list, not here** (see "When to Skip" below): `/sudo-quick-dev`
> is operator-invoked, and invoking it IS the "skip the plan" instruction. Naming it inline here as
> *overridden* is what put this rule and that command in direct contradiction — two copies of a gate's
> scope drift apart, and each one reads authoritative.

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

The ONLY exception: the artifact directory `_artifacts/` itself (where `implementation_plan.md` and `walkthrough.md` live). This directory is auto-allowed by `opencode.json` `permission.edit` so writes don't prompt.

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

1. Track with the live TodoWrite task list — no `task.md`; its end-state lands as the `## Task Checklist` outline inside `walkthrough.md` (per `artifacts-always-first`)
2. Execute the plan — NOW modify project files (story status, sprint-status, code)
3. Create `walkthrough.md` artifact — outline-first: `## Task Checklist` (pitfalls under the tasks that fought back) + `## Evidence` (AC matrix + actual test totals + SHA) + `## Your Actions`
4. End-of-task checklist in final message (what was built, Daniel's action items, blockers, BMAD backfill)

## When to Skip

**The exemption list lives in ONE place: `artifacts-always-first.md` § "When to Skip".** Read it there.

It is not duplicated here on purpose — two copies of a gate's exemptions drift apart, and each one reads
authoritative. If you are deciding whether this gate applies, you are deciding against that list.

## Violation Examples

❌ "The bmad-dev-story skill said to mark the story in-progress, so I updated sprint-status.yaml before creating a plan." — VIOLATION. Sprint-status is a project file.

❌ "The story was simple (1 file, surgical change), so I skipped the plan." — VIOLATION. Scope does not override this gate.

❌ "I created the implementation_plan.md and Daniel said 'looks good', so I started coding." — VIOLATION. "Looks good" is not "approved."

❌ "I loaded the BMAD dev-story skill and it has <critical> tags saying 'execute continuously, do NOT stop' — so I followed those." — VIOLATION. No skill overrides this gate. Period.
