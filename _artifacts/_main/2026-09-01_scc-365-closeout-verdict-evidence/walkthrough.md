# SCC-365 — Close-out accepts a `Verdict: PASS` that no suite ever backed

**Lane:** `chore/SCC-365-closeout-verdict-evidence` · worktree `.claude/worktrees/scc365-closeout-verdict`
**Plan:** [implementation_plan.md](implementation_plan.md) (with the two-round Self-Audit)
**Ticket:** SCC-365 (Task, one lane, no subtasks)

---

## What was broken, in one paragraph

A story could close carrying `Verdict: PASS` that no test suite ever backed — what happened on
AVCH-106, where a walkthrough asserting its own PASS was committed and closed while the standing
suite was RED. Four things had to be true at once for that to get through, and all four were:
`check_artifacts` read the verdict and never asked it for evidence; the receipt check was OFF unless
a caller remembered `--require-gates`, which two of the four doors omit and a third showed in
brackets; a receipt that was never written only WARNed, under a 2026-08-02 ruling that kept the gate
"advisory for one sprint" and was never revisited; and the step that actually decides the `done` flip
carried its own copy of that expired ruling plus the sentence *"Fail-open: a gate-read error never
blocks close-out"* — so an error raised at Step 0.6 was overruled by prose at Step 4, the story
flipped to `done`, and the flip then made it permanently exempt from every later re-run.

## The design call

The ticket asked for "a default for `--require-gates`". The obvious reading — hardcode `"suite"` —
would have refused every already-`done` story `/cicd-prune-worktree` runs on, whose lanes are pruned
and whose only remedy ("re-run the suite") nobody can perform. This file documents that failure mode
twice: **a gate whose refusal has no reachable fix is a gate that gets disarmed.**

So the demand is **derived from the claim, not hardcoded**. A `PASS`/`CONCERNS` *is* a claim that a
gate was green, so `suite` becomes required — and only while the story is still flip-eligible, where
the remedy is one command away. `FAIL`, `WAIVED` and a walkthrough with no verdict demand nothing,
matching what `verdict_receipt.py` (SCC-363) gates at commit time. The house's usual escape hatch —
a dated cutoff — is **inert here**: `roster.lane_date` reads a `YYYY-MM-DD` prefix off the artifact
folder and story lanes do not carry one, so a cutoff would exempt everything or block everything. The
limiter is `0 < wf.STATUS_RANK.get(status, -1) < wf.STATUS_RANK["done"]`, which is exactly the set
`/cicd-update-sprint-memory` already advances — no second vocabulary to keep in sync.

## Two more the audit found and this lane closed

**The same story blocked or passed by SPELLING.** `main()` handed `check_gates` the raw `--story`
while every other check got the resolved board key, and `gr.receipt_dir` keys off that raw string.
Reproduced live on AviationChat: `--story 23-9` → `suite: STALE - passed at 808dce60`;
`--story 23-9-flight-status-drawer-polish-active-curriculum` → `suite: no receipt`. Same tree, same
story. Harmless while it was a WARN; a **blocking false refusal** once promoted — and the long form
is reachable, because `/cicd-prune-worktree` Step 0.2 resolves a long slug before Step 0.3 asks for
"the id". `receipt_dir_for` now resolves literal-first, then `wf.slug_matches` over what is on disk,
and only when it picks exactly one.

**Both landing doors demanded receipts nothing writes.** `--require-gates suite,ruff,pyrefly`, when
the review step stamps `suite` and nothing else (`cicd-code-review.md:356`) and 9 of the 10 live AGY
receipt dirs hold `suite.json` alone. Promoting a missing receipt to an ERROR would have hard-blocked
**every** close-out on two receipts no step in this system has ever written. Both doors now ask for
`suite`.

## Blast radius, measured not inferred

Run against the live AviationChat tree with the new script: all four stories carrying receipts
(`23-9`, `23-10`, `23-13`, `19-1`) are `done` and correctly draw **no gate row at all**. The three
flip-eligible rows on that board (`12-3-igor-full-checkride`, `12-3-4-checkride-frontend`,
`12-3-7-checkride-report-split`) carry no walkthrough verdict, so **no new error fires anywhere on
the live board.** The `STALE` path is pre-existing and unchanged — it fires today with the flag the
merge door already passes mandatorily.

---

## Acceptance

| | Statement | Assertion that proves it | Result |
|---|---|---|---|
| **A** | Flip-eligible + `PASS` + no receipt → exit 2 with `--require-gates` omitted | `EV1` | ✅ |
| **B** | Same + usable receipt → no `gates` ERROR; AVCH-106 replay refused on the VERDICT LINE | `EV2`, `EV6` | ✅ |
| **C** | `done` **and** `deferred` + `PASS` + no receipt → no new error | `EV3` (both statuses) | ✅ |
| **D** | `FAIL`, `WAIVED` and no-verdict acquire no receipt demand | `EV4` (three controls) | ✅ |
| **E** | Explicit `--require-gates <g>` missing → **one** ERROR naming the directory searched and the `gate_receipt.py run` remedy | `EV5` | ✅ |
| **F** | Both doors carry `--require-gates suite` unbracketed and neither demands `ruff`/`pyrefly`; the flip step carries no `--advisory` and no fail-open | `CS-14 C2`, `CS-14 C3` | ✅ |
| **G** | Long board key resolves the same receipt as the short id, and with both on disk the story's own key wins | `EV7`, `EV8` | ✅ |

