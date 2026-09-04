---
name: agent-memory-is-long-term-only
description: "Agent memory is for long-term facts only: operator preferences, recurring machine and tooling quirks, and standing rulings. Story-scoped findings go in the story file or artifacts; delete story-scoped memories on sight; narrate every write in chat in one line. Load when reading, writing, auditing, or pruning agent memory."
trigger: model_decision
triggers: [memory, remember, save to memory, note for later, MEMORY.md, auto-memory, memory audit]
---

# Agent Memory Is Long-Term Only

Memory holds only what must be remembered for a long time: how Mr. Hatter wants to be worked with,
machine and tooling quirks that recur across projects, and standing rulings. A finding tied to one
story or one fix belongs in that story's file or its `_artifacts/` walkthrough, where the next lane
reads it and where it retires with the story.

> **Operator ruling (2026-09-04, SCC-386):** *"Those should be in the story, not memory that will
> not be used after this story is done. Only keep things we need to remember for a long time — we
> have to clean up and delete memories."*

## The One Test

Before saving ANY memory — auto-memory, manual note, or close-out routing — ask:

> **"Will this still be true and still be useful after this story closes?"**

- **NO** → It is a **story fact**. Put it in the story file (`_bmad/bmm/stories/`), the session
  walkthrough (`walkthrough.md`), or the audit under `_artifacts/`. It stays in the project history,
  informs the immediate follow-ons, and retires cleanly when the story lands.
- **YES** → It is a candidate for memory. Author it concisely following the memory store rules.

## What Qualifies for Memory

Memory is an expensive shared context cost paid by every future session on every platform. Only three
categories earn a permanent home:

1. **Operator preferences and profile**: how Mr. Hatter thinks, directs work, reviews, and
   communicates (the Jobs/Woz division of labor; consequence before mechanism; directness).
2. **Machine and tooling quirks**: persistent toolchain behavior that recurs across stories and
   projects (macOS vs Windows vs WSL differences, `acli` CLI syntax and flag traps, SDK bugs, shell
   quoting traps, permission quirks).
3. **Standing rulings**: durable architectural, testing, or workflow decisions that govern future
   lanes and projects.

## What Never Qualifies (Prohibited in Memory)

The following must **never** be saved to agent memory:

- **Measurements**: benchmark numbers, execution times, character counts, or byte savings from a run.
- **A bug's mechanism**: root-cause explanations of a defect being patched. The fix, its test, and
  the story record capture that permanently.
- **Gate mismatches & temporary failures**: CI mismatches, broken checks, or pipeline failures that a
  ticket is actively fixing (e.g. the Epic 24 CI scope mismatch that AVCH-119 resolves). Saving them
  creates stale noise the moment the fix lands.
- **Story tasks & intermediate notes**: task checklists, in-flight status, or temporary observations.

## The Delete-on-Sight Duty

Story-scoped notes rot into deceptive distractions that cause agents to fight ghost issues months
later.

Whenever you read, review, or audit a memory store (the lobby `_artifacts/_memory/`, local platform
stores like `~/.claude/projects/*/memory/` which symlink into the shared checkout, or project stores):
- If you find a note that is story-scoped, obsolete, or tied to a single resolved fix,
  **delete it on sight** (and remove its entry from `MEMORY.md` in the same commit to preserve
  link↔file integrity).
- Do not amend, soften, or archive temporary facts into permanent memory — remove them. Git history is
  the undo mechanism if anything historical is ever needed.
- ⛔ **Never delete another session's in-flight uncommitted memory** (`AGENTS.md` §7 authorship gate).
  If deleting on an active lane, perform the deletion in your worktree and commit it on the branch; never
  mutate the shared checkout directly.

## The Narrate-Every-Write Duty

Every time an agent writes, creates, or updates a memory file (including automatic memory captured by
platform harnesses), it must:
- **State in chat, in one line, exactly what was saved.**
- This keeps memory generation visible to Mr. Hatter in real time so invalid or story-scoped notes can
  be challenged and pruned immediately.
