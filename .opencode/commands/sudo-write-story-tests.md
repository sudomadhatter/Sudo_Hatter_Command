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
   the name alone into `.agents/active-project.txt` (overwrite) so later commands inherit it.
2. **Active pointer** — else read `.agents/active-project.txt`; if it names a folder under
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

## Step 2 — BDD Vision Lock (ATDD Contract Phase — MANDATORY, never silently skipped)
Invoke the **`/sudo-bdd-tests`** workflow. This is an interactive session with the Test Architect (Murat)
to hash out exact expected behaviors until they are 100% understood. The locked Given/When/Then contract
is codified **into the story's ATDD red test file(s)** (BDD-structured pytest scenarios for backend;
BDD-structured vitest/Playwright `describe`/`it` for frontend) — Step 3 extends those same files. A
standalone `pytest-bdd` `.feature` + step-defs pair is **opt-in only** (the human explicitly chooses it
during the lock, when Gherkin itself buys value); never default to it.

This phase is a standing part of the enterprise flow — **the ONLY exit without a contract is a recorded
waiver**: the story has no product-behavior surface (docs-only, characterization-only), the human confirms
the waiver in chat, and the story frontmatter records `bdd: waived — <rationale>`. Either way the story
leaves ① carrying `bdd: locked` (+ contract paths) or `bdd: waived` in its frontmatter —
`/sudo-dev-story-tests` (②) **hard-gates on that record** and will refuse to dev a story without it.

## Step 3 — Write the failing acceptance tests (ATDD red phase)
Invoke the **`bmad-testarch-atdd`** skill against the story just created. Generate any remaining unit/component acceptance tests that codify each AC and **must fail now** (no implementation exists yet) —
**extending the Step 2 contract file(s), not minting sibling test files** (one red file per story per
stack; the Vision Lock scenarios and the ATDD reds live together). If the epic has a
`bmad-testarch-test-design` risk plan, pull it so P0 ACs get priority coverage.

**Ground every red before it counts (per `tests-must-gate-for-real`).** A red must fail because the
feature is *unbuilt*, never because it invented something. Before leaving this step, verify against the
ACTUAL code (grep the producing surface; read the page/handler/endpoint) that every asserted string,
selector, endpoint, and **precondition** is real or is the honest absence of a real thing — and that the
test's assumed auth / precondition model matches reality (e.g. don't assert an auth-gated page as
"public"). A test asserting copy that does not exist in source, or misreading the auth model, is
**fiction, not a red** — it fails identically whether the feature is unbuilt or the assertion is bogus,
so it can never go green. Fix or drop it here; do not hand fiction to ②.

## Done
Report: story id + path, ACs covered, the red tests written (paths) and confirmation they fail as
expected. Leave them staged — `sudo-dev-story-tests` turns them green next. **Do NOT start implementing.**

Optional additional input: $ARGUMENTS
