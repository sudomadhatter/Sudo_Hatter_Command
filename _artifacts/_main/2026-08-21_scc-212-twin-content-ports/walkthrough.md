---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-212 — walkthrough: the twin standard applied to the cicd command bodies"
  type: walkthrough
  date: 2026-08-21
---

review-runtime: fan-out

# SCC-212 — walkthrough

**Lane** `chore/SCC-212-twin-content-ports` · **Base** `origin/main` @ `295abe5`
**Plan** [implementation_plan.md](implementation_plan.md) (with its Self-Audit) · **Build spec** [edit-spec.md](edit-spec.md) · **Manifest** [task.yaml](task.yaml)
**Instruments** [assert-scc212.py](assert-scc212.py) · [sweep.json](sweep.json) · [gates/suite.json](gates/suite.json)

## What this lane did, in one paragraph

SCC-205 built the twin-parity **mechanism**; this lane applies the **content**. The ticket's 84
findings deduplicate to **66**. Seven read-only passes re-measured every one against `295abe5`:
**56 were live and 10 were already settled** — by SCC-205 Part C, SCC-211, or SCC-225's approved
self-audit rewrite. **Twelve backlog edits were wrong at HEAD** and were replaced by what the tree
actually needs. Six laws that both families genuinely share are now **fenced** as `twin-law` rather
than copied once and left to drift again, which is the failure the whole ticket exists to close.

## Task Checklist

- [x] Re-measure all 66 findings against `295abe5` — seven parallel read-only passes, one per target file
  - The backlog's line numbers were taken at `fd22097` and are stale everywhere; every anchor was re-taken
  - 12 backlog edits were **wrong at HEAD** — see the ledger's "replaced by" column
- [x] Write the plan + edit-spec; run `/smh-self-audit` → **GO** with 5 anchored findings, all fixed in-plan
- [x] RED first — `assert-scc212.py`, one named case per live finding, `--red origin/main`
  - ⚠️ **Four cases were vacuous on the first run** and were re-aimed before any edit landed (below)
- [x] RED for the fence mechanism through the live gate, not the assertion file
- [x] Apply the ports, file by file, anchored by quoted text
  - ⚠️ **Two guard defects surfaced mid-build** and were fixed here (below)
- [x] Test pins — `FENCED_TODAY` +2 pairs, `LOADERS` +1 **and its scope pin** +1
- [x] SOP updated in the same commit as the commands (currency gate armed, no `[sop-ok]`)
- [x] One `/smh-sync-agents` run; three Antigravity mirrors flip to thin launchers as predicted
- [x] Suite through the receipt writer — **red first, then green** (below)
- [x] Mutation sweep — **two survivors were real**, fixed, re-swept to 15/15; the review pass took it to **21/21**
- [x] Review gate — five lenses, all as subagents in clean contexts, **all findings reproduced by
      execution** ([review-findings.md](review-findings.md))
  - ⚠ **25 confirmed defects, all fixed in thread before the verdict**; 4 relevance-killed with reasons
  - ⚠ **The defects clustered in the machinery this lane wrote to prove the ports, not the ports** —
    see `## Code Review` for the three that would each have reported success


## Disposition ledger — all 66 findings, by ID

⛔ **Acceptance row 1 says "applied, or explicitly dismissed here with a reason — no silent drops."
This is the "here."** Every ID the ticket carries appears below exactly once. `APPLIED` names the case
in [assert-scc212.py](assert-scc212.py) that holds it (RED at `origin/main`, GREEN at HEAD);
`SETTLED` names what landed it and why no edit was owed.

**56 live and applied · 10 settled.** (The plan's roster said 55/11; the re-measurement had
`QD-C12` filed SETTLED, and it is not — its case is RED at `origin/main` and the edit landed. Counted
correctly here.)

### `cicd-dev-story-tests.md` — 14 live, 0 settled

