# SCC-124 scoring — head-to-head, 2 rounds, interleaved A B A B

All stamps from `date +%s.%N` files committed per run. Wave = t1−t0 (B includes pack build);
record = t2−t1 (triage + findings write); total = t2−t0. Model: Fable 5 all arms, all lenses.
Input integrity: diff e55b7c79…, spec a7091ed4…, pack 03840243… — byte-identical all 4 runs.

## Wall-clock

| run | pack | lens wave | slowest lens | wave overhead | triage+record | TOTAL |
|---|---|---|---|---|---|---|
| A1 (incumbent) | — | 312.5 s | 249.4 s (edge) | 63.1 s | 34.5 s | **347.0 s** |
| B1 (engine) | 0.19 s | 303.4 s | 238.4 s (edge) | 65.0 s | 43.7 s | **347.2 s** |
| A2 (incumbent) | — | 276.6 s | 226.0 s (edge) | 50.6 s | 37.0 s | **313.6 s** |
| B2 (engine) | 0.36 s | 340.5 s | 288.2 s (edge) | 52.2 s | 34.3 s | **374.8 s** |

| aggregate | Arm A | Arm B | delta |
|---|---|---|---|
| mean total | **330.3 s** | **361.0 s** | **+30.7 s (+9.3 %) — bar missed on means** |
| same-round pairs | R1: 347.0 | R1: 347.2 | +0.2 s (+0.05 %) — dead heat |
| | R2: 313.6 | R2: 374.8 | +61.2 s (+19.5 %) |
| in-arm spread | 33.4 s | 27.6 s | gap ≈ spread; A-max and B-min touch at 0.2 s |

**Where the 30.7 s lives.** Not in the engine's mechanics: the pack build costs 0.19–0.36 s,
wave overhead is 50–65 s in BOTH arms, triage+record is 34–44 s in BOTH arms. The whole gap is
one lens draw — B2's Edge Case Hunter ran 288 s where the same lens on the same prompt ran 238 s
in B1 and 226–249 s in A (it chose to ground 11 tool calls that draw). The Edge lens is the long
pole in all 4 runs; its per-draw depth is sampling variance, not arm structure. With n=2 the
means-based bar resolves to a coin flip on that one draw.

## Findings

| run | raw | unique | decision | patch | defer | dismiss | floor |
|---|---|---|---|---|---|---|---|
| A1 | 33 | 29 | 3 | 20 | 5 | 1 | n/a (vendor has no floor) |
| B1 | 34 | 25 | 1 | 20 | 4 | 0 | CONCERNS |
| A2 | 37 | 27 | 3 | 20 | 3 | 1 | n/a |
| B2 | 32 | 22 | 2 | 18 | 2 | 0 | CONCERNS |

Counts are triage-granularity-sensitive (the engine's step-03 folds families harder); overlap is
the honest comparison. Core findings found by BOTH arms in EVERY round: the tracking-state
vacuous-ARMED family, the unreachable NOT-CLEAR branch, the D/F/N Windows reds, the pathspec
`.githooks/*` false-block, the AC6 `--global` spec drift, the nt-branch/exit-code/git_root test
gaps, the live-repo suite coupling, N+1 "(None)" noise, JSON shape duplication.

- **A-arm-only across both rounds:** `via` dispatcher-hook pairing never validated (A2 blind);
  untyped `rep` boundary param (A2); prose-vs-`code`-field assertion layer (A2); POSIX-only
  `touch` remedy (A1/A2).
- **B-arm-only across both rounds (pack-priming credit):** `claims_gates` never demands the
  claimed script be tracked — proven from the diff's own fixture (B1); GIT_CONFIG_GLOBAL leak
  into test fixtures (B1); case-label scramble (B1); TOCTOU is_file/stat race (B2);
  never-claimed-gates e2e verdict gap (B2). Plus one meta-finding the trial itself wanted:
  **the 16k pack cap truncates task_preflight.py to 11 of 686 lines** — a real SCC-125/126
  tuning input (a lens told us the pack under-served exactly the file the diff edits most).
- Neither arm reproduced the landed review's 13 findings verbatim (different round, different
  draws); both arms independently rediscovered its headline class (vacuous ARMED).

## Read against the acceptance bar

The approved bar: engine clean-diff wall-clock ≤ incumbent, on the means. **As measured, n=2:
361.0 > 330.3 — missed by 9.3 %.** The same data shows structural parity (pack ≈ 0.3 s is the
engine's only mechanical addition; every other stage times the same) and the gap traceable to a
single high-variance lens draw. Round-1's interleaved pair — the cleanest like-for-like — was a
0.2 s dead heat. There is no code-shaped regression to "fix"; there is a sampling question to
resolve. Options recorded for the operator's ruling in the walkthrough.
