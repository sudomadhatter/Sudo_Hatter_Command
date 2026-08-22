---
IsArtifact: true
ArtifactMetadata:
  title: SCC-127 verify wave — Evidence Verifier ‖ Compound Synthesis, self-gating
  type: implementation_plan
  date: 2026-08-13
---

# SCC-127 — Verify wave (implementation plan)

Parent spec: `_artifacts/_main/2026-08-12_scc-116-house-review-engine/implementation_plan.md`
§SCC-127 (approved epic plan). Ticket: SCC-127, Subtask of the SCC-116 work, In Progress.
Lane: `chore/SCC-127-verify-wave` in `.claude/worktrees/scc-127-verify-wave`, off `main` @ `36e1ffe`.

## Goal

Replace the honest pass-through in `step-02-verify.md` with the real verify wave: an **Evidence
Verifier** and a **Compound Synthesis** role running concurrently as one subagent wave, both
consuming `evidence_extract.py --findings` dossiers, both self-gating on finding count — so a clean
diff still costs zero new wall-clock. Severity becomes evidence-forced: the verifier's
`revised_severity` feeds the step-03 mapping table, where it already outranks the hunter's
assertion (that half landed in SCC-122).

## Acceptance list — every item checkable

Authority: the ticket's description (read from the live board this session) + the approved epic
plan §SCC-127. Each item below is enforced by a relationship-bound check in
`test_review_engine.py` (each with a counter-example proven to go red), except A9/A10 which are
command runs.

- **A1 — Self-gating, step level:** 0 step-1 findings → the whole step is skipped; no wave runs.
- **A2 — Self-gating, compound level:** fewer than 2 findings → the compound role does not run;
  the verifier still does.
- **A3 — Both roles consume `evidence_extract.py --findings` output**, and the step names the
  exact invocation (`--repo` + `--findings` + `--diff`). Results join to findings **by index, in
  input order** — titles are not unique, so index is the only reliable join (the extractor's own
  documented contract).
- **A4 — Verifier role framing is pr-af's, verbatim in intent:** neither the original reviewer
  nor the adversary — an independent investigator; the four questions (claim accurate? scenario
  reachable? broader context? severity proportionate?); per-finding output `verified` /
  `actual_behavior` / `revised_severity` / `revised_confidence` / `verification_notes`.
- **A5 — Compound contract:** NEW findings only, never restating originals; `contributing_findings`
  (exact titles) required on every one; emit only at confidence ≥ 0.6 with concrete evidence; an
  empty list is a valid, expected answer.
- **A6 — Extractor-failure semantics:** the extractor is code, not a lens — if it cannot run or
  dies, the verifier runs **cold** (repo access only) with a note in the record, and this does
  **NOT** cap the verdict.
- **A7 — Role-failure contract inherited unchanged from step-01:** retry once → rerun inline →
  record the degradation; only a role still dead after BOTH raises `severity_floor` to CONCERNS.
- **A8 — No filter at this layer:** step 2 never drops a finding — a refuted finding is annotated
  (`verified: false` + notes) and handed to triage, which owns buckets. Verification states are
  distinguishable in the record (a checked finding never reads like an unchecked one).
- **A9 — step-03's scaffold-stage caveat is retired:** the "⚠ Today no revised severity exists
  (step 2 is a pass-through until SCC-127)" paragraph is replaced by the live rule (unverified /
  cold findings score on hunter-asserted severity); `grep -rn "pass-through until SCC-127"
  .agents/skills/code-review-engine/` returns nothing.
- **A10 — Suite + cache:** `python3 .agents/scripts/tests/run_all.py` exits 0, and
  `.claude/skills/code-review-engine/` is byte-identical to master (enforced by the existing
  cache checks).

## File set (everything this lane touches outside `_artifacts/`)