| ID | Disposition | Case |
|---|---|---|
| DEV-01 | APPLIED — backtick-in-`-m` hazard, command half **and** rule half | `DEV-01`, `DEV-01-rule` |
| DEV-02 | APPLIED — the full suite goes through the receipt writer, stamp-first | `DEV-02` |
| DEV-03 | APPLIED — the mutation doctrine replaces one RELOCATE sentence | `DEV-03a` `DEV-03b` `DEV-03c` `DEV-03d` |
| DEV-04 | APPLIED — new Step 0.8, the runtime probe **before** the plan | `DEV-04a` `DEV-04b` |
| DEV-05 | APPLIED — the RED paste must name WHICH LINE RAISED | `DEV-05a` `DEV-05b` |
| DEV-06 | APPLIED — a `NO-GO` stops the lane | `DEV-06` |
| DEV-09 | APPLIED — the eject tripwire as its own Step 3.5 | `DEV-09` |
| DEV-10 | APPLIED — sibling lanes read at 0.6, not at review | `DEV-10` |
| DEV-11 | APPLIED — absorb the epic branch before the first edit | `DEV-11` |
| DEV-12 | APPLIED — link the gitignored assets, here and in ① | `DEV-12`, `DEV-12b` |
| DEV-14 | APPLIED — `reproduce-before-you-fix` loaded in the rules block | `DEV-14` |
| DEV-15 | APPLIED — `work-consolidation` loaded in the rules block | `DEV-15` |
| DEV-16 | APPLIED — five rules the block never loaded | `DEV-16a`–`DEV-16e` |
| DEV-17 | APPLIED — a characterization check is labelled, never presented as a red | `DEV-17` |

### `git-policy.md` — 2 live, 1 settled

| ID | Disposition | Case |
|---|---|---|
| DEV-01 (rule half) | APPLIED — the rule now carries the law the pointer points at | `DEV-01-rule` |
| QD-C1 (rule residue) | APPLIED — found by re-measurement, not by the backlog: `:30-32` still said a `chore/*` lane merges back to `main` in the same session | `QD-C1-rule` (an absence row) |
| **D7** | **SETTLED** — landed by SCC-211 @ `73c6f9c`; the `:70` write-gate row already says it | — |

### `cicd-merge-epic-workingtrees.md` — 14 live, 0 settled

| ID | Disposition | Case |
|---|---|---|
| MERGE-01 | APPLIED — `git -C "$TREE"` on every call; assert the tree before the push | `MERGE-01a` `MERGE-01b` |
| MERGE-02 | APPLIED — modify/delete joins the overlap classes | `MERGE-02` |
| MERGE-03 ⚠ | APPLIED — **backlog edit was wrong at HEAD**: its preflight call omits `--expect-key` (required since SCC-210, argparse exits 2), `--fetch` is now default, and its "exit 2 = BLOCKED" reading blocks every healthy lane. Replaced by the solo door's `landed`-row carve-out, plus `--require-gates` (review finding E4) | `MERGE-03a` `MERGE-03b` |
| MERGE-04 | APPLIED — an absorb that touches code, script **or doc** VOIDS the verdict | `MERGE-04a` `MERGE-04b` |
| MERGE-05 | APPLIED — a machinery lane lands LAST | `MERGE-05` |
| MERGE-06 ⚠ | APPLIED — **backlog edit was wrong at HEAD**: it names `/cicd-close-workingtree`, a door SCC-210 deleted, and compares against a local `epic/*` ref the shared checkout never holds. Replaced by verify-then-report against the REMOTE ref | `MERGE-06` |
| MERGE-07 | APPLIED — rewrite vs edit; gate-or-script; regenerate, never hand-merge | `MERGE-07a` `MERGE-07b` `MERGE-07c` |
| MERGE-08 ⚠ | APPLIED — **backlog edit was wrong at HEAD**: it points at `/cicd-update-sprint-memory` Step 4.5, deleted by SCC-210. Replaced by `jira_feed.py devrecord` + `finish --landing-ref` (SCC-242), never raw `acli … transition` | `MERGE-08a` `MERGE-08b` |
| MERGE-09 | APPLIED — an empty eligible set is a STOP ⛔ **fenced** `merge-empty-set-stop` | `MERGE-09` `MERGE-09b` `MERGE-09c` |
| MERGE-11 | APPLIED — the case totals must be additive | `MERGE-11` |
| MERGE-12 | APPLIED — run every gate BARE | `MERGE-12` |
| MERGE-14 | APPLIED — an unclassified conflict is a finding, not a judgement call | `MERGE-14` |
| MERGE-15 | APPLIED — the commits-ahead column; a 0-ahead lane was never built | `MERGE-15` |
| MERGE-16 | APPLIED — an unmerged branch in another repo ⛔ **fenced** `merge-cross-repo-order` | `MERGE-16` |

