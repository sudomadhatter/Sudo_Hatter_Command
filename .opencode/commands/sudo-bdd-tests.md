---
description: BDD Vision Lock — interactive session to hash out exact expected behaviors until 100% understood, then codify them as BDD-structured contracts INSIDE the story's ATDD red test files (standalone pytest-bdd .feature is opt-in only) — or record an explicit human-approved waiver. Mandatory phase of the sudo dev flow; ② hard-gates on its output.
platforms: [opencode, antigravity, codex]
---

# /sudo-bdd-tests — BDD Vision Lock (Step 1a)

Thin orchestrator — initiates an interactive session to finalize the exact behaviors of a story before translating them into strict `pytest-bdd` contracts. This ensures 100% clarity and zero AI drift. Project-scoped (targets THIS repo).

> Flow position: `sudo-boot-sprint-memory` → **`sudo-bdd-tests`** (often via `sudo-write-story-tests`) → `sudo-dev-story-tests`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Run from the **command center** (the lobby), this command operates on exactly ONE child project under `Projects/`, never the lobby itself. Resolve the target now:
0. **Self (sub-project fast path — check this FIRST, and STOP here if it matches)** — if this repo has **no** `Projects/` subfolder, you ARE the project: set `PROJECT_ROOT = .` and skip straight to the binding rule.
1. **Inline override** — if `$ARGUMENTS` begins with a name matching a folder under `Projects/`, that is the target; consume that first token. Write the name alone into `.agents/active-project.txt` (overwrite).
2. **Active pointer** — else read `.agents/active-project.txt`; if it names a folder under `Projects/`, use it.
3. **Ask** — else STOP and ask Daniel *"Which project are we working in? (e.g. AGY_AVIATIONCHAT)"* — never guess.

Set `PROJECT_ROOT = Projects/<name>` and **echo exactly** `Target: Projects/<name>` before any work.

**Binding rule (applies to EVERY step below):** every "THIS repo", every `{project-root}`, and every bare path resolves **under `PROJECT_ROOT`**.

## Step 1 — Elicit and Clarify (Interactive)
Load the target story (from `$ARGUMENTS` or the active story).
Assume the persona of **Murat (Test Architect)**. 
- **Waiver check first:** if the story has NO product-behavior surface to lock (docs-only, pure
  characterization/test-debt, config-only), say so and propose a **waiver**. A waiver is only real once
  the human confirms it in chat AND it is recorded in the story frontmatter (Step 2b). Never waive
  silently, and never waive because the behaviors merely seem "obvious" — obvious is exactly what drifts.
- Otherwise: you MUST talk to the user to understand the behaviors 100% clearly.
- Ask targeted, specific questions about edge cases, unstated assumptions, and exact expected outcomes.
- **STOP and wait for the user's answers.** Do NOT proceed to Step 2 until the user explicitly agrees that the behaviors are perfectly defined.

## Step 2 — Codify the contract (default: INTO the story's ATDD red tests)
Once the user confirms the behaviors are locked in, codify the Given/When/Then contract **into the story's
existing ATDD red test file(s)** — the Vision Lock's value is the decision-forcing *conversation*; the
artifact rides the red tests ① writes anyway. (Epic 17 audit, 2026-07-13: the genuine catches came from
the lock session, self-audit, and recon — the parallel pytest-bdd layer mostly re-confirmed already-correct
behavior while adding its own harness-bug class, e.g. the sync-step `asyncio.run` false-reds.)
- **Backend behaviors (default):** BDD-structured pytest — one test (or test class) per scenario, named
  for it, with the locked `Given/When/Then` verbatim in the docstring — written into the story's ATDD red
  test file under `backend/tests/`, red until ② implements. No separate `.feature`/steps pair.
- **Frontend behaviors (unchanged):** the SAME contract as BDD-structured `describe("Given …")` /
  `it("When … Then …")` cases in the story's vitest (or `frontend/e2e/` Playwright) red test file.
- **Standalone `pytest-bdd` (OPT-IN — the exception, never the default):** a `.feature` file in
  `backend/tests/features/` + self-binding steps in `backend/tests/bdd/` ONLY when Gherkin itself buys
  something (a stakeholder-readable spec, heavy data-table scenarios, a cross-team contract) AND the human
  explicitly opts in during the lock session. It duplicates ATDD and carries its own harness bugs
  (sync steps driving async fns, step-binding drift) — so it must be chosen, never assumed.
- **Mixed stories:** each behavior lands in its own stack; the story frontmatter lists every contract path.

## Step 2b — Record the lock (or waiver) in the story file
Update the story file's YAML frontmatter so downstream steps can gate on it (`/sudo-dev-story-tests` ②
refuses to dev a story without one of these):
- Locked: `bdd: locked` + `bdd_contract: <path(s) to the contract test file(s)>` — the ATDD red file(s)
  carrying the scenarios (or the opt-in `.feature` files). **These paths are load-bearing:** ② verifies
  each exists on disk, and any later rename/delete MUST update this frontmatter — a `locked` record
  pointing at missing files fails the gate (the Epic 17.7 phantom-contract lesson: `bdd: locked` with all
  three cited files deleted from disk).
- Waived: `bdd: waived — <rationale> (human sign-off, <date>)`
The frontmatter is the source of truth; a waiver that lives only in chat or an epic-notes comment does not count.
Also record the lock's *decisions* (the resolved Qs/forks) as a dated comment block in the story file —
Epic 17 proved that decision record is where the step earns its keep.

## Done
Report: the generated contract files (or the recorded waiver) and the frontmatter record. Ask the user if they are ready to proceed to the standard unit tests (`sudo-write-story-tests` Step 3) or implementation (`sudo-dev-story-tests`).

Optional additional input: $ARGUMENTS
