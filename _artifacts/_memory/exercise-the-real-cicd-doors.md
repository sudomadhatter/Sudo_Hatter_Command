---
name: exercise-the-real-cicd-doors
description: "When the operator is TESTING the dev system on a real epic (AVCH Epic 19, 2026-08-21), run the actual /cicd-* commands via the Skill tool one story at a time — never hand-roll the steps — and file every command/script defect met on the way as a lettered SUBTASK of the open rolling bugs ticket (SCC-244 cycle), each with a measured defect + file anchor."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3c639bc2-a651-44b4-9cba-8bfac6214e41
  modified: 2026-08-22T01:53:01.140Z
---

**The ruling (2026-08-21, verbatim):** *"no we will be using the cicd commands"* — when I started
hand-rolling ① from the command text — and *"one at a time. you can cut branches for them as you
go"*, *"We develop this whole epic on a seperate branch until we test it. so just cut working trees
off of that."*

**Why:** the point of the session was to exercise the doors (`/cicd-boot-sprint-memory` →
`/cicd-write-story-tests` ×N → `/cicd-label-tasks` → `/cicd-dev-story-tests`), so skipping a step
because I already knew its body hides exactly the defects the operator wants found. Running them
for real on Epic 19 surfaced seven: boot reads the checked-out branch's YAML (epic-only updates
invisible), `link-worktree-assets.py` resolves a submodule to `.git/modules/…` and links nothing,
`jira_feed.py` finds zero ACs in the house `### Theme` story shape and never refreshes a stale
ticket description on reuse, `label_tasks.py` grounds a ①-only lane on a tests-only branch-diff,
and the BMAD story path default disagrees with `_bmad/bmm/stories/`.

**How to apply:** invoke the Skill, echo its Step-0 target, follow the body end to end, and when a
step misbehaves keep going with the explicit workaround (e.g. `--repo`, a hand-written outline)
**and** file it — [[discovered-work-becomes-a-lettered-part]] under the rolling ticket
([[audit-findings-need-a-file-anchor]]: measured defect, anchor, SCOPE, ACCEPTANCE). The Vision
Lock stops are real operator stops (use AskUserQuestion with a recommended default first); every
other decision is mine. Story lanes are cut off the EPIC branch with an explicit base; the shared
checkout stays on `main`. Related: [[to-do-next-is-the-queue]], [[lane-collision-is-gates-not-files]].
