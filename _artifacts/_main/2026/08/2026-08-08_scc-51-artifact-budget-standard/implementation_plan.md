---
IsArtifact: true
ArtifactMetadata:
  title: SCC-51 — replace the artifact byte caps with a substance standard
  type: implementation_plan
  date: 2026-08-08
---

# SCC-51 — replace the artifact byte caps with a substance standard

**Ticket:** SCC-51 (epic SCC-33) · **Branch:** `chore/SCC-51-artifact-budget-standard` off `main` @ `182bee5`
**Status:** edits drafted in an isolated worktree, suite green, **nothing committed or pushed.**

## The operator ruling

> *"There can not be hard limits. We can explain the necessity of compressed and only valid information
> without fluff, but this makes no sense and I see it as a huge threat to quality."* — 2026-08-08
>
> *"Make sure you don't take out all the stuff. Some stuff needs limits."*

Both halves are honoured below: the caps that destroy substance go, the limits that relocate misplaced
content stay.

## The principle that separates a good limit from a bad one

This is the whole decision, and it is mechanical rather than a matter of taste:

> **A limit is legitimate when exceeding it means "the wrong content is in this file" — the fix is to
> MOVE or DELETE content that belongs somewhere else, and nothing is lost.**
>
> **A limit is harmful when exceeding it means "you found more than expected" — there is nowhere for the
> content to go, so the only available lever is destroying substance.**

Applied to this codebase, the same author could rationally have set both kinds. That is why they got
conflated, and why the distinction has to be written down rather than remembered.

## REMOVE — the caps that can only be met by truncation

| Cap | Where | Why it is harmful |
|---|---|---|
| `implementation_plan.md` ≤ 8 KB | `artifacts-always-first.md:39` | Over budget = **findings, ACs, decisions**. The rule *forbids* splitting into a second file, so there is nowhere to move them. Only truncation is left. |
| `walkthrough.md` ≤ 10 KB | same | Over budget = the AC→evidence matrix, suite totals, the review's findings table and Verdict line. Same trap. |
| `check_artifact_budgets()` + `_BUDGETS` | `workflow_lint.py:142-181` (+ call at :388) | The machine half. A WARN that can only be silenced by deleting substance. |

**Three pieces of evidence, not opinion:**

1. **The plan is a TWO-author document, and the cap never accounted for it.** `git log -S` proves the cap
   and the audit-into-plan rule shipped in the **same commit** — 2026-08-03,
   *"two-doc story close — audit appends to plan, review appends to walkthrough."* From that moment
   `implementation_plan.md` had to hold the plan **and** `/sudo-self-audit`'s findings table, per-phase
   evidence and verdict (§7), under a cap written "incl. its audit section" that was never validated
   against a real audit. A fixed cap on a two-author doc squeezes the **second** author — the auditor,
   the one voice you least want truncated.

2. **It broke on first contact.** The SCC-40 Full self-audit produced 8 findings, blew the cap
   immediately, and took six trim passes. Finding F6's text was compressed to fit. That is the gate
   cutting substance while the filler it was aimed at survives untouched.

3. **Prose and enforcement already disagreed.** The rule said "Budgets (**HARD**)" with no scope;
   `workflow_lint.py:164` silently exempted `_main/`, `_archived/` and `debugging/`. A rule enforced
   outside its stated scope is how it earned its reputation — and it is why I misapplied it to two
   `_main/` initiative plans this session despite a memory telling me not to.

## KEEP — limits that relocate content instead of destroying it

**These are deliberately untouched. Removing them would be the over-correction.**

| Limit | Where | Why it stays |
|---|---|---|
| `active-context.md` ≤ 20 KB (~5k tokens) | `closeout_preflight.py:278` | It is loaded into **every session at boot** — the one file whose size is a standing tax on all future work. Over budget means **stale state that should be deleted**; git keeps the history. Content leaves the file, nothing is lost. Textbook legitimate. |
| Board note budget | `workflow_lint.check_board_note_budget` | Over budget means narrative that belongs in `_bmad-output/history/CHANGELOG.md`. The limit **routes** prose to the right file — it does not delete it. |
| Board size cap | same check | Keeps `sprint-status.yaml` bare state. Same relocation logic. |
| Autopilot `-MaxCost` / `-MaxStageCost` | the engines | Money, not quality. A runaway-spend backstop. |
| `bmad-quick-dev` spec 900–1600 tokens | the skill | Already explicitly soft: *"Neither limit is a gate. Both are proposals with user override."* Nothing to fix. |
| "Never split into a second file" | `artifacts-always-first.md` | **A structure rule, not a size rule.** Load-bearing — it is what stops `code-review.md` / `your-action-required.md` / `task-list.md` proliferating. Kept verbatim. |

## The replacement standard

