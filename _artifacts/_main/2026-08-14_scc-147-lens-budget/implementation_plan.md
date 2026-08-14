# SCC-147 — interactive review callers must name `lens_budget: standard`

**Ticket:** SCC-147 (Subtask; the defect SCC-145's merge message tracked as "STILL OWED: SCC-143" —
same summary, this key is its current home).
**Lane:** `chore/SCC-147-lens-budget` · worktree `.claude/worktrees/lens-budget` · off `main` @ `0677441`.
**Parallel:** SCC-148 runs in a sibling session (task_preflight.py · git-policy.md ·
cicd-mobile-error-team.md) — **zero file overlap** with this set; landing order free. No other
`chore/*` worktree is live locally (SCC-145's was pruned by its close-out).

## The defect

The engine's step-01 defines `lens_budget` once: `standard` (interactive — caps bind, plus ONE
earned top-up) and `capped` (autopilot — caps bind, no top-up), and a caller that names nothing
gets `capped` as the deliberate safe default. `/cicd-code-review-AP` names `capped` explicitly.
The two INTERACTIVE callers — `/cicd-code-review` (Step 1 input table, no `lens_budget` row) and
`/smh-code-review` (Step 1 input table, no `lens_budget` row; rewired to the engine in SCC-128) —
name nothing, so a human-attended review silently runs on the overnight budget and the
literal-correctness lens loses the top-up it is supposed to have when someone is watching.

The SOP already documents the intended split — `workflows_testing_SOP.md:1689`: "Typed by hand it
runs `standard`" — so this change aligns the commands TO the SOP. Nothing an operator types or
reads in the SOP changes → the commit carries `[sop-ok]` with that justification, which is the
auditable exit.

## Acceptance list (Step 1, echoed and frozen)

| # | Item | The assertion that proves it |
|---|---|---|
| A1 | `/cicd-code-review`'s engine-invocation table passes `lens_budget: standard` explicitly | guard case pinning `^\|\s*`lens_budget`\s*\|\s*`standard`` in **that file's own body**; plus visible row in the diff |
| A2 | `/smh-code-review` answered: same omission, same fix — explicit `standard` row | second guard case, same pin, against that file's body |
| A3 | Guard cases live in `test_review_engine.py` and read each caller's OWN body, not step-01's claim (SCC-126 F7) | both callers added to `CALLER_FILES`; cases keyed to `.agents/commands/<caller>.md`; `run_all.py` green |
| A4 | The guard fails when the budget line is removed — proven, not assumed | INVERT/removal sweep per the SCC-145 doctrine: delete the row on disk per caller → guard RED naming that case → `git checkout` restore → green again; both outputs pasted in the walkthrough |
| A5 | No stale prose or drift left behind | `cicd-code-review-AP.md:9` comment ("the primary passes none and takes the capped default") updated same commit; `/smh-sync-agents` regenerates `.opencode/commands/` copies; full suite + `workflow_lint --toolkit-only` green at the landing sha |

## Steps

**S1 — RED first (A3, natural test-first red).** Edit `test_review_engine.py`:
`CICD_CMD = ".agents/commands/cicd-code-review.md"`, `SMH_CMD = ".agents/commands/smh-code-review.md"`,
`CALLER_FILES = (AP_CMD, CICD_CMD, SMH_CMD)`, and two CHECKS tuples:

```python
("interactive caller /cicd-code-review: invocation table passes lens_budget standard", CICD_CMD,
 r"^\|\s*`lens_budget`\s*\|\s*`standard`", re.M,
 "| `lens_budget` | `standard`", "| `lens_budget` | `capped`"),
("interactive caller /smh-code-review: invocation table passes lens_budget standard", SMH_CMD,
 r"^\|\s*`lens_budget`\s*\|\s*`standard`", re.M,
 "| `lens_budget` | `standard`", "| `lens_budget` | `capped`"),
```

