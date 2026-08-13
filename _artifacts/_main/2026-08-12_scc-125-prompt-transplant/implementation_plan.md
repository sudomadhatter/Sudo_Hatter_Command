# SCC-125 — Prompt transplant: FP gates on hunter lenses, adapted rubrics for auditors

**Ticket:** SCC-125 (Subtask of SCC-116) · **Lane:** `chore/SCC-125-prompt-transplant` off `main` @ `8c927dd`
**Spec:** `_artifacts/_main/2026-08-12_scc-116-house-review-engine/implementation_plan.md` §SCC-125
**Source text:** `_my_resources/open_tasks/pr-af-dev-system-upgrade.md` Appendix B (B.1–B.4)

## What this is

The engine's step-01 today points its two hunter lenses at bare BMAD skills and gives the two
auditors three-line prompts. pr-af's measured discipline — the three false-positive gates, the
severity rubric, the evidence-chain format, "what's NOT in the diff", and the author-intent
engagement rule — exists only in the research doc. This task transplants that text into
`step-01-review.md`, hunter lenses only, with adapted recall-first rubrics for the auditors,
plus the two corrections SCC-124 measured: the Blind Hunter must stop being pack-primed, and
the pack builder must stop starving late files.

## Acceptance list (each item names the assertion that proves it)