### `cicd-quick-dev.md` — 9 live, 4 settled

| ID | Disposition | Case |
|---|---|---|
| QD-C1 ⚠ | APPLIED (partial) — **backlog edit was wrong at HEAD**: SCC-205 wrote *"there is none"* for the project-repo chore door; SCC-211 @ `73c6f9c` then created **two**. Replaced by the door table the diff selects from | `QD-C1a`, `QD-C1b` (absence) |
| QD-C4 ⚠ | APPLIED (partial) — the header slot moved; the probe must precede Step 3 ⛔ **fenced** `review-runtime-probe` | `QD-C4a` `QD-C4b` |
| QD-C7 | APPLIED — fetch before the cut; `--unset-upstream` after it | `QD-C7a` `QD-C7b` |
| QD-C8 | APPLIED — sibling lanes are a landing-order dependency | `QD-C8` |
| QD-C9 | APPLIED — pin the key before any tool answers; move the ticket at the tree | `QD-C9a` `QD-C9b` |
| QD-C10 | APPLIED — the backtick hazard | `QD-C10` |
| QD-C11 | APPLIED (partial) — link the gitignored assets | `QD-C11` |
| QD-C12 | **APPLIED** — the `task.yaml` manifest on the ad-hoc lane. ⚠ **The plan filed this SETTLED and was wrong**; its case is RED at `origin/main` | `QD-C12` |
| QD-C14 ⚠ | APPLIED — **backlog edit was wrong at HEAD**: the story half must name `/cicd-close-story-merge-tree` (SCC-210), not the save | `QD-C14` |
| **C2 C3 C5 C6** | **SETTLED** — landed by SCC-205 Part C, verified line-by-line at `295abe5` | — |

### `cicd-create-epic-sprint.md` — 6 live, 0 settled

| ID | Disposition | Case |
|---|---|---|
| PAIR-01 | APPLIED — the rules-in-force block, and the operator's word opens **Step 3** after the reorder | `PAIR-01a` `PAIR-01b` `PAIR-01c` |
| PAIR-02 ⚠ | APPLIED — **source moved**: the not-approval list now lives in `smh-plan-task.md:234-236` | `PAIR-02` |
| PAIR-05 ⚠ | APPLIED — **backlog path was wrong at HEAD**: the epic-level test-design output is `_bmad-output/test-artifacts/test-design-epic-<N>.md`, not `test-design/…` | `PAIR-05a`–`PAIR-05d` |
| PAIR-06 ⚠ | APPLIED — **backlog edit was wrong at HEAD**: its wholesale step move breaks the mint, because `jira_feed.py outline --epic N` dies without the `## Epic N` heading the moved step writes. Replaced by dedupe → bare mint (1a) → keyed cut (1b) → `epics.md` (2) → outline backfill | `PAIR-06` |
| PAIR-07 | APPLIED — `-C "$PROJECT_ROOT"` on the epic cut | `PAIR-07` |
| PAIR-08 | APPLIED — look before you mint | `PAIR-08` |

### `cicd-clean-code-audit.md` — 5 live, 0 settled

| ID | Disposition | Case |
|---|---|---|
| QD-C1 ⚠ | APPLIED (placement) — **backlog edit was wrong at HEAD**: "append at `:87`" would DUPLICATE what Part E added. The live defect is that the two scan rows sit in Step 2B, which an embedded run skips | `QD-C1/C2-cc` |
| QD-C2 ⚠ | APPLIED (placement + `Path(__file__)`) — same duplication; same relocation | `QD-C1/C2-cc`, `QD-C2-cc` |
| QD-C3 ⚠ | APPLIED — **backlog's `PROJECT_ROOT/` prefix dropped**: redundant under `:40`, and it would break fence identity ⛔ **fenced** `memory-sweep` | `QD-C3-cc`, `QD-C3-sc` |
| QD-C4b | APPLIED — never fall back to the lobby | `QD-C4b-cc` |
| QD-C5 (HIGH) | APPLIED — unstaged edits join the set on a standalone run (review finding B6 scoped it) | `QD-C5` |

### `cicd-code-review.md` / `smh-code-review.md` — 7 live, 1 settled

