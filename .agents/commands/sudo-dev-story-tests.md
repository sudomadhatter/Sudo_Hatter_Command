---
description: Develop a story test-first — plan, then STOP at the self-audit gate (`continue` = audit here; `changed` = human switched the model, audit then stop to switch back; a pasted file path = another team's blind audit), implement, then auto-expand coverage. Step ② of the sudo dev flow.
platforms: [opencode, antigravity]
---

# /sudo-dev-story-tests — Plan → Self-Audit → Implement → Automate (②)

Thin orchestrator — builds the story against ①'s red tests and ends with expanded coverage. Project-scoped
(targets THIS repo).

> Flow position: `sudo-write-story-tests` → **`sudo-dev-story-tests`** → `sudo-code-review`.

## Step 0 — Resolve the target project (FIRST — before any other step)
Bind the target per `.agents/rules/sudo-target-resolution.md` §STD + §BIND: self fast-path → `$ARGUMENTS`
override (remainder = the real argument: story id, focus…) → `.agents/active-project.txt` → else **STOP
and ask** — never guess, never operate on the lobby. Set `PROJECT_ROOT` and **echo exactly**
`Target: Projects/<name>` before any work. Every bare path below resolves under `PROJECT_ROOT` (nested
`bmad-*`/`1_*` skills bind their `{project-root}` to it); a needed path missing under `PROJECT_ROOT` →
STOP and say so, never fall back to the lobby.

## Step 0.5 — Resolve & create the artifact folder (BEFORE any sub-skill writes a file)
Per `artifacts-always-first` §2, everything this flow produces lands in ONE story-scoped folder — set it
now: numeric `E.S` → `ARTIFACT_DIR = PROJECT_ROOT/_artifacts/epic_<E>/story-<E>-<S>-<short-title>/`
(create `epic_<E>/` if missing; reuse the existing folder on a resume) · TEA / non-numeric id →
`PROJECT_ROOT/_artifacts/tea/<story-slug>/` · no story id → `PROJECT_ROOT/_artifacts/_main/<YYYY-MM-DD>_<slug>/`
(the holding bucket; never a dated folder at the `_artifacts/` root). **Echo** `Artifacts: <ARTIFACT_DIR>`
before Step 1; pass it explicitly to each sub-skill and **never** let one mint its own root-level or
date-stamped folder.

## Step 0.6 — Re-enter the story worktree if one already exists (fresh-chat resume)
Before any planning or edit: `git worktree list` under `PROJECT_ROOT` (`worktree-per-story` → "Resuming").
A `claude/<story-slug>` tree exists → **cd into it and re-bind everything below under it** — story file,
① red tests, `ARTIFACT_DIR`, test commands (they commonly live ONLY in that tree; skipping this plans
blind or opens a duplicate). None → first work session; `bmad-dev-story` opens one at first edit. Echo the
case (`Worktree: reused <path>` / `none yet — opens at first edit`).

## Step 0.7 — BDD contract gate (HARD — before any planning or code)
The BDD Vision Lock is a standing phase of this flow: **a story may not be planned or implemented without
its locked behavior contract or a recorded waiver.** Check the story frontmatter, then verify on disk (a
flag with no file behind it fails the gate):
- **`bdd: locked`** AND every `bdd_contract:` path exists on disk (BDD scenarios inside the story's ATDD red
  files — the default — or opt-in `.feature` files) → proceed; those contracts are part of the ① red set
  Step 3 drives green. A `locked` record whose cited files are missing **fails the gate** — fix the
  frontmatter or re-lock, never wave it through (Epic 17.7 shipped a `locked` record backed by zero files).
- **`bdd: waived — <rationale>`** (explicit, human-approved) → proceed; note the waiver in the plan.
- **Neither** (incl. stories predating this gate, no `bdd:` key) → **STOP. Do not plan or code.** Run
  **`/sudo-bdd-tests`** now (interactive — human in the loop); continue only once the story carries a real
  contract or waiver. Never grandfather silently, never author the "lock" yourself.

## Step 1 — Plan
Invoke **`bmad-dev-story`** in PLAN mode for the story in `$ARGUMENTS`. Produce its `implementation_plan.md`
**into `ARTIFACT_DIR`** — not the BMAD stories dir, not the `_artifacts/` root.

## Step 2 — Self-audit STOP gate (MANDATORY — stop the moment the plan is written)
The plan exists; **STOP before the audit and before any code.** This stop lets the human switch the model
for the audit, or hand it to another team (a different LLM, blind).
**You can NEVER switch the model yourself — never offer to.** Only the human can (e.g. `/model`).

Post the gate message — short, ALWAYS with the clickable plan link (never a bare path):

> "Plan ready → **[implementation_plan.md](<ARTIFACT_DIR>/implementation_plan.md)**
> **1.** `continue` — audit runs here · or switch your model first, then say `changed`
> **2.** handoff to another team — paste the audit file's path here when it's done."

Then **WAIT — modify NO project file, write NO code.** The reply IS the trigger:

- **`continue`** — no model change. Run **`/sudo-self-audit`** on the plan here (pre-dev adversarial
  stress-test). **Persist as `self-audit-stress-test.md`** (`type: self_audit`) **in `ARTIFACT_DIR`** —
  inline-only findings do NOT satisfy the protocol (`artifacts-always-first` §7). Fold findings into the
  plan, then go straight on (Step 2.5 → 3 → 4 → 5) — **no second gate**.
- **`changed`** — the human ALREADY switched the model; the audit lane. Run **`/sudo-self-audit`** now (on
  the switched model), persist + fold as above — then **STOP AGAIN**: *"Audit done — switch back, then say
  `continue`."* WAIT before Step 2.5/3 — **never implement on the audit-switched model.** This switch-back
  gate exists ONLY after `changed`.
- **A pasted file path** — another team ran the audit blind; the path IS the handoff. Read it; if outside
  `ARTIFACT_DIR`, copy it in as `self-audit-stress-test.md` (`type: self_audit`, source noted in
  frontmatter). Fold its findings into the plan, then proceed — no further stops.
- **Explicit "skip the audit"** — confirm once; on yes, write a stub `self-audit-stress-test.md` recording
  `Skipped by human decision (<date>)` so the Step 5 checklist stays honest, and proceed.

**`continue` always means: run the remainder (Step 2.5 → 3 → 4 → 5) without further stops** — subject only
to Step 2.5's real-questions rule and the `changed`-path switch-back stop above.

## Step 2.5 — Gate: ask first, but ONLY if you have questions
A **conditional** gate — not a mandatory approval stop. After the plan + audit, decide honestly whether you
have real questions: a genuine ambiguity, a decision only the human can make, contradictory ACs, or a plan
concern the audit raised that you can't safely resolve yourself.
- **Have questions → STOP before any code.** Ask concisely in chat (web/mobile: the tap-to-approve chip) and
  wait. Modify NO project file until resolved. This gate OVERRIDES bmad-dev-story's no-pause directive — but
  only here, and only because you have questions.
- **No questions → go straight to Step 3.** Don't manufacture one; an unambiguous plan just gets built.

## Step 3 — Implement
Invoke **`bmad-dev-story`** in IMPLEMENT mode: apply the audit, write the code, and drive the ① red tests —
**including the BDD contract scenarios from the Vision Lock (Step 0.7)** — to green. Run scoped suites while
you iterate (the story's files + touched modules), then **finish with ONE full-suite run per touched stack**
(backend: `backend/.venv` pytest with the project's canonical runner flags — the runner AIDEV-NOTE in
`backend/requirements.txt` is the one source of truth) and paste the **actual** totals **plus
`git rev-parse HEAD`** into the walkthrough (constitution rule). That (totals, SHA) pair is ③'s entry
baseline — ③ re-runs the full suite up front ONLY when the SHA or the shape doesn't hold, so the pair never
pays for the full suite twice. If a test fails, find root cause before fixing.

**Every ① red ends green or is quarantined — never shipped red (`tests-must-gate-for-real`).** A red that
can't go green is the tell ① handed you **fiction** — it asserts what the design never had (copy absent from
source, an auth-gated page assumed "public"). Fix it to the real contract or drop it with a one-line note;
never delete-to-force-green.

## Step 4 — Automate (expand coverage)
Invoke **`bmad-testarch-automate`** to expand API / UI / contract coverage around what was built — closing
gaps the ATDD pass missed. **Leave evidence:** persist its summary as
`_bmad-output/test-artifacts/automation-summary-<story>.md`; if expansion is genuinely N/A, write a
`## Automate: skipped — <rationale>` section into the walkthrough instead. A silent skip is an unfinished
Step 4 — the Step 5 checklist and the ③ gate verify this.

## Step 5 — Close-out artifacts (MANDATORY — never skip, even on "just do it")
The Always-On **`artifacts-always-first`** rule governs this step. Before reporting Done, `ARTIFACT_DIR`
MUST hold all three files, each carrying the `IsArtifact: true` + `ArtifactMetadata` frontmatter
(correct `type:`):

- [ ] **`implementation_plan.md`** (`type: implementation_plan`) — from Step 1, frontmatter present (§2).
- [ ] **`self-audit-stress-test.md`** (`type: self_audit`) — the persisted Step 2 audit, a standalone file,
      NOT inline-only and NOT merely folded into the plan (§7).
- [ ] **`walkthrough.md`** (`type: walkthrough`) — the ONE closing doc (§5): narrative (what changed
      file-by-file & why), the red→green test story, the **actual pasted test output**, an AC→evidence
      matrix, then a **`## Task Checklist`** section (final TodoWrite snapshot) and a **`## Your Actions`**
      section (what landed — worktree branch + commits — plus anything still on the human). **Required even
      when told to "skip the plan, just do it" — the walkthrough is never skippable.**
- [ ] **Automate evidence (Step 4)** — `_bmad-output/test-artifacts/automation-summary-<story>.md` exists,
      OR the walkthrough carries an explicit `## Automate: skipped — <rationale>` section. (Lives with the
      TEA outputs, not `ARTIFACT_DIR`.) A silent skip fails this checklist.

Post a clickable Markdown link to every artifact in the chat that same turn — never a bare path.

## Done
Report: plan-vs-built deltas, audit findings applied, tests now green (paste output), coverage added, and
the three Step-5 artifact links. Hand to `sudo-code-review`. The dev step **may advance the story to
`review`** — bmad-dev-story's Step 9 does this and we let it. **Never flip to `done`** — Daniel's call at
close-out via `/sudo-update-sprint-memory`. **Git:** commit freely inside the story worktree (explicit paths,
never `git add -A`); do NOT land it on `main_debug` — Step 7 of `/sudo-update-sprint-memory` owns that push
(→ `worktree-per-story`).

Optional additional input: $ARGUMENTS
