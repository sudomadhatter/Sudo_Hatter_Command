---
IsArtifact: true
ArtifactMetadata:
  title: SCC-124 baseline trial + stopwatch gate - house engine vs vendor review, timed
  type: implementation_plan
  date: 2026-08-12
---

# SCC-124 — Baseline trial + stopwatch gate (go/no-go for SCC-128)

## Goal

Race the scaffolded house engine (`code-review-engine`, SCC-122 + SCC-123) head-to-head against the
current review (`bmad-code-review`, run exactly as `/cicd-code-review` Step 1 invokes it today) on
one real, already-landed diff — TIMED. **Acceptance: engine clean-diff wall-clock ≤ incumbent.**
A miss records NO-GO and blocks SCC-128 (caller rewire) until the regression is fixed.
Epic spec §SCC-124: `_artifacts/_main/2026-08-12_scc-116-house-review-engine/implementation_plan.md:84`.

## Operator rulings folded in (2026-08-12, this session)

- **Nothing modifies BMAD.** The vendor skill is only *run*, unmodified, as the stopwatch's
  incumbent side. (It cannot be edited anyway — regenerated from upstream.)
- **No smh arm.** `smh-code-review` is the quick/task lane (single subagent, mostly non-code
  changes); timing it here is over-engineering. Out of scope; SCC-128 still rewires it later per the
  epic ("gains the lenses" is a scoped capability change, not this gate's subject).
- **Cost cap respected:** 2 runs per arm × 2 arms = 4 review runs ≈ 16 lens subagents,
  ≈ 0.5–1 M tokens, ~30–60 min wall-clock total.

## Trial design

**Trial diff — SCC-110 lane** (merge `e6354d3`, "hooks armed", landed 2026-08-11):
`git diff e6354d3^1 e6354d3` — 10 files, +1089/−11; 618 of those lines are real code
(`hooks_armed.py` new, `task_preflight.py` edited, 3 test files). Landed, reviewed
(PASS @ `08489ea`), so it is the closest thing to a certified-clean diff we own — exactly the
"clean diff" the acceptance bar prices. Frozen ONCE to `inputs/diff.patch` so all 4 runs review
byte-identical input.

**Spec, both arms:** SCC-110's own `implementation_plan.md` (at the landed tree) →
`review_mode: full` → **4 lenses on BOTH sides.** Same lenses, same prompts (SCC-122 ported them
verbatim), same model (session model; lenses inherit), interleaved **A B A B** to cancel load
drift. Apples to apples; the only structural differences are the engine's evidence-pack priming
(new, SCC-123) and its triage/record steps replacing the vendor's triage/present.

| | Arm A — incumbent | Arm B — house engine |
|---|---|---|
| What runs | `bmad-code-review` skill, as `/cicd-code-review` Step 1 invokes it, under `bmad_code_review_sudo_fix.md` (run-to-completion, no HALTs) — production's actual shape | `code-review-engine` with the full caller contract (I am the caller) |
| Gets | frozen diff + spec | frozen diff + spec + `EVIDENCE_PACK` from `evidence_extract.py --repo . --pack <the 6 code files>` |
| Clock includes | steps 2–4 (review → triage → present) | pack build + steps 1–4 (pack is part of the engine's real cost) |
| Output goes to | `runs/A<N>/` in this trial folder | `runs/B<N>/` (`FINDINGS_SINK`, `ARTIFACT_DIR` pointed there) |

Timing: `date +%s` brackets each run — start when the arm's flow begins (Arm B's clock starts
before the pack build), stop when its summary/verdict returns. Diff resolution (frozen, shared) is
outside both clocks: neither arm pays for what the caller owns.

Known shape, stated so nobody "discovers" it: engine step-02 is a pass-through until SCC-127, so
Arm B times fan-out + triage + record. That IS the clean-diff cost the bar prices — the verify wave
only ever fires on findings.

**⛔ Findings are evidence, not fixes.** Both arms review landed history; nothing gets applied to
the repo. A real bug surfaced in landed code → reported to the operator for its own ticket, never
fixed in this lane. The SCC-110 lane's historical walkthrough is never edited.

## Measurements → walkthrough

1. Wall-clock per run; per-arm mean + both draws (spread stated — a bar met inside noise is said so).
2. Finding counts per lens and per triage bucket, both arms.
3. Overlap matrix: found-by-both / A-only / B-only.
4. Anything the 4 current lenses missed that pack-priming surfaced (feeds SCC-125/126 evidence).
5. **`GO | NO-GO for SCC-128`** verdict line, from the acceptance bar on the means.

## Files touched

Artifacts only — this trial ships no code, no command, no rule:
- `_artifacts/_main/2026-08-12_scc-124-baseline-trial/` — this plan, `task.yaml`,
  `inputs/` (frozen diff + spec copy + evidence pack), `runs/A1|B1|A2|B2/` (raw lens outputs +
  timing), `walkthrough.md`.
- No usage surface changes → `sop_currency` passes with no `[sop-ok]`. No new scripts → no new
  guard file; suite total stays 21 files / 1091 cases (measured at close, never quoted forward).

## Execution order

1. Freeze inputs: diff, spec, evidence pack (`inputs/`) — commit.
2. Runs, interleaved: A1 → B1 → A2 → B2 — raw outputs + timestamps committed per run.
3. Score: timing table, counts, overlap, misses.
4. `walkthrough.md` with the timing evidence + `GO | NO-GO for SCC-128` — hand back for
   `/smh-close-task-merge-tree`.

## Verification

```bash
python3 .agents/scripts/tests/run_all.py                      # bare; expect all files green
python3 .agents/scripts/workflow_lint.py --toolkit-only       # bare; 0 errors 0 warnings
```
Plus the trial's own controls: 4/4 runs completed with all lenses `ok` (a dead lens invalidates
that run's clock — rerun it, noted); byte-identical `inputs/` across all runs (`shasum`).

## Open questions

None blocking. One recorded alternative: an AGY BMAD story diff would mirror `/cicd-code-review`'s
production context more closely, but crosses repos for test data with no gain to the stopwatch —
SCC-110 is real, local, and mid-size. Chosen: SCC-110.