Written into `artifacts-always-first.md` where the cap was:

> **Dense, not short — and there is NO byte cap.** Both docs are re-read on every pass of the loop: the
> dev writes the plan, `/sudo-self-audit` appends into it (§7), the reviewer reads it, close-out reads it
> before flipping status. Every line is paid for repeatedly, so every line must earn it — a decision, a
> constraint, a finding, or evidence. Cut restatement of the codebase, narrative filler, and context
> already stated elsewhere. Test evidence is totals lines + SHA, never reporter dumps; a re-run REPLACES
> the pasted totals — only `## Suite Ledger` accretes. Feels bloated → compress in place, **never a new file.**
>
> ⛔ **Length is NEVER a reason to omit a finding, an AC, or a piece of evidence.** A plan that grew
> because the audit found eight real things is working correctly. Truncating substance to hit a number is
> the failure this rule exists to prevent — not the outcome it wants.

The *why* survives — the docs are re-read on a hot loop, so density genuinely matters. Only the number,
which turned that reasoning into a weapon against findings, is gone.

## The 9 sites (lobby only — AGY's tomls carry no cap)

| # | File | Change | Done |
|---|---|---|---|
| 1 | `.agents/rules/artifacts-always-first.md:39` | standard replaces "Budgets (HARD)", + a dated note recording why | ✅ |
| 2 | `.agents/rules/artifacts-always-first.md:169` | long-plan exception restated as judgement, not "≳ 8 KB" | ✅ |
| 3 | `.agents/commands/sudo-dev-story-tests_AP.md` | drop `≤ 10 KB` | ✅ |
| 4 | `.agents/commands/sudo-update-sprint-memory.md:177` | drop `≤ 10 KB` | ✅ |
| 5 | `_bmad/custom/bmad-dev-story.toml` `persistent_facts` | drop cap — **injected into every dev run** | ✅ |
| 6 | `_bmad/custom/bmad-dev-story.toml` `on_complete` | drop cap | ✅ |
| 7 | `_bmad/custom/bmad-quick-dev.toml` `persistent_facts` | drop cap | ✅ |
| 8 | `.agents/scripts/workflow_lint.py` | delete `_BUDGETS` + `check_artifact_budgets()` + call site; leave a comment saying **do not re-add a byte threshold** and why | ✅ |
| 9 | `.agents/scripts/tests/test_workflow_lint.py` | F7 byte tests → **two guard tests** that fail if a byte threshold returns or the rule loses the standard | ✅ |

Site 9 is the part that makes this stick: the removal is now defended by tests, so a future agent
"restoring the budget" trips the suite instead of quietly re-breaking audits.

**+4 sites the first pass missed** — found by a `git grep` sweep that was wider than the plan's list:

| # | File | Change | Done |
|---|---|---|---|
| 10 | `.opencode/commands/sudo-update-sprint-memory.md:208` | the **generated mirror** kept `≤ 10 KB` after the source dropped it — sync copies `.agents/commands/` into `.claude/` + `.opencode/`, so editing only the source leaves the opencode lane reading the old cap | ✅ |
| 11 | `_artifacts/_memory/artifact-budgets-are-scoped-not-universal.md` | → `git mv` to `limits-relocate-content-never-truncate.md`, rewritten as the ruling + the legitimate/harmful test | ✅ |
| 12 | `_artifacts/_memory/story-artifacts-two-doc-close.md:17` | `Budgets are HARD: plan ≤ 8 KB, walkthrough ≤ 10 KB` → no byte cap | ✅ |
| 13 | `_artifacts/_memory/MEMORY.md:128` + `portable-memory-store-dot-slug-trap.md:43` | index line + backlink repointed to the new slug | ✅ |

Sites 11–13 are the ones that actually mattered. **Memory is recalled into context before any rule file
is read** — `MEMORY.md:128` is why the cap got applied in this very session. Fixing the rules while
leaving the memory saying "8/10 KB binds in-flight STORY docs" reinstalls the cap on the next session,
from a source the operator can't see.

## Verification (already run on the draft)

```
python3 .agents/scripts/tests/run_all.py     → 6/6 files passed
  [PASS] SCC-51 no byte-budget check exists on the linter
  [PASS] SCC-51 the rule states the standard that replaced the cap
```
Still to run before landing: `check_maps.py`, and a grep proving no byte cap survives anywhere.

## Landing

Usage-surface change (rules + commands + scripts), so the SOP quick-reference moves in the same commit or
the armed `sop-currency` gate rejects it. That page is the one file that collides with SCC-49 — resolved
by merging `origin/main` before pushing.

## Out of scope

The `active-context` 20 KB budget and the board budgets (see KEEP). SCC-41's rewrite follows once this
lands — that is the ticket this rule was actively damaging.
