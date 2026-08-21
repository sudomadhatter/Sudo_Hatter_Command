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
**55 were live and 11 were already settled** — by SCC-205 Part C, SCC-211, or SCC-225's approved
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
- [x] Mutation sweep — **two survivors were real**, fixed, re-swept to 15/15

## Evidence

### Acceptance row 1 — every finding applied or explicitly dismissed

`assert-scc212.py` carries one case per live finding, named by its backlog ID.

```
RED  @ origin/main : -- 3/102 passed --      (99 red; the 3 greens are preservation pins)
GREEN @ HEAD       : -- 109/109 passed --
```

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
| `test_command_surfaces.py` | **177/177**, exit 0 (after the sync — red before it, by construction) |
| `test_twin_parity.py` | **64/64**, exit 0 |
| `check_maps.py --depth3-only --strict` | exit 0 |
| `assert-scc212.py` | **109/109** at HEAD · **99 RED** at `origin/main` |
| `mutation_sweep.py --table sweep.json` | **15/15 killed**, each by its declared case; restore verified against the pinned sha |
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

## Your Actions

- [x] Plan, edit-spec, walkthrough, manifest, receipt and sweep table are linked at the top of this
      document; the INDEX row is filed.
- [x] The three Antigravity mirrors that flipped to thin launchers
      (`cicd-merge-epic-workingtrees`, `cicd-clean-code-audit`, `cicd-create-epic-sprint`) are the
      designed mechanism at the 11,500-byte threshold, not a regression — the command file is still
      the brain and the launcher points at it.

**Nothing is owed.** The lane is committed and pushed; the door is `/smh-close-task-merge-tree`, and
invoking it is the sign-off.