**Declared change set reconciliation:** 13 declared, all landed. Three files edited beyond the
declared set, each named here: `_artifacts/_main/INDEX.md` (the row this lane owes —
`test_check_maps.py` F2 caught its absence in the first receipt-stamped suite run),
`docs/_scc_sops_prds/workflows_testing_SOP_changelog.md` (required by `sop-currency.md` habit 4 in
the same commit as the SOP edit), and `_artifacts/_memory/workflow-enforcement-scripts.md` (declared
in plan step 9, written through the sanctioned Claude harness flow and carried onto the lane by
`AGENTS.md` §7's four-step procedure — the shared checkout was restored and SCC-358's two in-flight
memory files were left untouched).

## RED first

Ten new cases written and run against the **unmodified** script and doors:

```
[FAIL] EV2  rc=1 gates=[] verdict='VERDICT: clear to close out'
[FAIL] EV1  rc=1 gates=[] verdict='VERDICT: clear to close out'
[FAIL] EV6  VERDICT: clear to close out
[FAIL] EV5  rc=1 gates=['suite: no receipt (gate_receipt.py run ...)']
[PASS] EV3  done      · CONTROL
[PASS] EV3  deferred  · CONTROL
[PASS] EV4  no Verdict line / FAIL / WAIVED · CONTROLS
[FAIL] EV7  short=['suite: pass @ 4b48e0d1'] long=['suite: no receipt (gate_receipt.py run ...)']
-- 5/10 passed --
```

```
[FAIL] CS-14 C2  merge door: '--require-gates suite,ruff,pyrefly' | close door: '[--require-gates suite,ruff,pyrefly]'
```

Each red is an assertion failure with measured detail, not a setup crash — `EV1`/`EV6` show the
literal AVCH-106 outcome (`clear to close out` over a suite that never ran) and `EV7` shows the
spelling bug reproduced in a fixture.

**Five pre-existing cases were re-based deliberately, exactly as the pre-work audit predicted, and no
sixth:** `FR0` (:751), `FR2` (:764), `FR5` (:794), `FR6` (:828) and `MEM3` (:879). The shared
`lane_repo` fixture *was* the blocked shape — board `30-1-fresh: review`, `**Verdict: PASS**`, no
receipt — so those rows started reading `BLOCKED` where they exist to read freshness and memory
classification. The re-base gives the fixture its own receipt rather than weakening any assertion.
`ev_repo`, written first as a second builder, was **folded back into `lane_repo`** as three
defaulted knobs rather than shipped as a near-duplicate.

⚠ **One fixture device worth knowing:** the receipt is `.gitignore`d in `lane_repo`. A receipt records
the commit it ran on, and committing it moves HEAD past that commit, after which `check_receipt`
compares trees and correctly says STALE — so a fixture that commits its receipt cannot show a clean
one. Staleness policy is a different question from "was there any evidence at all", which is what
these rows measure.

## Mutation sweep — 9/9 killed by their declared case

Table declared before mutating, every mutant drawn **from the code**, run as one sweep through
[`mutation_sweep.py`](../../../.agents/scripts/mutation_sweep.py) — table at [sweep.json](sweep.json).

| Mutant | File | Killed by |
|---|---|---|
| M1 missing-receipt row back to a WARN (the expired ruling) | `closeout_preflight.py` | `EV1` |
| M2 **width** · claim set swallows `FAIL`/`WAIVED` | `closeout_preflight.py` | `EV4` |
| M3 **width** · flip-eligible LOWER bound drops (parked lanes demanded) | `closeout_preflight.py` | `EV3` |
| M4 **width** · flip-eligible UPPER bound opens (`done` demanded, prune blocks) | `closeout_preflight.py` | `EV3` |
| M5 dedupe guard removed (same error filed twice) | `closeout_preflight.py` | `EV5` |
| M6 receipt directory never resolved against disk | `closeout_preflight.py` | `EV7` |
| M7 `check_gates` takes the raw `--story` again | `closeout_preflight.py` | `EV8` |
| M8 close door shows the flag optional again | `cicd-close-story-merge-tree.md` | `CS-14 C2` |
| M9 flip step runs the receipt check advisory again | `cicd-update-sprint-memory.md` | `CS-14 C3` |