| # | Acceptance item | Proving assertion |
|---|---|---|
| A1 | step-01 carries the three FP gates (Gate 1 Reachability Proof, Gate 2 Evidence Chain, Gate 3 Confidence ≥ 0.6, "When in doubt, DROP the finding") addressed to the **hunter lenses only** | new `CHECKS` rows in `test_review_engine.py`, each with a counter-example proven rejected |
| A2 | step-01 **exempts both auditor lenses from Gates 1 and 3** by name, with the stated reason (a reachability proof is unwritable for a missing-test finding) and an adapted recall-first rubric for each | new `CHECKS` rows, counter-examples |
| A3 | step-01 carries the severity rubric (B.2, incl. "Use the FULL severity range"), the five review moves (B.3, incl. move 5 "what's NOT in the diff"), and the author-intent engagement rule (B.4) in the hunter prompt block | new `CHECKS` rows, counter-examples |
| A4 | step-01 primes **only repo-access lenses** with `EVIDENCE_PACK`; the Blind Hunter is excluded by name, with the SCC-124 evidence cited (+38.6 s of the +33.0 s gap; contradicts its context-starvation design) | new `CHECKS` row whose counter-example is the current "prime every lens" wording |
| A5 | every pack-receiving lens prompt states the pack is **a starting point, not the search space** | new `CHECKS` row, counter-example |
| A6 | step-01 states the **no-noise-filter rule** (no worthiness gating at any layer; pr-af's own measurement recall 0.69→0.52) so nobody adds one "for free" later | new `CHECKS` row, counter-example |
| A7 | `build_pack` divides `_PACK_MAX_CHARS` across the files it packs so a late file cannot be starved by earlier ones (the B2 meta-finding: `task_preflight.py` got 11 of 686 lines while smaller files were quoted in full) | new test in `test_evidence_extract.py`: two oversized files first + one small file last, asserting every file keeps its header and both big files keep a fair share — **RED on current code**. *(Shipped shape differs from the "one small first + one large last" written here: two-large-then-small reproduces the B2 starvation directly. Corrected 2026-08-12 during review.)* |
| A8 | the `.claude` engine cache is byte-identical to master, and the whole gate is green | existing cache-parity checks in `test_review_engine.py`; `run_all.py` all cases; `workflow_lint.py --toolkit-only` exit 0 |

## Steps

1. **RED** — extend `test_review_engine.py` `CHECKS` with the A1–A6 rows (pattern + applicable
   counter-example each, per that file's self-proving design) and add the A7 pack-budget test to
   `test_evidence_extract.py`. Run both bare; paste the failing output and read which line raised.
2. **GREEN, step-01** — rewrite the lens section of
   `.agents/skills/code-review-engine/steps/step-01-review.md`:
   - a **Hunter-lens contract** block (applies to Blind Hunter, Edge Case Hunter, and by its own
     words to any future hunter lens — SCC-126's literal lens inherits it without edits): the three
     FP gates (B.1), the severity rubric (B.2), the five moves (B.3), the author-intent rule (B.4,
     adapted: the rationale source is the diff's own comments/docstrings for the Blind Hunter, plus
     the story file where the lens receives one).
   - **Gate adaptation for the Blind Hunter's horizon:** it has no repo access by design, so its
     Gate 1/Gate 2 trace within the diff's own text; the gates' bar (no speculation, evidence
     chain, confidence ≥ 0.6) is unchanged.
   - an **Auditor rubric** block: Acceptance + Test-Adequacy are exempt from Gates 1 and 3,
     recall-first (a missed spec violation or missing test is the expensive error), Gate 2 adapted
     (the chain cites the spec item / the untested behavior instead of a call path).
   - the **pack paragraph** rewritten: repo-access lenses only; Blind Hunter never primed; the
     starting-point-not-search-space sentence required in each receiving lens's prompt.
   - the **no-noise-filter rule** stated once with the recall numbers.
3. **GREEN, pack budget** — rework the tail of `build_pack` in `evidence_extract.py`: build the
   blocks, and when the joined blob would exceed `_PACK_MAX_CHARS`, shrink the oversized blocks to
   an equal per-file share (files already under their share keep every byte; the freed remainder
   goes to the big ones) instead of slicing the tail off the assembled blob. `_PACK_MAX_CHARS`
   itself is unchanged — the total cap is pinned; only the distribution changes, which is exactly
   what the spec orders. Truncation labels state what is shown.
4. **Cache parity** — byte-copy the changed engine files master → `.claude/skills/code-review-engine/`
   in the same commit. Deliberately NOT via `/smh-sync-agents`: the sync engine and its manifest are
   both in SCC-135's open file set, and a sync run would touch surfaces that lane owns right now.
5. **Full gate** — re-run the RED checks green, then `run_all.py` and `workflow_lint.py
   --toolkit-only`, all bare. Then walkthrough, `task.yaml`, Dev Record, `/smh-code-review`.

## File set (and sibling overlap)

Mine: `.agents/skills/code-review-engine/steps/step-01-review.md` · its `.claude/skills/` twin ·
`.agents/scripts/evidence_extract.py` · `.agents/scripts/tests/test_review_engine.py` ·
`.agents/scripts/tests/test_evidence_extract.py` · this artifacts folder.

Checked against both live lanes (SCC-135: maps/sync/workflows/INDEX/SOP; SCC-119: jira seam
scripts+tests/commands/SOP): **zero file overlap.** Kept that way by two choices: no sync run
(step 4 above) and no SOP edit (next paragraph). No landing-order dependency either direction.

## Decisions taken while opening the lane

- **Subtask `start` refusal (exit 2):** `jira_feed.py start` refuses Subtasks ("start the parent").
  The parent SCC-116 is already In Progress, which is the state the seam wants; SCC-124 ran this
  identical shape end to end (Subtask key on a chore lane, ticket To Do during dev, Done at
  close-out). Proceeding on that precedent; the formal rule is SCC-119's open lane, not mine.
- **SOP currency:** the only gate-tripping path is `evidence_extract.py` (`skills/` is deliberately
  not a surface; `tests/` is exempt). The SOP's own row for that script says "you never type it" —
  the rebalance changes no flag and no operator-typed usage, so that sentence stays true, and both
  sibling lanes are editing the SOP doc. The commit touching `evidence_extract.py` therefore carries
  `[sop-ok]` as the auditable exit rather than a three-way SOP conflict.
- **BMAD skills untouched:** the hunter transplant lives in step-01 as prompt text the engine
  supplies to its subagents on top of the BMAD skills; `bmad-review-adversarial-general` and
  `bmad-review-edge-case-hunter` are vendor files and are not edited.

## Boundaries

- No noise/worthiness filter at any layer — this task *writes down* the prohibition (A6).
- No new lens (SCC-126), no verify wave (SCC-127), no caller rewire (SCC-128).
- steps 02–04 of the engine: **zero edits expected.** If a step-01 cross-reference forces one, it
  is named explicitly in the walkthrough — never silent.
- `/smh-quick-dev` and `/cicd-quick-dev` untouched (operator ruling in the epic Boundaries).

## Self-Audit (2026-08-12)

Repo: `Sudo_Hatter_Command` (lane worktree) | Branch: `chore/SCC-125-prompt-transplant` (from
`rev-parse`, not belief). Right-size: **Full** — a script with a test, plus a skill published to a
second cache. Mode: PRE-WORK.

- **Phase 0** — change set named in §File set; A1–A8 ↔ steps 1–5 trace both directions, no orphan
  item, no orphan step; no deployable path → this closes through `/smh-close-task-merge-tree`.
- **Phase 1** — blast radius walked: `evidence_extract.py` has **no callers** (no hook, no script
  imports it — the SOP's own row: "you never type it"); its test exists; the engine skill exists in
  exactly two places (master + `.claude` cache, byte-parity mechanically enforced by
  `test_review_engine.py`), none elsewhere in the tree. Existing pack assertions (6-file cap,
  400-line cap, ≤16 000 total, context-above-body) all stay green under the rebalance — verified
  against the test source, not assumed. Sibling lanes re-read: zero file overlap with SCC-135 and
  SCC-119 sets.
- **Phase 2** — no new command, rule, script, flag, or clone-and-tweak. The hunter-contract block
  naming future hunter lenses is spec-ordered (§SCC-125 names the SCC-126 lens), costs wording not
  machinery. The budget redistribution loop is justified over a fixed `cap // n` slice because small
  files leave budget a starved big file needs — the exact B2 failure.
- **Phase 3** — both machines: no new operator-typed command. Fresh clone: no new gate. Empty-input
  pass: impossible by construction — every new `CHECKS` row carries a counter-example the test
  proves it rejects, and the pack test must be seen RED first. Sibling-lands-first: still applies
  (no overlap, no sync run, no INDEX edit). Rollback: revert the merge; nothing irreversible.

| Finding | Severity | Disposition |
|---|---|---|
| `build_pack`'s in-code comment ("only the ORDER changed") becomes false under the rebalance | low | fold into step 3: update the comment in the same edit |
| `scripts/INDEX.md` rationale sentence describes the port-time truncation motive | info | leave untouched — it is historical rationale and stays true; editing it would create the only file overlap with SCC-119 |
| `[sop-ok]` on the `evidence_extract.py` commit | info | correct per the SOP's own row for this script; auditable in the log by design |

Four quick gates: verification strategy present per item (the table's right column) · nothing
irreversible · no step vague enough to guess (steps 02–04 expectation pinned to zero above) ·
conventions anchored (self-proving test design, artifacts layout, cache parity, key-in-commit).

Audit verdict: GO

⚠️ **AUDIT FINDING — this audit was wrong on one line, corrected 2026-08-12 after the code review.**
Phase 1 above claims *"Existing pack assertions … all stay green under the rebalance — verified
against the test source, not assumed."* One did not: the single-big-file control asserted
`len(out.strip()) >= 16000`, an exact-byte equality that line-boundary trimming cannot satisfy, and
the enumeration in that sentence simply omitted it. The change to that control is defended on its
merits in the walkthrough (it is red on the old code, for the right reason), but the audit sentence
overstated what had been checked. Recorded rather than edited away: an audit that quietly repairs
its own claims is worth nothing.