| ID | Disposition | Case |
|---|---|---|
| QD-C1 ⚠ | APPLIED — **backlog said DELETE a sentence that is TRUE** (`MERGE_DOORS` includes the story door). Replaced, not deleted; C2 folded in | `QD-C1-cr` (absence), `QD-C2-cr` |
| QD-C3 ⚠ | APPLIED — **worse at HEAD than the backlog knew**: `$WORKTREE`/`$EPIC` are bound later, so the bindings move up (review finding B8 then re-bound them per shell block) | `QD-C3-cr`, `QD-C3-cr-b` |
| QD-C4 ⚠ | APPLIED — **"in three lines" does not match `walkthrough_roster.py` E7**, which counts rows under a heading matching `0.7|re-deriv`; the port mandates the sub-heading ⛔ **fenced** `rederive-record` | `QD-C4-cr-a` `QD-C4-cr-b` `QD-C4-sr` |
| QD-C5 ⚠ | APPLIED (partial) — the guard list is inline `(a)/(b)` prose at HEAD, so this lands as `(c)` | `QD-C5-cr` |
| QD-C6 ⚠ | APPLIED — **worse at HEAD**: `HEAD_SHA` was read from `$PROJECT_ROOT`, not the worktree | `QD-C6-cr` |
| QD-C7 | APPLIED — the memory store is named and left alone | `QD-C7-cr` |
| QD-C9 (smh) | APPLIED — the `DEFERRED_WORK` row the smh twin lacked | `QD-C9-sr` |
| **C2 as a separate edit** | **SETTLED** — its premise was inverted by SCC-210/242: the story door now runs `check-actions` and `finish --landing-ref`, so the refusal claim is TRUE. Only the "nothing BEFORE the door checks it" half survived, and it is folded into C1's replacement | — |

### `cicd-self-audit.md` / `smh-self-audit.md` — 1 live, 4 settled

| ID | Disposition | Case |
|---|---|---|
| QD-C2 | APPLIED (partial: the sibling-lane binding, the epic ref, the `status` read) | `QD-C2-sa-a`–`QD-C2-sa-c` |
| **C1 C3a C4 C5** | **SETTLED** — SCC-225's approved rewrite deleted the Phase-2 tripwire list and the Light/Full ladder on **both** twins, the STOP-on-no-plan already exists at `:56-57`, and the constitution scan was deleted on both sides by name. Settled decisions, not gaps — re-adding them would reverse an approved plan | — |

### Rows that assert something must NOT change

`QD-pin1`, `QD-pin2` and `CR-pin` are preservation pins, correctly green in **both** states — the
`assert-partA.sh` A4 precedent. (`CR-pin` was re-aimed during the review: keyed on the bare word
`merge-tree` it also matched five command *names*, and deleting the whole of Step 0.7 left it PASS.)


## Evidence

### Acceptance row 1 — every finding applied or explicitly dismissed

`assert-scc212.py` carries one case per live finding, named by its backlog ID.

```
RED  @ origin/main : -- 3/115 passed --      (112 red; the 3 greens are preservation pins)
GREEN @ HEAD       : -- 115/115 passed --
```

⛔ **The two runs report the SAME number of rows, and that is a fix, not a coincidence.** Before the
review the six `FENCE … byte-identical` rows were guarded by `if both:` — so under `--red`, where no
fence exists yet, they did not fail: they **vanished**. The RED transcript read `3/103` while the
green one read `109/109`, and nothing said six checks had disappeared. A check that is absent looks
exactly like a check that passed. They now emit a failing row in the `else` arm (finding T5).

The three greens at `origin/main` are `QD-pin1`, `QD-pin2` and `CR-pin` — rows that assert something
must **not** change. They are correctly green in both states, the `assert-partA.sh` A4 precedent.

⛔ **Four rows were vacuous on the first RED run and were rewritten before any edit landed.** A case
that is green before its edit proves nothing, and all four were green for the same reason — they
matched text that already existed:

| Row | Matched instead | Now keyed on |
|---|---|---|
| `QD-C1/C2-cc` | the `tests-must-gate-for-real` §5 **pointer** at `:13`, which sits above Step 2 already | the scan **bullets** themselves, above the `## Step 2` heading |
| `QD-C2-cr` | the **false sentence** the finding replaces, which already said `check-actions` | `twice: its Step 2 runs` — the replacement's own claim |
| `FENCED_TODAY-*` | the `PAIRS` tuple thirty lines above | the `FENCED_TODAY` tuple, extracted by closing on a line-initial `)` |
| `MERGE-12` | `BARE \`key: status\` rows` at `:88` | `gate BARE` — the instruction |

