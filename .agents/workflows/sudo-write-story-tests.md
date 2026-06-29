---
description: Story prep — create the next BMAD story, then write its failing acceptance tests (ATDD red phase) before any code. Step ① of the sudo dev flow.
platforms: [opencode, antigravity]
---

# /sudo-write-story-tests — Create Story + Red Tests (①)

Thin orchestrator — calls two existing workflows back-to-back so a story arrives with its acceptance
tests already written and **failing**. Tests-first, before any dev. Project-scoped (targets THIS repo).

> Flow position: `sudo-boot-sprint-memory` → **`sudo-write-story-tests`** → `sudo-dev-story-tests` →
> `sudo-code-review` → `sudo-update-sprint-memory`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Run from the **command center** (the lobby), this command operates on exactly ONE child project under
`Projects/`, never the lobby itself. Resolve the target now:
0. **Self (sub-project fast path — check this FIRST, and STOP here if it matches)** — if this repo has
   **no** `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip straight to the
   binding rule. Do NOT read `active-project.txt`, parse `$ARGUMENTS` for a project name, or ask which
   project — cases 1–3 below are command-center-only (the lobby that hosts children under `Projects/`).
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is
   the target; consume that first token (the remainder is the real argument — story id, focus, …). Write
   the name alone into `_my_resources/active-project.txt` (overwrite) so later commands inherit it.
2. **Active pointer** — else read `_my_resources/active-project.txt`; if it names a folder under
   `Projects/`, use it.
3. **Ask** — else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"* —
   never guess, never operate on the lobby.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

**Binding rule (applies to EVERY step below):** every "THIS repo", every `{project-root}`, and every bare
path (`_bmad-output/…`, `_bmad/…`, `_artifacts/…`, story files, `implementation_plan.md`, test commands)
resolves **under `PROJECT_ROOT`**. When you invoke any nested `bmad-*` / `1_*` skill, bind its
`{project-root}` to `PROJECT_ROOT`, run it against that directory, and read/write only there. If a needed
path is missing under `PROJECT_ROOT`, STOP and say so — never fall back to the lobby.

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
