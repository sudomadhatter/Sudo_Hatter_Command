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

## Step 0.5 — Resolve & create the artifact folder (BEFORE any sub-skill writes a file)
Every artifact this flow produces (plan, self-audit, walkthrough, code-review) lands in ONE story-scoped
folder — set it **now** so `bmad-dev-story` and the audit don't drop files at the `_artifacts/` root. Per
`artifacts-always-first`:
- **Numeric story `E.S`** → derive the epic from the leading number (e.g. `11.18` → `11`);
  `ARTIFACT_DIR = PROJECT_ROOT/_artifacts/epic_<E>/<story-slug>/` — **create `epic_<E>/` if missing**, then
  the story folder inside it (slug `story-<E>-<S>-<short-title>`), or reuse the existing one on a resume.
- **TEA / non-numeric id** (e.g. `tea-17`) has no numeric epic → nest under the `tea/` bucket:
  `PROJECT_ROOT/_artifacts/tea/<story-slug>/`.
- **No story id at all** (a true one-off) → `PROJECT_ROOT/_artifacts/<YYYY-MM-DD>_<slug>/` at the root.

**Echo** `Artifacts: <ARTIFACT_DIR>` before Step 1. Every step below writes into `ARTIFACT_DIR`; pass it
explicitly to each sub-skill and **never** let one mint its own root-level or date-stamped folder.

## Step 1 — Plan
Invoke the **`bmad-dev-story`** skill in PLAN mode for the story in `$ARGUMENTS`. Produce its
`implementation_plan.md` **into `ARTIFACT_DIR`** — not the BMAD stories dir, not the `_artifacts/` root.

## Step 2 — Self-audit the plan (automatic, the moment the plan is written)
Immediately invoke **`/sudo-self-audit`** against the just-written plan — the pre-dev adversarial
stress-test (gaps, over-engineering, contract breaks) BEFORE any code. Fold its findings back into the
plan. (Human-lane equivalent of autopilot Stage 2.) **Persist the audit as its own
`self-audit-stress-test.md`** (`type: self_audit`) **in `ARTIFACT_DIR`** (Step 0.5) — inline findings, or
findings folded only into the plan, do NOT satisfy the protocol (`artifacts-always-first` §7).

## Step 2.5 — Gate: ask first, but ONLY if you have questions
A **conditional** gate — not a mandatory approval stop. After the plan + audit, decide honestly whether you
have real questions for the human: a genuine ambiguity, a decision only they can make, contradictory ACs, or
a plan concern the audit raised that you can't safely resolve yourself.
- **Have questions → STOP before any code.** Ask them concisely in chat (on web/mobile, the tap-to-approve
  chip) and wait for answers. Modify NO project file and do NOT start dev until they're resolved. This gate
  OVERRIDES bmad-dev-story's no-pause directive — but only here, and only because you have questions.
- **No questions → go straight to Step 3.** Don't manufacture one; an unambiguous plan just gets built.

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
but no closing artifacts). Before reporting Done, `ARTIFACT_DIR` (the Step 0.5 folder — a numeric story's
`PROJECT_ROOT/_artifacts/epic_<E>/<story>/`) MUST hold all three files, each carrying the
`IsArtifact: true` + `ArtifactMetadata` frontmatter (with the right `type:`):

- [ ] **`implementation_plan.md`** (`type: implementation_plan`) — from Step 1, frontmatter present (§2).
- [ ] **`self-audit-stress-test.md`** (`type: self_audit`) — the persisted Step 2 audit, a standalone file,
      NOT inline-only and NOT merely folded into the plan (§7).
- [ ] **`walkthrough.md`** (`type: walkthrough`) — the ONE closing doc (§5): narrative (what changed
      file-by-file & why), the red→green test story, the **actual pasted test output**, an AC→evidence
      matrix, then a **`## Task Checklist`** section (final TodoWrite snapshot) and a **`## Your Actions`**
      section (the human's manual steps + the exact git commit command). **Required even when told to
      "skip the plan, just do it" — the walkthrough is never skippable.**

Post a clickable Markdown link to every artifact in the chat that same turn — never a bare path.

## Done
Report: plan-vs-built deltas, audit findings applied, tests now green (paste output), coverage added, and
the three Step-5 artifact links. Hand to `sudo-code-review`. The dev step **may advance the story to
`review`** — bmad-dev-story's Step 9 does this and we let it (don't fight bmad's own logic). **Never flip to
`done`, and never `git commit`/`push`** — `done` is Daniel's call at close-out via
`/sudo-update-sprint-memory`, after his human-in-the-loop review.

Optional additional input: $ARGUMENTS
