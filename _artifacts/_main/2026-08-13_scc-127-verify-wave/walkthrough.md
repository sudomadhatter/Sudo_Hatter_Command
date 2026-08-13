---
IsArtifact: true
ArtifactMetadata:
  title: SCC-127 verify wave — walkthrough
  type: walkthrough
  date: 2026-08-13
---

# SCC-127 — Verify wave (walkthrough)

Lane: `chore/SCC-127-verify-wave` · worktree `.claude/worktrees/scc-127-verify-wave` · off `main`
@ `36e1ffe`. Epic: SCC-116 (house review engine). Plan + self-audit: `implementation_plan.md`
beside this file.

**What shipped.** `steps/step-02-verify.md` stops being an honest pass-through and becomes the
wave the engine was scaffolded for: an **Evidence Verifier** and a **Compound Synthesis** role,
launched as ONE concurrent batch, both fed the programmatic `evidence_extract.py --findings`
dossier, both self-gating on the finding count. Severity becomes evidence-forced — the verifier's
`revised_severity` reaches step 3, where the rule that it outranks the hunter's assertion was
already written and had nothing to act on. `steps/step-03-triage.md` loses its "step 2 is a
pass-through until SCC-127" caveat for the live rule and gains `compound` as a finding source.

## Task Checklist

- [x] Pin repo + lane from command output; move SCC-127 to `In Progress` (`jira_feed start` exit 0)
- [x] Read the sibling lanes before planning (SCC-126 live, SCC-128 empty)
- [x] Fix the checkable acceptance list A1–A10 from the ticket + the epic plan
- [x] Write `implementation_plan.md`; run `/smh-self-audit` → **GO**, 2 findings baked in
  - the embedded extractor command must carry the `python3`/`python` two-machine note, or a PC
    role subagent fails and "ran cold" records a fake reason
  - a gate-skipped wave must write a note, or 0-findings reads identically to all-confirmed
- [x] STOP for the literal `approved` (given 2026-08-13)
- [x] RED — 55 new guard rows binding the WIRING, each with a counter-example proven to go red
- [x] GREEN — rewrite step-02, edit step-03, mirror both to the `.claude/` cache
  - one check failed for a real reason on first run: my line wrap split the phrase it pins
    (`gates exactly as hard as the path it replaces`) across a newline; rewrapped, not weakened
- [x] Full suite + toolkit lint bare, on the code that lands
- [x] Commit inside the worktree, explicit paths (`89a5423`, `6441e64`)
- [x] Review gate — `/smh-code-review` (section below)

## Evidence

Measured at HEAD **`6441e64`** (`git rev-parse HEAD`), after the last code change. The two
artifact commits after it do not invalidate it; no code or test changed.

| Acceptance item | Proving assertion | Result |
|---|---|---|
| A1 — 0 findings → no wave | `step-02: zero findings skips the entire step` + the gate table row `\| 0 \| **does not run** \| **does not run** \|` | GREEN |
| A2 — <2 findings → no compound | `step-02: under two findings there is no compound pass` + gate row for `1` | GREEN |
| A3 — both roles consume `--findings`; join by index | `step-02: the extractor invocation is pinned, both modes' flags` · `the findings JSON carries the keys the extractor reads` · `the join is by index, never by title` | GREEN |
| A4 — verifier framing + 4 questions + 5 output fields | 11 rows: `neither reviewer nor adversary` · `independent investigator` · Q1–Q4 · `verified` / `actual_behavior` / `revised_severity` / `revised_confidence` / `verification_notes` | GREEN |
| A5 — compound contract | 6 rows: `NEW findings only` · `contributing_findings` exact titles · confidence ≥ 0.6 · empty list valid | GREEN |
| A6 — extractor failure = cold, does NOT cap | `a failed extractor leaves the verifier running cold` · `a cold verifier does NOT cap the verdict` · `a dead script is not a dead role` | GREEN |
| A7 — role-failure contract inherited | `a failed role is retried once` · `rerun inline` · `only a still-dead role raises the floor` · `a gate-skipped role is not a dead role` | GREEN |
| A8 — no filter at this layer | `this step drops nothing` · `a refuted finding still reaches triage` · `the no-noise-filter law binds at this layer too` | GREEN |
| A9 — step-03 caveat retired | `grep -rn "pass-through until SCC-127\|verification pass not yet installed" .agents/skills/code-review-engine/ .claude/skills/code-review-engine/` → **no matches** | GREEN |
| A10 — suite + byte-identical cache | `run_all.py` 21/21 exit 0; `cache is byte-identical to master` | GREEN |

### RED → GREEN

**RED** — the 58 new rows run against the still-unwritten step file (the assertions fail on absent
content; nothing dies in setup):

```
[FAIL] step-02: both roles run concurrently in one wave
[FAIL]   ^ counter-example applies: steps/step-02-verify.md: '**concurrently, in ONE wave**' not present, so the proof would be vacuous
[FAIL]   ^ counter-example is rejected: check survives its own counter-example — it cannot fail on content
[FAIL] step-02: the gate table gives 0 findings neither role
...
-- 380/554 passed --                                        EXIT 1   (174 failing = 58 rows x 3)
```

**GREEN** — after the step files were written and mirrored:

```
-- 554/554 passed --                                        EXIT 0
```

### The gate, run bare (no pipes — a piped gate returns the pipe's exit code)

| Gate | Output | Exit |
|---|---|---|
| Enforcement suite | `21/21 files passed` · **1497/1497 cases** | **0** |
| Toolkit lint | `-- 0 error(s), 0 warning(s), 8 info --` | **0** |
| Assertion evidence | `-- 554/554 passed --` | **0** |
| SOP currency | no output (the diff carries no usage surface) | **0** |
| SOP currency — **positive control** | same script, `--paths .agents/commands/smh-code-review.md` → `Commit rejected.` | **1** |
| Link + anchor | 9 paths across 3 changed `.md` files, **0 dead** | — |
| Door parity | no command added/renamed/deleted (`git diff --name-only main...HEAD -- .agents/commands/` = 0) | n/a |

The SOP control matters: exit 0 on this diff is a real pass, not a vacuous one — the same script
rejects a commit the moment a usage surface is in the path list. The `[sop-ok]` in the commit
message is therefore belt-and-braces rather than load-bearing, and is recorded as such.

## Case-count arithmetic (nothing displaced anything)

Counted from the AST of both versions of the guard file rather than by hand:

| | rows total | step-02 rows | step-03 rows |
|---|---|---|---|
| `main` @ `36e1ffe` | 115 | 5 | 18 |
| this lane @ `6441e64` | 169 | 56 | 21 |

**55 rows authored** (51 replacing the 5 scaffold-era step-02 rows, 4 replacing 1 in step-03) for
a **net +54**, and every row contributes exactly 3 assertions: **+162 cases**. That lands on both
measured totals exactly — `test_review_engine.py` 392 → **554**, suite **1335 → 1497** — so the
change is precisely additive and no commit displaced another lane's tests.

⚠️ **Correction, recorded rather than rewritten:** the commit message on `89a5423` and the first
draft of the `_main/INDEX.md` row both say *"58 new guard rows"*. That was written from a hand
count before the AST count was run; the measured figures are the ones above. The INDEX row is
corrected; the commit message stays as it is, with this line as its erratum.