```
-- restore verified: bytes match, nothing was committed, and `git diff --quiet 94099588` is clean --
-- full file, unfiltered: test_closeout_preflight.py -> exit 0 -- 80/80 passed --
-- full file, unfiltered: test_command_surfaces.py  -> exit 0 -- 276/276 passed --
-- sweep clean: 9/9 killed by their declared case --
```

⭐ **The sweep earned its keep before it ran.** Building the table exposed that `M5` would have
SURVIVED — nothing asserted the missing-receipt error appears exactly once, so a doubled prepend was
invisible — and that `M7` would have survived too, because `receipt_dir_for` alone makes `EV7` green
from either spelling. `EV5` was tightened to `len(errs) == 1` and `EV8` was added, **before** the
sweep, so neither is a test written to its answer. `CS-14 C3` was added for the same reason: the
Gap-4 prose deletion had nothing holding it, and a prose deletion nothing pins is how the 2026-08-02
ruling outlived its own sprint in the first place.

## Gates

| Gate | Result |
|---|---|
| `run_all.py` (full enforcement suite) | **68/68 files** · exit 0 |
| `test_closeout_preflight.py` | **80/80** (baseline 69) |
| `test_command_surfaces.py` | **276/276** (baseline 274) |
| `workflow_lint.py --toolkit-only` | exit 0 · 0 errors, 0 warnings, 8 info |
| Door parity (`diff -q` brain vs `.opencode`) | silent on all three edited doors |
| Suite receipt | `result=pass`, `dirty_tree=false` |
| Mutation sweep | 9/9 killed, restore byte-verified |

## Files

| File | Why |
|---|---|
| [`closeout_preflight.py`](../../../.agents/scripts/closeout_preflight.py) | `receipt_dir_for`, `require_evidence_gate`, `check_gates` err-not-warn, `check_artifacts` returns its verdicts, `main` passes the resolved key, docstring usage line |
| [`test_closeout_preflight.py`](../../../.agents/scripts/tests/test_closeout_preflight.py) | `EV1`–`EV8`, `lane_repo` folded + knobbed, five cases re-based |
| [`test_command_surfaces.py`](../../../.agents/scripts/tests/test_command_surfaces.py) | `CS-14 C2` (both doors' resolved calls), `CS-14 C3` (the flip step's prose) |
| [`cicd-close-story-merge-tree.md`](../../../.agents/commands/cicd-close-story-merge-tree.md) | flag unbracketed + narrowed, `# PC: \`python\`` added |
| [`cicd-merge-epic-workingtrees.md`](../../../.agents/commands/cicd-merge-epic-workingtrees.md) | narrowed to `suite` |
| [`cicd-update-sprint-memory.md`](../../../.agents/commands/cicd-update-sprint-memory.md) | `--advisory`, the ⏳ line and the fail-open clause retired |
| `.opencode/commands/` ×3 | byte-identical mirrors CS-03 compares |
| [`workflows_testing_SOP.md`](../../../docs/_scc_sops_prds/workflows_testing_SOP.md) + changelog | the operator-facing row and its one-line change record |
| [`workflow-enforcement-scripts.md`](../../_memory/workflow-enforcement-scripts.md) | the ⏳ flip this lane discharged |

## Your Actions

- [x] The merge itself — lands via this branch's PR.

Nothing else is owed.

---

review-runtime: inline (blocked: operator capped this lane mid-flight — *"You have 4 minutes and im pulling this"* — so no subagent fan-out was authorized; the lenses were run inline by the builder on the diff)

## Code Review (2026-09-01)

lenses_run:
- blind-hunter · recovered-inline
- acceptance-auditor · recovered-inline
- parity-blast · recovered-inline
- pre-mortem · recovered-inline

**Level:** quick — the re-derived radius came back contained: the only overlap with what landed on
`main` while this was built is `_artifacts/_main/INDEX.md`, a planning surface, resolved by keeping
both lanes' rows; nothing this diff references moved; `risk_seam.py classify` returns `unclassified`,
which is the permanent correct answer for the command centre (SCC-289).

**Findings, and their disposition under `code-standards.md` §6.5.** Three were assessed real and all
three were fixed **in thread, before the sweep**: the un-deduplicated error row (`EV5` tightened), the
unpinned half of the id fix (`EV8` added), and the unguarded Gap-4 prose deletion (`CS-14 C3` added).
Nothing else survived the three-question test. No ticket was minted; nothing was deferred.

**One thing raised once, with its remedy, because it is genuinely outside this lane's subject.** A
receipt committed to the lane necessarily records the commit *before* its own commit, so
`check_receipt`'s tree comparison reports `STALE` on essentially every real close-out — measured live
on `23-9`, `23-13` and `19-1`. That is pre-existing, unchanged by this lane, and already blocking at
the merge door today. Remedy: exempt `_artifacts/` from the tree comparison, the way `task_preflight`
already does. It belongs on the open rolling ticket, not here.

**Verdict: PASS @ 0c5a344e**