| File | Change |
|---|---|
| `.agents/skills/code-review-engine/steps/step-02-verify.md` | full rewrite: the real wave |
| `.agents/skills/code-review-engine/steps/step-03-triage.md` | retire the two "until SCC-127" caveats (§2 ⚠ paragraph); add `compound` to the `source` enum |
| `.agents/scripts/tests/test_review_engine.py` | replace the 5 scaffold-era step-02 checks with the new-contract checks; update the one step-03 check pinned to the retired paragraph |
| `.claude/skills/code-review-engine/steps/step-02-verify.md`, `step-03-triage.md` | byte-copy of master (cache law) |

## Sibling-lane dependencies (read this session, per Step 0.5)

- **SCC-126 (literal lens):** uncommitted edits to `test_review_engine.py` and `step-01-review.md`.
  Overlap: `test_review_engine.py` (their new checks target step-01; mine target step-02/step-03 —
  disjoint sections of the `CHECKS` tuple) and the `.claude/skills` cache tree (disjoint files).
  Landing order: **either order works**; the second lander resolves a trivial adjacent-hunk merge
  in the tests file and re-runs the suite. One real conflict candidate: if SCC-126 also adds
  `literal` to step-03 §1's `source` enum line that I extend with `compound` — a one-line merge,
  both values belong.
- **SCC-128 (rewire callers):** no changes yet; its file set (commands, rules, INDEXes) does not
  intersect mine. It depends on this lane semantically (the callers it rewires get the verified
  engine) but not textually.

## Design decisions (the ones the spec left open)

