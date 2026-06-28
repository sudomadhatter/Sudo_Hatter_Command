---
description: Story prep — create the next BMAD story, then write its failing acceptance tests (ATDD red phase) before any code. Step ① of the sudo dev flow.
---

# /sudo-write-story-tests — Create Story + Red Tests (①)

Thin orchestrator — calls two existing workflows back-to-back so a story arrives with its acceptance
tests already written and **failing**. Tests-first, before any dev. Project-scoped (targets THIS repo).

> Flow position: `sudo-boot-sprint-memory` → **`sudo-write-story-tests`** → `sudo-dev-story-tests` →
> `sudo-code-review` → `sudo-update-sprint-memory`.

## Step 1 — Create the story
Invoke the **`bmad-create-story`** skill for the story in `$ARGUMENTS` (a story id like `11.16`, or "the
next story" when empty). This writes the story file under `_bmad/bmm/stories/` with its acceptance
criteria (ACs). Confirm the story file + ACs exist before continuing. If create-story stops for input,
surface it and stop — never guess.

## Step 2 — Write the failing acceptance tests (ATDD red phase)
Invoke the **`bmad-testarch-atdd`** skill against the story just created. Generate acceptance tests that
codify each AC and **must fail now** (no implementation exists yet). If the epic has a
`bmad-testarch-test-design` risk plan, pull it so P0 ACs get priority coverage.

## Done
Report: story id + path, ACs covered, the red tests written (paths) and confirmation they fail as
expected. Leave them staged — `sudo-dev-story-tests` turns them green next. **Do NOT start implementing.**

Optional additional input: $ARGUMENTS
