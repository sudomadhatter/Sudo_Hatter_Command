---
description: Develop a story test-first — plan, then STOP at the self-audit gate (human picks: run it here on a chosen model, hand the plan to a fresh team, or continue), implement, then auto-expand coverage. Step ② of the sudo dev flow.
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

## Step 0.7 — BDD contract gate (HARD — before any planning or code)
The BDD Vision Lock is a standing, enterprise-level phase of this flow: **a story may not be planned or
implemented without its locked behavior contract or a recorded waiver.** Check the story file's
frontmatter, then verify on disk (trust nothing — a flag with no file behind it fails the gate):
- **`bdd: locked`** AND every `bdd_contract:` path exists on disk (BDD-structured scenarios inside the
  story's ATDD red test files — the default — or the opt-in `.feature` files) → proceed; those contracts
  are part of the ① red set Step 3 must drive green. A `locked` record whose cited files are missing
  (deleted, renamed, never written) **fails the gate** — fix the frontmatter or re-lock, never wave it
  through (Epic 17.7 shipped a `locked` record backed by zero on-disk files).
- **`bdd: waived — <rationale>`** (explicit, human-approved, recorded) → proceed; note the waiver in the plan.
- **Neither** — including stories that predate this gate (no `bdd:` key at all) — → **STOP. Do not plan,
  do not write code.** Run the **`/sudo-bdd-tests`** Vision Lock now (it is interactive — the human must
  be in the loop) and only continue once the story carries a real contract or a recorded waiver. Never
  grandfather a story past this gate silently, and never author the "lock" yourself without the session.

## Step 1 — Plan
Invoke the **`bmad-dev-story`** skill in PLAN mode for the story in `$ARGUMENTS`. Produce its
`implementation_plan.md` **into `ARTIFACT_DIR`** — not the BMAD stories dir, not the `_artifacts/` root.

## Step 2 — Self-audit STOP gate (MANDATORY — stop the moment the plan is written)
The plan exists; **STOP before the audit and before any code.** This stop exists so the human can choose
the audit *lane and model* — e.g. a lighter model for an easy story, or a fresh team with clean context.
Post the clickable link to `implementation_plan.md` and ask ONE question:

> "Plan ready → self-audit next. **(a)** run `/sudo-self-audit` here — name a model if you want a
> different lane (e.g. 'use Fable' for an easy story); **(b)** you take `implementation_plan.md` to a
> fresh team/session for the audit — I'll wait; or just say **continue**."

Then **WAIT. Modify NO project file and write NO code until the human answers.**
- **(a) Run here** — invoke **`/sudo-self-audit`** against the plan (the pre-dev adversarial stress-test:
  gaps, over-engineering, contract breaks). If the human named a model, run the audit on it — spawn
  `/sudo-self-audit` as a subagent with that model override where the surface supports it; otherwise the
  human switches model and re-invokes. Fold findings back into the plan. (Human-lane equivalent of
  autopilot Stage 2.) **Persist the audit as its own `self-audit-stress-test.md`** (`type: self_audit`)
  **in `ARTIFACT_DIR`** (Step 0.5) — inline findings, or findings folded only into the plan, do NOT
  satisfy the protocol (`artifacts-always-first` §7).
- **(b) Fresh team** — do nothing and wait. When the human returns and says **continue**, read the
  external audit (expect `self-audit-stress-test.md` in `ARTIFACT_DIR`; if it lives elsewhere, ask), fold
  its findings into the plan, then proceed.
- **"continue" with no audit run and none provided** — confirm once ("skipping the self-audit for this
  story?"); on an explicit yes, write a stub `self-audit-stress-test.md` recording
  `Skipped by human decision (<date>)` so the Step 5 checklist stays honest, and proceed.

**"continue" always means: run the remainder of the flow (Step 2.5 → 3 → 4 → 5) without further stops** —
subject only to Step 2.5's real-questions rule.

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
① red tests — **including the BDD contract scenarios from the Vision Lock (Step 0.7)** — to green. Run the
relevant suite(s) and paste the **actual** output (constitution rule). If a test fails, find root cause
before fixing.

**Every ① red ends green or is quarantined — never shipped red (`tests-must-gate-for-real`).**
A red that can't go green is the tell ① handed you **fiction** — it asserts what the design never had
(copy absent from source, an auth-gated page assumed "public"). Fix it to the real contract or drop it
with a one-line note; never delete-to-force-green.

## Step 4 — Automate (expand coverage)
Invoke the **`bmad-testarch-automate`** skill to expand API / UI / contract coverage around what was
built — closing gaps the ATDD pass did not reach. **Leave evidence:** persist its summary as
`_bmad-output/test-artifacts/automation-summary-<story>.md`; if expansion is genuinely not applicable to
this story, write a `## Automate: skipped — <rationale>` section into the walkthrough instead. A silent
skip is an unfinished Step 4 — the Step 5 checklist (and the ③ gate's automate-evidence check) verify this.

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
- [ ] **Automate evidence (Step 4)** — `_bmad-output/test-artifacts/automation-summary-<story>.md` exists,
      OR the walkthrough carries an explicit `## Automate: skipped — <rationale>` section. (Lives with the
      TEA outputs, not in `ARTIFACT_DIR`.) A silent skip fails this checklist — the bug this item closes:
      the 2026-07-09 testing audit found 13 of 14 Epic-8 ATDD stories finished green with no expansion
      pass and nothing caught it.

Post a clickable Markdown link to every artifact in the chat that same turn — never a bare path.

## Done
Report: plan-vs-built deltas, audit findings applied, tests now green (paste output), coverage added, and
the three Step-5 artifact links. Hand to `sudo-code-review`. The dev step **may advance the story to
`review`** — bmad-dev-story's Step 9 does this and we let it (don't fight bmad's own logic). **Never flip to
`done`, and never `git commit`/`push`** — `done` is Daniel's call at close-out via
`/sudo-update-sprint-memory`, after his human-in-the-loop review.

Optional additional input: $ARGUMENTS