1. **Who runs the extractor.** The engine's tool grant deliberately excludes Bash
   (`allowed-tools: Read, Write, Glob, Grep, Task` — test-pinned). So the orchestrator cannot run
   `evidence_extract.py` itself. Each verify-role **subagent** runs it instead, as its first
   action: the orchestrator embeds the findings JSON (keys `title` / `file_path` / `line_start` /
   `body` / `evidence` — the extractor's documented input shape) and the diff in the role prompt;
   the role materializes them to files it owns and invokes the script. The duplicate run (once per
   role) is deliberate: it is code-speed, deterministic over the same tree, and avoids both a
   shared-scratch race and a third serial subagent hop.
2. **Index is the join, everywhere.** The extractor returns one package per finding in input
   order and documents index as the only reliable join (duplicate titles are the expected case in
   a multi-lens fan-out). The verifier is therefore required to return its per-finding results in
   input order too, and the orchestrator reconciles by index — never by title.
3. **Compound findings enter triage unverified**, tagged `source: compound`, carrying their
   `contributing_findings`. pr-af does not re-verify compounds in v1 and neither do we
   (`compound_dedup_phase` is explicitly deferred in the epic plan). Their severity is the
   compound role's own label and is subject to step-03 alias normalization like any other.
4. **A refuted finding is annotated, never dropped** (the no-filter law from step-01 §"No noise
   filter" applies at this layer too, and the step says so). Triage owns the `dismiss` bucket;
   verification supplies the evidence it decides on.
5. **⚠️ AUDIT FINDING (baked): two-machine invocation.** The step file embeds the extractor
   command in role prompts; the Mac has no bare `python`, the PC no `python3`. The embedded
   command carries the house convention explicitly (`python3` — `python` on the PC), so a role
   subagent on either machine runs it as written.
6. **⚠️ AUDIT FINDING (baked): a skipped wave must say so.** The A1 self-gate (0 findings → no
   wave) is correct behavior, but silence would make "skipped by gate" indistinguishable from
   "ran clean". The step requires `notes` to carry `verify wave: skipped (0 findings)`, and the
   test pins that requirement — an empty input never reads as a pass that happened.

## Steps — each mapped to the assertion that proves it

1. **RED:** rewrite the step-02 section of `CHECKS` in `test_review_engine.py` (and the one
   step-03 check pinned to the retired caveat) to bind A1–A9. Run
   `python3 .agents/scripts/tests/test_review_engine.py` → paste the failing output (the new
   checks red against the current pass-through file; the structural/counter-example halves prove
   the checks can fail on content).
2. **GREEN:** rewrite `steps/step-02-verify.md`; edit `steps/step-03-triage.md` (§2 caveat →
   live rule; `source` enum gains `compound`); byte-copy both to `.claude/skills/`. Re-run the
   test file green, then the full suite: `python3 .agents/scripts/tests/run_all.py` exit 0.
3. **Commit** inside the worktree, explicit paths, subjects leading `SCC-127`. If `sop_currency`
   fires (tests live under `.agents/scripts/`), the change alters nothing an operator types —
   engine-internal step files and their guard — so `[sop-ok]` with that stated reason
   (SCC-125 set the precedent for exactly this class of change).
4. **Review gate:** `/smh-code-review` per lane law; verdict into the walkthrough.
5. **Close artifacts:** `walkthrough.md` (checklist, RED→GREEN evidence, review verdict, your
   actions), `task.yaml` manifest, `_artifacts/_main/INDEX.md` row, Dev Record via
   `jira_feed.py devrecord`, push the branch. STOP — merge belongs to
   `/smh-close-task-merge-tree`.

## Boundaries

- `step-01-review.md`, `SKILL.md`, `step-04-record.md`, every command file, every rule: untouched
  (SCC-126/SCC-128 territory or settled).
- No worthiness/noise filter added at any layer (epic plan boundary, restated because this step is
  where one would be tempting).
- `evidence_extract.py` itself: untouched — it already ships both modes (SCC-123).
- No re-verify/dedup pass over compound findings (explicitly deferred in the epic plan).

## Self-Audit (2026-08-13)

Mode: PRE-WORK. Right-size: **Full** (the change set includes a test guard and the review-gate
surface). Repo/branch pinned from command output: `scc-127-verify-wave` worktree,
`chore/SCC-127-verify-wave`.

- **Phase 0** — change set named (4 files outside `_artifacts/`); acceptance list A1–A10 all
  checkable; traceability both ways clean (every A-item has a step, no step without an A-item);
  no deployable path touched — this closes through `/smh-close-task-merge-tree`. ✅
- **Phase 1** — reference sweep for `step-02-verify` / `pass-through until SCC-127` /
  `verification pass not yet installed`: every hit is inside the planned file set (master + cache
  + the test file). `SKILL.md`'s flow line ("verification pass over what the lenses found")
  describes the new behavior correctly, unchanged. No SOP row, no INDEX row, no command names the
  pass-through. Sibling lanes read live: SCC-126 holds uncommitted `test_review_engine.py` +
  `step-01-review.md`; SCC-128 empty. ✅
- **Phase 2** — no new command/rule/script/flag; the per-role duplicate extractor run is a
  deliberate, documented duplication traced to the test-pinned tool grant (no Bash for the
  orchestrator); no gate-that-cannot-fail (the new checks each carry a counter-example proven to
  go red, same as the file's existing design). ✅
- **Phase 3** — two findings, both baked into Design §5–6: the two-machine `python3`/`python`
  note in the embedded command, and the mandatory skipped-wave note so an empty finding set never
  reads as a wave that ran. Cache reach: the engine is a Claude-cache skill (`.claude/skills/`),
  byte-identity test-enforced; opencode/Antigravity reach it through commands, untouched here.
  Sibling-lands-first: either order works; second lander re-merges disjoint hunks of the tests
  file and re-runs the suite. Rollback: pure `git revert`, nothing irreversible (the Jira start
  transition is reversible and idempotent). ✅

| Finding | Severity | Scenario | Disposition |
|---|---|---|---|
| embedded extractor command must run on both machines | important | PC role subagent gets `python3`, fails, verifier "runs cold" for a fake reason | baked — Design §5 |
| gate-skip must be recorded in `notes` | important | 0-finding review reads identically to a verified one | baked — Design §6, pinned by a test |

Landing-order dependency: `test_review_engine.py` shared with SCC-126 (disjoint sections; either
order; second lander merges + re-runs). Four quick gates: verification strategy present (each
A-item names its check); nothing irreversible; no step vague enough to guess (the step file's
prompt text is written in the plan's design decisions, not improvised later); convention fit
anchored (step-01's assembly convention, blockquote = prompt text, reused verbatim).

Audit verdict: GO

