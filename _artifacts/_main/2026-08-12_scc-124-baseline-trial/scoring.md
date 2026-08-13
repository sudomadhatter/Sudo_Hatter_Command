# SCC-124 scoring — head-to-head, 3 rounds, interleaved A B / A B / A B

All stamps from `date +%s.%N` files committed per run. Wave = t1−t0 (B includes pack build);
record = t2−t1; total = t2−t0. Model: Fable 5, all arms, all lenses, same session. Input
integrity: diff e55b7c79…, spec a7091ed4…, pack 03840243… — byte-identical across all 6 runs.
Round 3 ordered by the operator as a tie-break after round 1 tied (+0.2 s) and round 2 split.

## Wall-clock

| run | pack | lens wave | slowest lens | wave overhead | triage+record | TOTAL |
|---|---|---|---|---|---|---|
| A1 | — | 312.5 s | 249.4 (edge) | 63.1 s | 34.5 s | **347.0 s** |
| B1 | 0.19 s | 303.4 s | 238.4 (edge) | 65.0 s | 43.7 s | **347.2 s** |
| A2 | — | 276.6 s | 226.0 (edge) | 50.6 s | 37.0 s | **313.6 s** |
| B2 | 0.36 s | 340.5 s | 288.2 (edge) | 52.2 s | 34.3 s | **374.8 s** |
| A3 | — | 226.8 s | 186.0 (edge) | 40.7 s | 26.6 s | **253.4 s** |
| B3 | 0.20 s | 268.6 s | 233.2 (blind) | 35.4 s | 22.3 s | **290.9 s** |

| aggregate (n=3) | Arm A | Arm B | delta |
|---|---|---|---|
| mean total | **304.7 s** | **337.6 s** | **+33.0 s (+10.8 %)** |
| round pairs | 347.0 / 313.6 / 253.4 | 347.2 / 374.8 / 290.9 | +0.2 s · +61.2 s · +37.5 s |

**Where the delta actually lives — per-lens means across 3 rounds (from subagent duration_ms):**

| lens | Arm A mean | Arm B mean | delta | read |
|---|---|---|---|---|
| Blind Hunter | 180.9 s | 219.5 s | **+38.6 s** | the pack tax: B's blind reads +16 KB it never sees in A |
| Edge Case Hunter | 220.5 s | 237.9 s | +17.4 s | smaller tax; it reads the repo anyway |
| Acceptance Auditor | 127.4 s | 128.2 s | +0.8 s | parity |
| Test-Adequacy | 75.3 s | 77.9 s | +2.6 s | parity |

Orchestration is at parity everywhere: pack build 0.19–0.36 s, wave overhead 35–65 s in both
arms, triage+record 22–44 s in both arms. **The +33 s is the cost of every lens consuming the
16 KB pack, concentrated in the Blind Hunter** — the one lens whose entire design is context
starvation, and which step-01 currently primes anyway ("prime every lens"). SCC-125 lever,
recorded: pack the repo-access lenses only; the blind lens loses nothing it was designed to have,
and the measured tax (~two-thirds of the whole gap) goes away.

## Findings

| run | raw | unique | decision | patch | defer | dismiss | floor |
|---|---|---|---|---|---|---|---|
| A1 | 33 | 29 | 3 | 20 | 5 | 1 | n/a (vendor) |
| B1 | 34 | 25 | 1 | 20 | 4 | 0 | CONCERNS |
| A2 | 37 | 27 | 3 | 20 | 3 | 1 | n/a |
| B2 | 32 | 22 | 2 | 18 | 2 | 0 | CONCERNS |
| A3 | 38 | 27 | 2 | 20 | 5 | 0 | n/a |
| B3 | 39 | 27 | 3 | 20 | 4 | 0 | CONCERNS |

Core set found by BOTH arms EVERY round: tracking-state vacuous-ARMED family · unreachable
NOT-CLEAR branch · D/F/N Windows reds · pathspec `.githooks/*` false-block · AC6 `--global` spec
drift · nt-branch/exit-code/git_root/--json test gaps · N+1 "(None)" · non-repo misdiagnosis ·
`~` expansion · live-repo suite coupling · JSON shape issues · hardcoded expect-key.

- **A-only across all rounds:** `via` dispatcher-pairing never validated (A2) · untyped `rep`
  param (A2) · prose-vs-`code`-field assertion layer (A2).
- **B-only across all rounds (the pack/priming credit):** claims_gates never demands the claimed
  script exist — proven from the diff's own fixture (B1) · GIT_CONFIG_GLOBAL/system leak into
  test fixtures (B1) · TOCTOU is_file/stat race (B2) · never-claimed-gates e2e verdict gap (B2) ·
  NOT-CLEAR verdict/exit-code mismatch if ever reachable (B3) · "NOT ARMED above the clear line"
  mixed-signal surface (B3) · **meta: the 16 k pack cap truncates task_preflight.py to 11/686
  lines** (B2) — direct SCC-125/126 tuning input.
- Grounding quality: B's edge lens cited `pre-push-main-approval.sh:38` (the disk-read seam) from
  pack context — the sharpest single evidence line any lens produced in 6 runs.

## Verdict inputs

- **Original bar** (plan as approved): engine ≤ incumbent on means. **Not met:** 337.6 > 304.7
  (+10.8 %).
- **Amended rule** (operator, mid-trial, 2026-08-12, verbatim intent): *"if it's a better process
  and more accurate then the new one wins if they are close in time."*
- Close in time: +33 s on a ~5-minute review, with round 1 a 0.2 s tie and a named, removable
  cause (blind-lens pack tax) for most of the rest.
- Better process: caller contract (no self-resolved diffs) · deterministic triage law + severity
  floor the callers stop reinventing · no HALTs, no status flips, no vendor-adapter attention
  contest · verify-wave slot ready for SCC-127.
- More accurate: B-only grounded findings in every round (list above) at equal-or-equal core
  recall; zero A-only findings that B missed in more than one round.
