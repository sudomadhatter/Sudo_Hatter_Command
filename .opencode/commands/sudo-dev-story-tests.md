---
description: Develop a story test-first — plan, auto self-audit the plan, implement, then auto-expand coverage. Step ② of the sudo dev flow.
platforms: [opencode, antigravity]
---

# /sudo-dev-story-tests — Plan → Self-Audit → Implement → Automate (②)

Thin orchestrator — drives the existing dev workflows so the story is built against the red tests from ①
and ends with expanded coverage. Project-scoped (targets THIS repo).

> Flow position: `sudo-write-story-tests` → **`sudo-dev-story-tests`** → `sudo-code-review`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Run from the **command center** (the lobby), this command operates on exactly ONE child project under
`Projects/`, never the lobby itself. Resolve the target now:
0. **Self** — if the current repo already has `_bmad/bmm/config.yaml` and **no** `Projects/` subfolder,
   you are inside a project already: `PROJECT_ROOT = .`. Skip to the binding rule.
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

## Step 1 — Plan
Invoke the **`bmad-dev-story`** skill in PLAN mode for the story in `$ARGUMENTS`. Produce its
`implementation_plan.md`.

## Step 2 — Self-audit the plan (automatic, the moment the plan is written)
Immediately invoke **`/sudo-self-audit`** against the just-written plan — the pre-dev adversarial
stress-test (gaps, over-engineering, contract breaks) BEFORE any code. Fold its findings back into the
plan. (Human-lane equivalent of autopilot Stage 2.) **Persist the audit as its own
`self-audit-stress-test.md`** (`type: self_audit`) in the story's artifact folder — inline findings, or
findings folded only into the plan, do NOT satisfy the protocol (`artifacts-always-first` §7).

## Step 3 — Implement
Invoke the **`bmad-dev-story`** skill in IMPLEMENT mode: apply the audit, write the code, and drive the
① red tests to green. Run the relevant suite(s) and paste the **actual** output (constitution rule). If a
test fails, find root cause before fixing.

## Step 4 — Automate (expand coverage)
Invoke the **`bmad-testarch-automate`** skill to expand API / UI / contract coverage around what was
built — closing gaps the ATDD pass did not reach.

## Step 5 — Close-out artifacts (MANDATORY — never skip, even on "just do it")
The Always-On **`artifacts-always-first`** rule governs this step; it is restated inline here so the
literal flow cannot miss it (the bug this hardening closes: the steps above produced a plan + a chat report
but no closing artifacts). Before reporting Done, the story's artifact folder
`PROJECT_ROOT/_artifacts/epic_<E>/<story>/` MUST hold all three files, each carrying the
`IsArtifact: true` + `ArtifactMetadata` frontmatter (with the right `type:`):

- [ ] **`implementation_plan.md`** (`type: implementation_plan`) — from Step 1, frontmatter present (§2).
- [ ] **`self-audit-stress-test.md`** (`type: self_audit`) — the persisted Step 2 audit, a standalone file,
      NOT inline-only and NOT merely folded into the plan (§7).
- [ ] **`walkthrough.md`** (`type: walkthrough`) — the ONE closing doc (§5): narrative (what changed
      file-by-file & why), the red→green test story, the **actual pasted test output**, an AC→evidence
      matrix, then a **`## Task Checklist`** section (final TodoWrite snapshot) and a **`## Your Actions`**
      section (Daniel's manual steps + the exact git commit command). **Required even when Daniel said
      "skip the plan, just do it" — the walkthrough is never skippable.**

Post a clickable Markdown link to every artifact in the chat that same turn — never a bare path.

## Done
Report: plan-vs-built deltas, audit findings applied, tests now green (paste output), coverage added, and
the three Step-5 artifact links. Hand to `sudo-code-review`. The dev step **may advance the story to
`review`** — bmad-dev-story's Step 9 does this and we let it (don't fight bmad's own logic). **Never flip to
`done`, and never `git commit`/`push`** — `done` is Daniel's call at close-out via
`/sudo-update-sprint-memory`, after his human-in-the-loop review.

Optional additional input: $ARGUMENTS
