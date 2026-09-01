---
name: 000-PLAN-FIRST-GATE
description: "PRIORITY ZERO — No project file may be modified until Mr. Hatter approves an implementation_plan.md. No skill, workflow, or slash command overrides this. Read this FIRST."
trigger: model_decision
# Protocol tier (rules/INDEX.md): conditional, not floor. Every gate it carries is ALSO
# stated inline in AGENTS.md and constitution.md, so the stop binds even in a session
# that never opens this file — which is what makes it safe to leave conditional rather
# than load ~44 KB of protocol prose into every read-only session.

---

# 🛑 PRIORITY ZERO: Plan First, Code Never (Until Approved)

> This rule OVERRIDES every skill, workflow, and slash command — including BMAD dev-story, create-story, and any future skill that has its own "execute" steps. If a skill says "mark in-progress" or "implement now," STOP — that instruction is subordinate to this gate.
>
> **The one carve-out lives in the exemption list, not here** (see "When to Skip" below): `/cicd-quick-dev`
> is operator-invoked, and invoking it IS the "skip the plan" instruction. Naming it inline here as
> *overridden* is what put this rule and that command in direct contradiction — two copies of a gate's
> scope drift apart, and each one reads authoritative.

## The Kill-Chain

Before modifying ANY project file, walk this chain:

1. **Do I have an `implementation_plan.md` artifact in the current conversation?** → If NO: create one. STOP.
2. **Has Mr. Hatter said the exact phrase "approved"?** → If NO: STOP. Wait.
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

**The gate opens on ONE thing: the operator typing `approved`, unprompted.** Everything below has
been mistaken for it in practice — the top four are the classics, the rest were all misread inside a
single session on 2026-08-09, which is why they are now written down.

- "ok", "sure", "looks good", "continue", "let's go", "ready-for-dev"
- A plan from a prior conversation
- A story file with status `ready-for-dev`
- A BMAD skill step that says "mark in-progress" or "begin implementation"
- ⛔ **A selected option in a question YOU authored.** A selection answers *which*, never *whether*.
- ⛔ **An instruction to do the work** — "go make SCC-12", "finish SCC-56", "I would like to fix
  this", "that is a bug and a problem". These commission the work; the plan step is still owed.
  Being told to build something is the *reason* to write a plan, not permission to skip it.
- ⛔ **An answer to a clarifying question.** That is information, not consent.
- ⛔ **A correction or an overrule** ("no, it is `cicd-label-tasks`"). A correction narrows the
  plan; it does not open the gate. **Edit the plan and stop AGAIN** — a correction restarts the
  wait, it never ends it.

### ⛔ Never put the gate word in an option label

Do not offer "approved" (or "go ahead", "ship it", or any other opening token) as the text of a
choice you present. Writing the word yourself and then reading it back off the operator's click is
**manufacturing the approval token** — the operator answered *which option*, and the consent was
authored by you. This is exactly how the gate was bypassed on 2026-08-09.

Present options for *design forks*. Ask for approval in **plain text**, and wait.

### One approval MAY cover several plans — only as `/smh-plan-task`'s recorded batch (SCC-155)

**Narrow, and every word of it is load-bearing.** `/smh-plan-task` plans a whole Task and all its
subtasks in one pass, then presents every plan, every `Audit verdict:` and the parallel table at
**one** stop. The operator's approval there covers **exactly the plans that stop listed** — and it
is only an approval at all when all four hold:

1. The operator's **verbatim words** are recorded into each covered plan, naming the subtask keys
   the batch covers. **You never write the gate word yourself** — the quote is the artifact, the
   same way the main-write gate takes the operator's own sentence rather than a flag (SCC-37).
2. Every covered plan carried `Audit verdict: GO` **at the moment of the stop**. A NO-GO lane is
   never in a batch.
