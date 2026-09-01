---
IsArtifact: true
ArtifactMetadata:
  title: SCC-232 — Literal-Correctness cost measurement (SCC-124 fixture, Arm A)
  type: bug_list
  date: 2026-08-20
---

# SCC-232 — the Literal-Correctness cost measurement

**Why this exists:** step-01 called Literal-Correctness "the one lens with a real token cost" with
no datum behind it (struck by SCC-230); tier membership for the two review levels is data-gated
(SCC-232), and this lens postdates the only per-lens trial we own
(`_artifacts/_main/2026-08-12_scc-124-baseline-trial/scoring.md`).

## Protocol

Same fixture, verified byte-identical by SHA-1 before the run: diff `e55b7c79…` (10 files,
83,128 bytes) · spec `a7091ed4…` · pack `03840243…`. **Arm A** (no evidence pack — the arm the
comparison numbers come from). Lens prompt assembled per step-01's assembly convention: the LC
discipline blockquote + diff-scope rule + Gate-1 adaptation + `standard` top-up clause; diff
handed as a path (83KB > the 9,000-char spill rule); repo access from the lane worktree at
`ba7feb7`+lane commits. Model: Fable (the trial ran Fable 5 — same family). Condition noted: the
repo has moved since the freeze (SCC-140/144/190 landed); the lens was told to verify relocated
definitions against the diff's own context lines and said where it did.

## Result

| round | wall clock (subagent duration_ms) | tokens | tool uses |
|---|---|---|---|
| 1 | **1,082.0 s** (1,082,046 ms) | 147,814 | 23 |

**n = 1, and the 3-round protocol was deliberately not completed:** the decision this number
feeds compares the 3-round mean against the Acceptance Auditor's measured 127.4 s. With round 1
at 1,082.0 s, the minimum possible 3-round mean is 1,082.0/3 = **360.7 s** — 2.8× the threshold
even if rounds 2 and 3 took zero seconds. The decision is invariant under any completion, so two
more ~18-minute runs buy no information for it. (Not a budget cap — an information argument;
re-run the full protocol if this number is ever compared against a threshold above 360 s.)

Reference: the run produced a real report — 2 *important* findings on the frozen diff, one of
them the vacuous-ARMED hole later independently fixed by SCC-140 — so the timing reflects the
lens doing its actual job, not idling.

## The decision (per SCC-232's pre-registered rule)

LC (1,082.0 s lower-bounded mean 360.7 s) **> Acceptance Auditor 127.4 s** →
**quick = Test-Adequacy + Acceptance Auditor · Literal-Correctness moves to standard.**
