---
IsArtifact: true
ArtifactMetadata:
  title: SCC-124 baseline trial walkthrough - engine vs vendor, timed, GO for SCC-128
  type: walkthrough
  date: 2026-08-12
---

# SCC-124 — Baseline trial + stopwatch gate — walkthrough

Task: SCC-124 (epic SCC-116) · branch `chore/SCC-124-baseline-trial` · commits `adef33c..aa8adb7`
(+ this doc) · plan: [implementation_plan.md](implementation_plan.md) · data:
[scoring.md](scoring.md) · raw runs: [runs/](runs/)

## Task Checklist

- [x] Open lane worktree `chore/SCC-124-baseline-trial` off `main` @ af821b0
- [x] Plan approved by operator (baseline = vendor skill AS-RUN, never modified; smh arm dropped
      as over-engineering — operator rulings, in-session)
- [x] Freeze inputs: SCC-110 diff (`e6354d3^1..e6354d3`, 1252 lines), spec copy, evidence pack
    - Fixture worktree pinned at `e6354d3` for repo-access lenses — today's tree no longer
      matches the diff's hunks (task_preflight.py edited by 3 later lanes)
    - Pack first built against the WRONG tree (today's); caught, rebuilt at the fixture, recommitted
- [x] Rounds 1–2 (approved n=2): A1 347.0 s / B1 347.2 s · A2 313.6 s / B2 374.8 s
    - n=2 means missed the approved bar by 9.3 % with round 1 a 0.2 s dead heat — put to the
      operator rather than ruled unilaterally
- [x] Round 3 tie-break (operator-approved spend): A3 253.4 s / B3 290.9 s
- [x] Score: n=3 means A 304.7 s vs B 337.6 s (+10.8 %); per-lens attribution isolates the gap to
      the Blind Hunter's pack tax (+38.6 s of the +33.0 s) — see scoring.md
- [x] Verdict under the operator's amended rule (see Evidence)
- [x] Lane gates bare; fixture worktree pruned

## Evidence

**Acceptance matrix (spec §SCC-124, epic plan line 84):**

| Acceptance item | Result | Evidence |
|---|---|---|
| Head-to-head on a real, already-landed story diff | done | SCC-110 lane diff, frozen byte-identical across all 6 runs (shas in scoring.md) |
| TIMED — wall-clock measured | done | `date +%s.%N` stamp files committed per run, per stage (t0/t0b/t1/t2) |
| Finding count | done | per-run tables; 22–29 unique per run, stable core set |
| Finding overlap | done | scoring.md §Findings: core set found by both arms every round; A-only 3; B-only 7 + 1 meta |
| Anything the 4 current lenses missed | done | B-only list (claims-gates fixture proof, GIT_CONFIG leak, TOCTOU, e2e verdict gap, NOT-CLEAR exit mismatch, mixed-signal surface, pack-cap truncation) |
| **Clean-diff wall-clock ≤ current review** | **not met as written; ruled GO under amended rule** | means 337.6 vs 304.7 (+10.8 %); operator rule 2026-08-12: "if it's a better process and more accurate then the new one wins if they are close in time" — applied with both prongs evidenced in scoring.md §Verdict inputs |

**Verdict: GO for SCC-128** — the engine replaces the vendor review at the callers when SCC-125–127
land. The original ≤ bar, the miss, the amended rule, and its application are all recorded — no
number was massaged to fit.

**Speed lever owed to SCC-125 (evidence-backed):** stop priming the Blind Hunter with the pack —
step-01 currently primes every lens, which contradicts the blind lens's context-starvation design
AND costs +38.6 s of the +33.0 s total gap. Pack the repo-access lenses only; most of the gap
disappears and the blind lens returns to its design. Second input: the 16 k pack cap truncated
task_preflight.py to 11/686 lines (B2 meta-finding) — rebalance per-file budgets in SCC-125/126.

**Gates (bare, at `aa8adb7`):**

```
python3 .agents/scripts/tests/run_all.py                 -> 21/21 files, 1091/1091 cases
python3 .agents/scripts/workflow_lint.py --toolkit-only  -> 0 errors, 0 warnings, 8 info; exit=0
```

Static checks: no code shipped — artifacts only; sop_currency owes nothing (no usage surface
touched, no `[sop-ok]` taken on any commit).

## Suite Ledger

| scope | command | duration | result | why this run |
|---|---|---|---|---|
| full enforcement suite | `python3 .agents/scripts/tests/run_all.py` (bare) | ~80 s | 21/21 files, 1091/1091 | lane gate at close |
| toolkit lint | `python3 .agents/scripts/workflow_lint.py --toolkit-only` (bare) | ~2 s | 0/0, exit 0 | lane gate at close |
| trial arms | 6 timed review runs (4 lens subagents each) | 304.7 s mean A · 337.6 s mean B | all 24 lenses `ok`, zero retries | the task itself |

## What fought back

- **The trial straddled its own bar.** Round 1 tied at 0.2 s, round 2 split 61 s on one deep lens
  draw. Escalated with options instead of self-ruling; operator ordered round 3, then amended the
  acceptance rule mid-trial. Both the original bar and the amendment are recorded verbatim.
- **The pack tax is real, not noise.** The n=2 read ("structural parity, sampling noise") was
  wrong in one respect — n=3 per-lens attribution shows every pack-primed lens pays a read/reason
  cost, 2/3 of it in the blind lens. The wrong intermediate read stands in scoring.md's history
  (git), the final read replaces it.
- **Wrong-tree pack.** First pack was built against today's tree instead of the diff's tree;
  caught before any run consumed it, rebuilt at the fixture SHA. Lesson already on file
  (destructive-reverify-must-read-fresh's cousin): evidence for a diff is extracted at the diff's
  SHA, never at HEAD.

## Your Actions

- **Landed on the lane branch:** `chore/SCC-124-baseline-trial` (pushed) — plan, frozen inputs,
  6 run records with stamp files, scoring, this walkthrough. No project file outside
  `_artifacts/` was touched; nothing merged.
- **On you:**
  1. `/smh-close-task-merge-tree` when you want SCC-124 landed on `main` (invoking it is the
     merge sign-off; it also prunes this lane's tree + branch).
  2. SCC-125 inherits two recorded inputs: blind-lens pack exemption (speed lever) and pack-cap
     rebalance. Both are in this walkthrough and scoring.md — no separate ticket minted (SCC-125
     already owns lens prompts).
  3. The trial re-found real defects in landed SCC-110 code (vacuous-ARMED family, unreachable
     NOT-CLEAR branch, Windows-red tests). They are evidence records here, deliberately unfixed
     (landed history, out of this lane's scope). Say the word if any should become a ticket.