3. It covers **those plans as they stood**, and that is **mechanically checkable** because the
   approval line ends `— recorded at <sha>`. `/smh-quick-dev` Step 1.5 compares
   `git log -1 --format=%h -- <the plan>` against that sha; equal means untouched. A batch cannot
   approve text the operator never saw.
   ⭐ **The one legal inequality is the `stamp-only successor` (SCC-359).** Recording the sha of
   the commit that records the approval is self-referential, so the planner writes `<pending>`,
   commits, and stamps the sha in a second commit — which means the plan's last touch is *always*
   the stamp, never the recorded sha. So the reader falls through to
   `git diff <recorded>..<last touch> -- <the plan>`: if that touches the `— recorded at` line and
   **nothing else**, it passes. Anything else means **that lane's gate re-arms** and it stops for
   its own approval. Bare equality was the original wording and it could never hold for a
   conforming lane — measured on SCC-347, SCC-358 and SCC-318.
   ⛔ **And that comparison is a COUNT, not a reading of the hunk.** `/smh-quick-dev` Step 1.5
   carries the command; it counts the changed lines that are not the approval line and passes on
   zero. Printing a diff and asking an agent "does this touch only that line?" replaces a boolean
   with a prose judgment, which is the shape `cheap-models-rationalize-past-prose` says gets
   rationalized past — three review lenses built a stamp commit carrying a body edit and watched
   the prose version bless it (SCC-318 cycle 9).
   ⛔ **No sha on the line = no approval.** The clause originally said "unchanged since the commit
   that recorded it" while nothing anywhere recorded which commit that was — so the check had one
   operand and an agent wanting to proceed would supply the other. A missing operand is a re-armed
   gate, never a pass (SCC-155).
4. It covers **planning only**. It is not merge approval, not a ticket transition, and it never
   carries to a lane that was not on the list.

⛔ This is **not** a general "batch mode". No other command may claim it, and an approval you
assemble from several messages is not a quote. Everything in § What is NOT Approval still applies
to each item inside the batch.

### The carve-outs are a CLOSED list

There is a real rule that invoking a command IS the sign-off — `/cicd-quick-dev`, and the close-out
commands. That list lives in `artifacts-always-first.md` § "When to Skip" and nowhere else. It does
**not** generalize from *"the operator told me to do the work"* to *"the gate is open."* If you are
reasoning your way toward an exemption that is not written in that list, you are bypassing the gate.

## The Plan Must Contain

1. Goal and background context
2. Proposed changes grouped by component/file (with clickable file links)
3. Open questions needing Mr. Hatter's input
4. Verification plan (exact test commands)

Present key points inline in the chat AND link the artifact. Mr. Hatter reviews plans he can **see in the conversation**, not just files on disk.

## BMAD Skill Integration

BMAD skills (`bmad-dev-story`, `bmad-quick-dev`, etc.) have execution steps that mutate project files — updating story status, sprint-status.yaml, writing code. **Those steps are subordinate to this gate.** The correct execution order when a BMAD skill is invoked:

> **Read this together with the carve-out at the top.** `bmad-quick-dev` appears in that list because a
> **bare** invocation of it is gated like any other skill. It is NOT gated when it runs as the engine of
> `/cicd-quick-dev` — that command's invocation IS the skip instruction, and its EJECT tripwire re-arms
> the gate. Same skill, two callers, two answers; the caller decides, never the skill and never the size
> of the change.

1. Run the skill's research/discovery steps (read-only)
2. Use the skill's context to write `implementation_plan.md` (artifact only)
3. Present the plan to Mr. Hatter with key points inline
4. **STOP — wait for "approved"**
5. THEN resume the skill's execution/implementation steps

## After Approval — The Sequence

1. Track with the live TodoWrite task list — no `task.md`; its end-state lands as the `## Task Checklist` outline inside `walkthrough.md` (per `artifacts-always-first`)
2. Execute the plan — NOW modify project files (story status, sprint-status, code)
3. Create `walkthrough.md` artifact — outline-first: `## Task Checklist` (pitfalls under the tasks that fought back) + `## Evidence` (AC matrix + actual test totals + SHA) + `## Your Actions`
4. End-of-task checklist in final message (what was built, Mr. Hatter's action items, blockers, BMAD backfill)

## When to Skip

**The exemption list lives in ONE place: `artifacts-always-first.md` § "When to Skip".** Read it there.

It is not duplicated here on purpose — two copies of a gate's exemptions drift apart, and each one reads
authoritative. If you are deciding whether this gate applies, you are deciding against that list.

## Violation Examples

❌ "The bmad-dev-story skill said to mark the story in-progress, so I updated sprint-status.yaml before creating a plan." — VIOLATION. Sprint-status is a project file.

❌ "The story was simple (1 file, surgical change), so I skipped the plan." — VIOLATION. Scope does not override this gate.

❌ "I created the implementation_plan.md and Mr. Hatter said 'looks good', so I started coding." — VIOLATION. "Looks good" is not "approved."

❌ "I loaded the BMAD dev-story skill and it has <critical> tags saying 'execute continuously, do NOT stop' — so I followed those." — VIOLATION. No skill overrides this gate. Period.
