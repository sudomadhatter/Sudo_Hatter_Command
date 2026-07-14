---
description: Fast-track dev flow — write the story, develop the fix directly, run a light post-dev sanity audit, and stop for review. Bypasses strict ATDD tests, planning gates, and code reviews.
platforms: [opencode, antigravity, claude, codex]
---

# /sudo-quick-dev — Fast-Track Development & Sanity Audit

Thin orchestrator to implement and log a quick fix. It bypasses red-phase test writing (`sudo-write-story-tests`), planning approval gates, and adversarial code reviews (`sudo-code-review`), running a direct implementation loop.

> Flow position: `bmad-create-story` → `bmad-dev-story` (Direct, Continuous) → `sudo-self-audit` (Light post-dev check) → [Stop for human review and close-out].

## Step 0 — Resolve the target project (FIRST — before any other step)
Run from the **command center** (the lobby), this command operates on exactly ONE child project under
`Projects/`, never the lobby itself. Resolve the target now:
0. **Self (sub-project fast path)** — if this repo has **no** `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip straight to the binding rule.
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is the target; consume that first token. Write the name alone into `.agents/active-project.txt` (overwrite).
2. **Active pointer** — else read `.agents/active-project.txt`; if it names a folder under `Projects/`, use it.
3. **Ask** — else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"* — never guess.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

**Binding rule:** every path and child tool call resolves under `PROJECT_ROOT`.

## Step 1 — Create the story
Invoke the **`bmad-create-story`** skill for the story in `$ARGUMENTS` (e.g., a story ID like `12.3`, or a new descriptive name). This creates the story file in `_bmad/bmm/stories/` with its ACs.

## Step 2 — Direct Implementation (Continuous)
Invoke the **`bmad-dev-story`** skill on the created story. 
* **Bypass Planning Gate:** During this step, the developer agent is explicitly permitted to bypass any "wait for approval" planning gates (such as the standard planning_mode halt after writing the implementation plan). It should plan, implement the fix, and write the walkthrough in one continuous execution.
* **Skip ATDD:** The developer agent skips the strict ATDD test-first cycle (writing separate red-phase acceptance tests beforehand) and implements the minimal code directly to satisfy the story.

## Step 3 — Sanity Audit (Post-Dev Conformance Check)
Invoke the **`/sudo-self-audit`** workflow. 
* **Note:** Even though self-audit is structurally a pre-dev tool, we run it here in **Light** mode to check that the implemented changes strictly trace back to the story's ACs and that no over-engineering or unwanted dependencies crept into the fix. Use the walkthrough.md and implementation plan generated in Step 2 as the targets of the audit.

## Done
Stop here. Do **NOT** run `/sudo-update-sprint-memory`. Display the story path, the key changes implemented, and invite the human (Daniel) to review the work and run `/sudo-update-sprint-memory` himself when satisfied.
