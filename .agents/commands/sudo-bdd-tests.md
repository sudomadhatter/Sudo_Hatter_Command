---
description: BDD Vision Lock — interactive session to hash out exact expected behaviors until 100% understood, then generate pytest-bdd contracts.
platforms: [opencode, antigravity]
---

# /sudo-bdd-tests — BDD Vision Lock (Step 1a)

Thin orchestrator — initiates an interactive session to finalize the exact behaviors of a story before translating them into strict `pytest-bdd` contracts. This ensures 100% clarity and zero AI drift. Project-scoped (targets THIS repo).

> Flow position: `sudo-boot-sprint-memory` → **`sudo-bdd-tests`** (often via `sudo-write-story-tests`) → `sudo-dev-story-tests`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Run from the **command center** (the lobby), this command operates on exactly ONE child project under `Projects/`, never the lobby itself. Resolve the target now:
0. **Self (sub-project fast path — check this FIRST, and STOP here if it matches)** — if this repo has **no** `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip straight to the binding rule.
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is the target; consume that first token. Write the name alone into `_my_resources/active-project.txt` (overwrite).
2. **Active pointer** — else read `_my_resources/active-project.txt`; if it names a folder under `Projects/`, use it.
3. **Ask** — else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"* — never guess.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

**Binding rule (applies to EVERY step below):** every "THIS repo", every `{project-root}`, and every bare path resolves **under `PROJECT_ROOT`**.

## Step 1 — Elicit and Clarify (Interactive)
Load the target story (from `$ARGUMENTS` or the active story).
Assume the persona of **Murat (Test Architect)**. 
- You MUST talk to the user to understand the behaviors 100% clearly.
- Ask targeted, specific questions about edge cases, unstated assumptions, and exact expected outcomes.
- **STOP and wait for the user's answers.** Do NOT proceed to Step 2 until the user explicitly agrees that the behaviors are perfectly defined.

## Step 2 — Generate BDD Contracts
Once the user confirms the behaviors are locked in:
1. Write the strict `pytest-bdd` `.feature` file (Given/When/Then) into `backend/tests/features/`.
2. Write the step definition scaffolds into `backend/tests/bdd/`.

## Done
Report: The generated `.feature` files and step definitions. Ask the user if they are ready to proceed to the standard unit tests (`sudo-write-story-tests` Step 2) or implementation (`sudo-dev-story-tests`).

Optional additional input: $ARGUMENTS
