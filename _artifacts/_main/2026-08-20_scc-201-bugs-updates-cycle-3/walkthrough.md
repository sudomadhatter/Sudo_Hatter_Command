---
IsArtifact: true
ArtifactMetadata:
  title: SCC-201 cycle 3 — walkthrough
  type: walkthrough
  date: 2026-08-20
---

# SCC-201 cycle 3 — the readers and gates that half-fire silently

**Lane:** `chore/SCC-201-bugs-updates-cycle-3`, cut from `origin/main` @ `db253fc`
**Riders:** SCC-242 · SCC-206 · SCC-243 — all three close with the parent.

## What was wrong, and what it cost

One theme, four defects: **a mechanism runs half of itself and reports success.**

| Rider | The defect | What it cost |
|---|---|---|
| SCC-242 | `finish`'s merge check was hardcoded to `origin/main` | a story lane read *held* forever while its own file said `done` |
| SCC-242 | `index-row` appended to the end of the **field**, not the section | SCC-201's index read `(empty)` above two rows |
| SCC-242 | a clone is verbatim, and said nothing about the three edits that leaves owed | SCC-244 was corrected by hand |
| SCC-206 | the continuation window never closed | the board was posted a row reading half one instruction and half another |
| SCC-243 | two callers' verdict tables were short | the script returns an answer the command has no instruction for |

## The three things measurement changed

**1. The landing-ref fix alone would have shipped a no-op.** `MERGE_DOORS` did not list
`/cicd-close-story-merge-tree`, so `merge_row_state` returned `None` before any comparison ran.
Found before writing code; it became acceptance row D and the lane's first RED.

**2. `/cicd-non-crit-pr-push` Step 0.5 qualified nothing.** `NOT-COMMAND-CENTRE` returns before
any path is read, so in a child project — the only place that command runs — `--paths
backend/api.py` and `--paths docs/notes.md` give the identical answer. Measured against
`Projects/AGY_AVIATIONCHAT`. Its `TASK` and `HANDOFF` rows could never fire. Documenting the
verdict alone would have left the step inert, so the command gained the deployable-path check
that does run there, importing `PRODUCT_DIRS` and `CI_DIR` rather than re-typing them.
⛔ `lane_qualify.py` was **not** edited — the centre-only scope is the operator's ruling.

**3. A guard accused the story door of lying.** CS-13 grepped for one needle, so replacing raw
`acli` with the safer `finish` verb turned it red. Widening it then let the door's own prose read
as a transition — and one such sentence sits ahead of the landing push. An invocation carries
`--key`; a mention does not. Applied to both verbs, since `acli` always had the same blind spot.

## Corrections to the plan, from measurement

- The verdict gap was **1 on `smh-`, 2 on `cicd-`** — not 2 and 2. `smh-quick-fix` already listed all five.
- Row N named the wrong authority: there is **no firestore-rules constant** (`firebase/` covers it),
  and `.github/` is **deliberately not deployable** (SCC-118) — it is a toolkit prefix, so it routes to `TASK`.

## Evidence

| Gate | Result |
|---|---|
| `test_jira_feed.py` | **366/366** |
| `test_lane_qualify.py` | **32/32** |
| `test_command_surfaces.py` | **177/177** |
| `test_twin_parity.py` | **58/58** |
| `run_all.py` (enforcement suite) | see below |
| mutation sweep | **10 mutants, each killed by the case declared against it** — `mutation-sweep.md` |

The one legitimate twin divergence is declared with the repo's own auditable marker and printed
by `test_twin_parity`: `NOT-COMMAND-CENTRE` is a **STOP** on `smh-` and the **EXPECTED** answer on
`cicd-`.

## Board repaired live

SCC-201's `INDEX` now lists all four subtasks, indented, with the falsified placeholder gone.
**SCC-238 had never been indexed at all.** Backfilled through the fixed verb.

## Commits

```
b6660d9  chore(sync): regenerate the five mirrors
9a70df3  fix(jira_feed): index rows INTO the section; a clone says what it left owed  (G, H)
93d8483  fix(open_actions): a ticked item ENDS the continuation window               (I, J, K, L)
bae11fa  feat(lane-qualify): every caller lists every verdict                        (M, N, O, P, R)
6187d7e  feat(close-story): the story door calls the closer again                    (F)
3f49cf7  feat(jira_feed): resolve the landing target; story door in MERGE_DOORS      (A-E)
3b992bb  docs(plan): the lane plan + two self-audit passes (NO-GO then GO)
```

review-runtime: inline

## Code Review (2026-08-20)

⛔ **`inline`, and that is a WEAKER review than the fan-out — recorded, not disguised.** Five
clean-context lenses were launched twice and died both times without returning, having filled their
own context. **The cause was the caller's, not the lenses':** three of them were told to run the
house suite, and `run_all.py` prints every passing case across 40 files — that output lands in the
lens's context. The second attempt trimmed the diff from 143 KB to 66 KB and banned bare suite runs;
it was killed on the operator's instruction rather than run to completion, with the lane a week
behind schedule.

Per the engine's own law, an `inline` review **drops the Blind Hunter rather than fake it** — the
assessor is holding this lane's plan and walkthrough, so no lens here was context-starved and none
may claim to have been.

lenses_run:
- Blind Hunter · dead — cannot run inline; the assessor holds the plan, so independence is unavailable
- Edge Case Hunter · recovered-inline — boundary sweep run by hand over `index_append` and `_collect`
- Literal-Correctness Hunter · recovered-inline — changed symbols checked against their definitions
- Acceptance Auditor · recovered-inline — 17 rows, Declared Change Set and DO NOTs re-checked
- Test-Adequacy Auditor · recovered-inline — mutation sweep re-run, 40/40 suite
lenses_counted:  4/5
lenses_na:       none
findings:        1 patch · 0 decision · 0 defer   (2 relevance kills)
severity_floor:  CONCERNS
notes:           fan-out unavailable — two launch attempts died on lens-side context exhaustion,
                 caused by caller instructions that flooded them. Recorded as a caller defect.

### What the hunt found

**1 finding fixed — and it was a fail-open in this lane's own fix.** `_collect`'s new HTML-comment
skip had no exit for an **unterminated** comment: `<!-- note` with no `-->` swallowed every item
below it. A typo in a walkthrough would silently drop owed operator work and `finish` would close
the ticket over it — **the exact shape SCC-206 exists to close, reintroduced by SCC-206's fix.** An
item line now ends the comment: over-reporting holds a ticket, under-reporting closes one that
should have held. Case **J3** pins it.

**2 dismissed under the assessor ruling** (real, stated, but they change no reachable behaviour):
`index_append` normalises CRLF to LF across the whole field — **measured: the live board returns
zero CR bytes**, so the input is unreachable; and the function alone is not idempotent, but
`cmd_index_row` dedupes before calling it.

### Evidence

| Gate | Result |
|---|---|
| `run_all.py` (40 files, bare, exit code read) | **40/40, exit 0** |
| mutation sweep | 10 mutants, each killed by its declared case |
| blast radius vs current `main` | re-derived after absorbing SCC-240 — three additive overlaps, one generated file regenerated |
| every repo path and anchor the diff names | resolves |

Verdict: CONCERNS @ 5f6dd912e

The floor is `CONCERNS` because the review ran `inline` with one lens dead — not because anything in
the diff is unresolved. Every finding raised was fixed or dismissed with a measured reason.

## Your Actions

- [ ] **The merge itself** — lands via this branch's PR