### Acceptance row 2 — pointer AND inline obligation

Every hoisted rule landed as a pointer **plus** the restatement an agent following the literal step
list will actually read. `cicd-dev-story-tests` went from a **one-rule** block to eight, and each new
pointer has its inline half in a step body: the NO-GO read at Step 2, the RED-paste at Step 3, the
rung ladder at Step 3, the eject at Step 3.5, the mutation doctrine at Step 4, the backtick clause at
Step 4.5. `git-policy.md` carries the backtick law itself, so the pointer resolves to something.

### Acceptance row 3 — what was left different, and why

Left different on purpose, because the **subject** forces it (the parity guard's own docstring lists
these as legitimate): the merge target (`origin/epic/…` vs `origin/main`) · the spec source (story
file + certification vs `implementation_plan.md`) · the close-out verbs (`devrecord --story … --closing`
+ `finish --landing-ref` vs `finish`'s default) · the runners (pytest/vitest/emulators vs `run_all.py`)
· `PROJECT_ROOT` binding (a `cicd-*` command binds exactly one project and never the lobby) ·
`--story <id>` vs the branch slug · the preflight script (`closeout_preflight` vs `task_preflight`) ·
the Light/Full ladder and the Phase-2 tripwire list, **deleted on both twins** by SCC-225's approved
plan and deliberately not re-added.

The smh side was touched in **four files only**, and only where a shared law had to become
byte-identical or a genuine gap existed:

```
.agents/commands/smh-clean-code-audit.md          | 10 +-   (memory-sweep fence; wording aligned to the rule)
.agents/commands/smh-code-review.md               | 11 +-   (DEFERRED_WORK row; rederive-record fence)
.agents/commands/smh-merge-multiple-workingtrees.md |  6 +   (3 fence markers, no wording change)
.agents/commands/smh-quick-dev.md                 |  2 +    (2 fence markers, no wording change)
```

`test_twin_parity` block D prints **one** divergence, and it is pre-existing (`cicd-non-crit-pr-push`,
SCC-243). This lane declared none.

### Acceptance row 4 — the guard passes with the regions MARKED

**RED first, through the live gate.** With `memory-sweep` fenced on the cicd side only:

```
[FAIL] B cicd-clean-code-audit.md marks no law the twin lacks: ['memory-sweep'] marked in
       cicd-clean-code-audit.md and absent from smh-clean-code-audit.md - port it, or declare
       `<!-- twin-divergence: <id> — <reason> -->` in smh-clean-code-audit.md
-- 56/58 passed --
```

After porting to both sides: **64/64, exit 0.** Six new ids across four pairs — `memory-sweep`,
`review-runtime-probe`, `merge-empty-set-stop`, `merge-machinery-last`, `merge-cross-repo-order`,
`rederive-record` — and both new pairs joined `FENCED_TODAY`, so the scope stays a decision.

### Acceptance rows 5 & 6 — doors, gates, mutants

| Gate | Result |
|---|---|
| `gate_receipt.py run --task SCC-212 --gate suite` | **exit 0, 129.2s @ `6341cf79`** — receipt at `gates/suite.json` |
| `workflow_lint.py --toolkit-only` | **0 errors, 0 warnings, 8 info**, exit 0 |
| `test_command_surfaces.py` | **185/185**, exit 0 (after the sync — red before it, by construction; `CS-14` adds 8 durable rows) |
| `test_twin_parity.py` | **64/64**, exit 0 |
| `check_maps.py --depth3-only --strict` | exit 0 |
| `assert-scc212.py` | **115/115** at HEAD · **112 RED** at `origin/main`, same row count in both states |
| `mutation_sweep.py --table sweep.json` | **21/21 killed**, each by its declared case; restore verified against the pinned sha |
| `pwsh sync-agents.ps1` | exit 0 — 38 workflows, 23 launcher skills, 59 opencode commands |

**The suite's first stamp was RED, and that is the mechanism working.** `run_all.py` exit 1 @
`9c075986`: `test_check_maps` F2 reported `_artifacts/_main/INDEX.md: missing row for
2026-08-21_scc-212-twin-content-ports/`. That was plan step 1, owed and skipped. Row added, committed,
re-stamped on a clean tree → exit 0. The red receipt is left in the history where it belongs.

## Three things the build itself found

**1. `test_twin_parity` F11 assumed its fixture pair carried exactly ONE fence.** It deleted the
literal `<!-- twin-law: disposition -->` and asserted the computed set went **empty** — true only
while `cicd-clean-code-audit.md` had a single law. The moment this lane fenced `memory-sweep` into
that same pair, F11 went red with nothing actually wrong. It now strips **every** opener, so the row
tests what it claims (un-fencing a file drops it from B*'s computed set) and survives the tree
growing. The walkthrough for SCC-205 predicted this class of latency for E1; it landed on F11.

**2. The `LOADERS` mutation row loops over `LOADERS`.** M15 was originally declared as "remove the
file from `LOADERS` *and* drop the rule from its block" — and it **survived**, because emptying the
loop leaves the check with nothing to fail on. The scope pin beside it (`{…} <= set(LOADERS)`) is the
only thing that can catch a narrowing, and it named just the two smh files. It now names all three,
and M15 was re-aimed at the mutation that matters: deleting the loaded rule while the file stays
pinned. Caught by the self-audit before the build, verified by the sweep after it.

**3. Two of my own assertions were weaker than the findings they claim to hold** — found by the
sweep, not by reading:

- **M9 SURVIVED**: `MERGE-03b` matched `--expect-key` anywhere in the file. Striking it out of the
  preflight **invocation** left the prose explaining why it is required, and the row stayed green.
  The call is what an agent copies; the prose is what it skims. Now pinned to the call.
- **M13 SURVIVED**: `QD-C3-cr` matched the `Step 0.6 — Resolve the diff` **heading**. Deleting the
  `status --short` line *inside* that section left the row green. The heading is not the finding;
  `QD-C3-cr-b` now pins the uncommitted sweep itself.

Both are the SCC-144 lesson in miniature: a mutant drawn from the **code** finds what a mutant drawn
from your own cases cannot.

## Notes for whoever runs the sweep next

`mutation_sweep.py` validates its table with `not m.get(k)`, so an **empty `mutated` reads as
MISSING** and the whole table is refused — a pure deletion cannot be expressed. Deletions here are
spelled as a replacement with a neutral line that carries none of the law (`<!-- the fence that was
here is gone -->`). Worth knowing before writing a table full of deletions; recorded rather than
changed, because the validation is also what catches a genuinely malformed row.


## Code Review (2026-08-21)

Verdict: CONCERNS @ 448ba5cf

review-runtime: fan-out
lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok — truncated pass, declared: received 4 of ~35 files (the 20-file cap); named every withheld file
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none
findings:        0 decision · 25 patch · 0 defer   (0 noise-dismissed · 4 relevance kills)
dispositions:    per-lens: blind-hunter=7/0/1 · edge-case-hunter=8/0/1 · literal-correctness-hunter=3/0/0 · acceptance-auditor=5/0/1 · test-adequacy-auditor=6/0/1
severity_floor:  CONCERNS
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — two rows reconciled mid-lane (Amendment 1) and two more at the gate (Amendment 2: `jira.md` + `review-findings.md`)
notes:           `FINDINGS_SINK` was absent, so the full triage was written to [review-findings.md](review-findings.md) rather than returned inline; every finding was reproduced by execution, not inferred.

### Step 0.7 — re-derivation

1. **What moved:** nothing. `origin/main` **is** the merge-base at `295abe5` — no sibling lane has
   landed since this branch was cut, so the diff is `295abe5...HEAD` with nothing to absorb, and
   every path and `#L` anchor this diff names still resolves.
2. **What that changes for this lane:** nothing has to be re-measured, so the gates below stand at
   the shipping sha rather than at a pre-merge one; the verdict is about code that will exist.
3. **Sibling lanes live:** none. `git worktree list` shows this tree alone, so there is no
   landing-order dependency to declare.

### The verdict, and why it is CONCERNS and not PASS

**Every confirmed finding was fixed in this lane, before this line was written** — that is the
`/smh-code-review` contract, and 25 of 25 are applied. What CONCERNS records is not unfinished work;
it is that a review this size *found* 25 real defects in work that had already passed a self-audit,
a RED→GREEN pass and a clean mutation sweep. The number is the signal.

**The distribution is the finding worth carrying forward.** The lenses found almost nothing wrong
with the 55 ports themselves: the Acceptance Auditor confirmed every claimed-applied ID is present
in the diff, and all six fences are byte-identical on both sides. **The defects clustered in the
machinery this lane wrote *to prove* the ports** — my new bash blocks, my assertion script, and my
own fix to the parity guard. The ported content was held to the bar; the scaffolding was not.

Three of them are worth naming here, because each is a gate that would have reported success:

- **The kickoff's three new commit blocks could not run.** `printf … > epic-commit-msg.txt` writes
  to the shell's cwd; `git -C "$PROJECT_ROOT" commit -F <relative>` reads it under `PROJECT_ROOT`.
  `fatal: could not read log file`, exit 128 — and the push on the very next line then reported
  success over a commit that never happened. Reproduced three times independently, in a scratch
  repo. Now `mktemp`, outside both trees.
- **My own fix to `test_twin_parity` F11 was vacuous by construction.** F11 must prove that
  un-fencing a file changes the computed set. My fix stripped *every* opener with `LAW_OPEN.sub("",
  t)` — the same regex `law_map()` iterates — so the map is empty for **any** input, including a
  file that never carried a fence. The row re-asserted the bare truthiness its own comment condemns,
  and would have stayed green if `laws()` stopped working entirely. It now removes ONE opener and
  asserts a strict subset: sensitivity that holds at one law and at ten.
- **Six of my assertion rows were ABSENT under `--red`, not red.** The `FENCE … byte-identical`
  rows sat behind `if both:`, so in the pre-edit state — where no fence exists — they simply did
  not run. The RED transcript read `3/103` against a green `109/109` and nothing said six checks had
  disappeared. A check that vanishes is indistinguishable from a check that passed.

**Four findings were relevance-killed, with the reason recorded** in
[review-findings.md](review-findings.md): two pointers that displaced no obligation (acceptance row
2's trigger is a Part E *hoist*, and neither is one), one true-but-duplicated sentence subsumed by
the fix beside it, and one pre-existing hardcode that is not in this diff. `code-standards` §6.5:
all three questions YES, or it is not acted on.

### What the fix pass cost, measured

| | Before the review | After |
|---|---|---|
| `assert-scc212.py` | 109 rows · **103** under `--red` | **115** rows in **both** states |
| `mutation_sweep.py` | 15 declared, 15 killed | **21** declared, **21** killed (M20 SURVIVED once — see below) |
| `test_command_surfaces.py` | 177 | **185** — `CS-14` promotes 8 lane-local pins into the durable suite |
| Durable protection when this folder is archived | 6 fences + 1 `LOADERS` entry | 6 fences + 1 `LOADERS` entry + **8 `CS-14` rows** |

⛔ **M20 SURVIVED the first re-sweep, and it is the same lesson a third time.** `CS-14 C` asserted
`--require-gates` was somewhere in the merge door's file — and the paragraph explaining *why the flag
is required* contains the flag, so striking it out of the invocation left the row green. It now
resolves the `closeout_preflight.py` call across its `\` continuations and looks only there.
`MERGE-03b`, `QD-C3-cr` and now `CS-14 C`: **the call is what an agent copies; the prose is what it
skims**, and only a mutant drawn from the code ever finds the difference.


## Your Actions

- [x] Plan, edit-spec, walkthrough, manifest, receipt and sweep table are linked at the top of this
      document; the INDEX row is filed.
- [x] The three Antigravity mirrors that flipped to thin launchers
      (`cicd-merge-epic-workingtrees`, `cicd-clean-code-audit`, `cicd-create-epic-sprint`) are the
      designed mechanism at the 11,500-byte threshold, not a regression — the command file is still
      the brain and the launcher points at it.

- [x] The review gate ran and its 25 findings were fixed **in this lane, before the verdict** — the
      `/smh-code-review` contract. Nothing was minted, nothing was deferred, nothing was left as a
      note for later. `## Code Review` says why the verdict is CONCERNS with every finding closed.

**Nothing is owed.** The lane is committed and pushed; the door is `/smh-close-task-merge-tree`, and
invoking it is the sign-off.