The harness's own anti-vacuity machinery (counter-example must APPLY and must BREAK the regex)
covers the tuples; the `capped` mutant breaks the `standard` pin by construction. Run the file →
**RED on both new cases** (the rows don't exist yet) and on their `counter-example applies`
sub-checks. Paste the red. NOTE: this red is the assertion-failure kind — read which check line
raised, not just the exit code.

**S2 — GREEN (A1, A2, A5-prose).** Add one row to each invocation table:
- `cicd-code-review.md` (after the `DEFERRED_WORK` row):
  `| \`lens_budget\` | \`standard\` — a human is sitting in front of this review, so the earned top-up applies; the autopilot twin names \`capped\`. step-01 owns both definitions — name the budget, never restate the caps |`
- `smh-code-review.md` (after the `ARTIFACT_DIR` row): same row, task-lane wording.
- `cicd-code-review-AP.md` header comment → "this twin passes `lens_budget: capped`; the primary
  passes `standard` explicitly (SCC-147)". (Twin-drift law: fix one, re-diff the twin.)
Re-run the guard → green. Then `run_all.py` full, bare.

**S3 — removal proof (A4).** For each caller in turn: delete its `lens_budget` row on disk →
`python3 .agents/scripts/tests/test_review_engine.py` → RED naming that caller's case →
`git checkout -- <file>` → green. RESTORE discipline per the doctrine: restore immediately, even
on interrupt; nothing stays mutated on disk.

**S4 — sync generated doors (A5).** `/smh-sync-agents` (the `.opencode/commands/` copies of both
commands are generated). Assert copies carry the new row.

**S5 — commit + gate.** Explicit paths only; subject leads `SCC-147`, body carries `[sop-ok]`
with the alignment justification; message via `-F` (it quotes backticked commands). Then the full
gate bare: `run_all.py` (expect 23 files, baseline 1875 + 2 checks ×3 sub-assertions = +6 cases),
`workflow_lint.py --toolkit-only`.

## Scope guard

Four hand-edited files: two interactive callers (one row each), the AP twin (one comment line),
the guard (two tuples + two constants). Generated `.opencode` copies via sync only. NOT touched:
step-01 (its text is already correct), SKILL.md (`lens_budget` input row already exists and says
"absent defaults to `capped`"), the SOP (already states the intended behavior), the fixture.

## Risks / notes

- Guard-file case-count guards elsewhere: SCC-145's `test_command_surfaces.py` counts nothing in
  this file; `run_all.py` totals are reported, not pinned — verify by running, not assuming.
- `CALLER_FILES` additions also generate two "exists with a body" checks — harmless, additive.
- Weak uplink on this machine today: pushes may 408; that is transport, never a gate verdict.

## Self-Audit (2026-08-14) — PRE-WORK, Full

`Repo: lens-budget | Branch: chore/SCC-147-lens-budget` (echoed from `rev-parse`, cwd is the lane
tree). Plan: this file. Ticket: SCC-147.

- **Phase 0** — change set: 4 hand-edited files (2 caller tables · 1 twin comment · 1 guard) +
  generated copies via sync. Right-size **Full** (guard file + multi-platform command surface).
  Checkable list frozen above (A1–A5), traceable both directions: every step maps to an item,
  no step traces to nothing. No deployable path → Task lane confirmed.
- **Phase 1** — blast radius, each row verified by command: `.opencode/commands/` copies are FULL
  bodies and `.agents/workflows/` launchers exist for BOTH commands → S4's sync is load-bearing,
  not optional. No name change → no INDEX row. No guard case in `test_review_engine.py` pins the
  AP divergence comment being edited (AP pins at lines 834–861 target other strings — checked).
  No test pins run_all totals (grep for 1875/1794: zero hits in `tests/*.py`). Sibling lanes:
  none live locally (`git worktree list`: main + this lane only); SCC-148's set
  (task_preflight.py · git-policy.md · cicd-mobile-error-team.md) — zero overlap.
- **Phase 2** — no tripwires: no new file, no new flag, no clone-and-tweak; both new tuples trace
  to A3/A4. The guard cannot-fail class is answered by the harness's own counter-example proof
  PLUS the on-disk removal sweep (A4), per § Mutation Testing.
- **Phase 3** — pre-mortem: both machines run the guard via `run_all.py` (no new machine-specific
  command); no new hook (nothing OFF on a fresh clone); a future editor who drops the row gets a
  red whose case name states exactly what is missing; empty/missing caller file reads as RED
  (exists-with-a-body check), never as pass; all four platform caches reached via S4; SCC-148
  landing first changes nothing (no shared file); rollback = revert the one commit, nothing
  irreversible in the lane (the Jira `start` transition already happened and is idempotent).

**Findings baked into the plan (both S2-scope corrections, no re-plan needed):**

| Where | Severity | Finding | Disposition |
|---|---|---|---|
| S2, AP twin | minor | The divergence note is a 3-line bullet ("…⚠ For an INTERACTIVE caller `standard` is the intended budget — raised as a follow-on…, not patched from inside its twin."). Editing only its first line would leave the follow-on prose stale — the follow-on IS this ticket. | Rewrite bullet #1 whole: both callers now name their budget explicitly — twin `capped`, primary `standard` (SCC-147). "THREE divergences remain" stays true (the VALUES still diverge). |
| S5, case math | minor | +6 was wrong: 2 tuples ×3 checks **+2** `CALLER_FILES` existence checks = **+8** (expect 1883 if baseline 1875 holds and nothing else changed — verify by running). | Corrected here; S5 asserts by measurement, not arithmetic. |

Four quick gates: verification strategy present (every A-item names its proving command) ·
nothing irreversible · no step vague enough to guess (row text and tuple text are written out
verbatim in S1/S2) · convention fit (tuple shape matches the file's own CHECKS contract; row
wording matches the tables' existing voice).

Audit verdict: GO

## Scope amendment (2026-08-14, operator ruling)

The review's deferred finding 7 — the `standard` top-up clause is UNQUOTED in step-01, so by
step-01's own assembly convention it never reaches the lens, making `standard` and `capped`
behaviourally identical — was deferred as a follow-on ticket. The operator ruled it rolled into
this lane instead ("we don't need to over-engineer this, just fix it"). Amended scope:

- **step-01-review.md** — the top-up clause is now a BLOCKQUOTE routed `standard`-only; under
  `capped` nothing is appended, so the same convention that caused the defect is the enforcement.
  The truncation disclosure hands the lens the withheld files' PATHS, never a count — the existing
  blockquote already ordered the lens to *name* what it did not get, which a count cannot satisfy,
  and the top-up is earned by naming a specific withheld file.
- **test_review_engine.py** — +4 net tuples (+12 cases, 762 → 774 in-file): paths-not-count,
  notes half, blockquoted top-up, standard-only routing, capped-side absence.
- **smh-close-task-merge-tree.md + SOP** — the anti-loop rule, from the operator's live report on
  the SCC-148 close-out: the close-out gate is MECHANICAL only; the review verdict stands at its
  sha; re-running a recall-first no-noise-filter reviewer always yields new findings, so "review
  until zero findings" never terminates. Prose guidance, deliberately unguarded — a test would be
  the over-engineering this amendment was ordered to avoid.
