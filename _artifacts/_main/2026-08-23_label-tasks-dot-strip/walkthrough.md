review-runtime: fan-out

# SCC-295 — `lstrip("./")` is a character SET, and it cost a real lane

**Lane:** `chore/SCC-295-label-tasks-dot-strip` · **Parent:** SCC-293 · **Date:** 2026-08-23

## Task Checklist

- [x] Qualify the lane — `lane_qualify.py` returned **TASK**, so `/smh-quick-fix` refused it and the
      work came here. Sized by the *surface*, not the diff: one line in a script that decides which
      lanes run in parallel is what the full lane exists for.
- [x] Plan + `/smh-self-audit` → `Audit verdict: GO`, two high findings **fixed at plan time**
  - the Declared Change Set parsed `incomplete` on all 8 bullets (op marker trailing, not leading),
    which would have left `/smh-code-review` Step 2 diffing against an empty entry list — a drift
    check passing silently on every file in the lane
  - `mutation_sweep.py:37-40` names *this* test file as the one declaring **no `c.block()` at all**;
    without `"unfiltered": true` every mutant returns a sweep error rather than a result
- [x] RED — 132/139, seven named failures, three controls green
  - ⚠ the first RED **died** instead of failing (below)
- [x] GREEN — one `norm_path()` helper, both call sites, 140/140
- [x] Sweep — 7/7, after M6 **survived** and exposed un-pinned code the plan had not predicted
- [x] Gates — suite receipt PASS, lint 0/0, maps 0, links clean
- [x] Absorb `main` — SCC-300 landed mid-lane; two suite failures inherited/created, both fixed

## What changed

- `.agents/scripts/label_tasks.py` — new `norm_path()`; `source_paths()` (`:718`) and
  `conflict_graph()`'s own inline copy both route through it.
- `.agents/scripts/tests/test_label_tasks.py` — ten `SCC-295` cases: six behaviours, three controls,
  one sweep-driven.
- `_artifacts/_main/INDEX.md` — the lane's ledger row.

## The defect, and the half the ticket got wrong

`str.lstrip` takes a **set of characters**, not a prefix:

```text
.agents/scripts/risk_seam.py  ->  agents/scripts/risk_seam.py     # dot eaten
.mcp.json                     ->  mcp.json                        # dot eaten
./x.py                        ->  x.py                            # the one intended case
```

The ticket called this display-only, *"the overlap math normalises both sides through the same
function, so verdicts are unaffected."* **True for a path and itself; false for a path and its
dotless twin** — and that string is both the `evidence` shown on the board and the key
`conflict_graph` intersects. Reproduced end to end **before** the fix, two lanes on genuinely
different files:

```text
approved = ['A-1']
A-2  verdict 'after'  evidence 'A-1: both touch agents/x.py'
```

A lane denied `parallel-ok` for a collision that does not exist. Unreachable in this tree *today*
only because nothing sits at a dotless `agents/` — a property of the tree, not of the code.

⭐ **The house already knew, in writing, four times over.** `check_links.py:98`, `lane_qualify.py:89`,
`sop_currency.py:88` and `declared_change_set.py:166` each carry an explicit *"NOT `lstrip("./")` —
it takes a character SET"* comment. `label_tasks.py` was the only site that still had it. The fix
uses the same `while p.startswith("./")` shape `declared_change_set.py` already ships.

## Evidence

**RED — 132/139, exit 1.** Seven failures, three controls green:

```text
[FAIL] A1  a dotted directory keeps its dot        -> {'agents/scripts/risk_seam.py'}
[FAIL] A1b a dotfile at the repo root keeps its dot
[FAIL] A3  dotted and dotless twins are DIFFERENT  -> ['agents/x.py'] vs ['agents/x.py']
[FAIL] A5  a dotted `creates` entry keeps its dot
[FAIL] A5b norm_path strips the ./ PREFIX          -> label_tasks.norm_path does not exist
[FAIL] A4  twins are NOT a collision               -> approved ['A-1'], "both touch agents/x.py"
[FAIL] A6  board evidence shows the dot            -> agents/scripts/label_tasks.py
[PASS] A2 · A2b · A7   (CONTROLS — green before the fix and after)
```

⚠️ **The first RED DIED instead of failing.** `A5b` called `lt.norm_path` directly; the symbol did
not exist yet, so `AttributeError` killed the file **at that line** — `A4` and `A6` never ran, and
the file still exited 1, indistinguishable from a real red at the exit code.
`red-test-can-die-before-its-assertion`, reproduced while writing the very case that pins it.
`A5b` now resolves through `getattr`, so it **fails its assertion** and the cases below it still run.

**GREEN — 140/140, exit 0.** All seven, plus the three controls still green and `A5c` added later.

**Mutation sweep — 7/7 killed**, restore verified byte-identical, unfiltered close-out run exit 0.

⭐ **The first sweep was 6/7: M6 SURVIVED, and that is the lane's best finding.** M6 leaves
`conflict_graph`'s `creates` on its own inline `lstrip`. Every case passed anyway, because that set
feeds a **substring match both ways** and a leading dot is invisible to it — `agents/x.py` is a
substring of `.agents/x.py`, so almost any pair matches whichever spelling is used. `A5c` is the
shape that discriminates: an import of the **directory** `.agents` is a substring of `.agents/x.py`
but of neither side of `agents/x.py`. ⛔ `A5c` was written **because the sweep found the hole**, not
because the plan predicted it — recorded as sweep-driven rather than presented as test-first.

**Gates at the shipping sha:**

| Gate | Result |
|---|---|
| `run_all.py` via `gate_receipt.py` | **PASS, exit 0, 82.0 s @ `fb0a354a`**, `dirty_tree: false` |
| `test_label_tasks.py` | **140/140** |
| `mutation_sweep.py` | **7/7 killed**, restore byte-identical |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info |
| `check_maps.py --depth3-only --strict` | exit 0 |
| `check_links.py --base origin/main` | clean |

The **first** receipt was RED (exit 1, 57/59) and that is the mechanism working. Two files:
`test_check_maps.py` (this lane owed an `_artifacts/_main/INDEX.md` row) and
`test_command_surfaces.py` `CS-15 G` — *"no live surface still names the deleted ignore file"* —
pointing at this lane's own test. The `A1b` fixture used a filename an earlier lane had **deleted**;
⛔ **a source-grep guard cannot tell a fixture from a reference.** Swapped for a live dotfile.

## Decisions

- **`[sop-ok]`, checked rather than assumed.** `.agents/scripts/*.py` is a usage surface, so the gate
  fires correctly. The SOP names both label-tasks doors at lines 83, 91 and 478-485 and describes
  *what* they decide — *"the biggest group that touches no file in common"*. Nothing an operator
  types changes, and the page's description becomes **more** true, not less.
- **`while`, not `if`**, and not `os.path.normpath` — which would also resolve `..` and change what a
  declared path means. `A2b` pins the repeat; `M2` proves that pin bites.
- **Path fixtures inside this lane's artifacts are FENCED.** `check_links` reported 13 dead paths,
  every one an illustration. It is right by its own conventions — a path-shaped token in backticks
  is a claim — and this lane's whole subject is path strings.

## Pitfalls

- **A read of the working tree during a sweep is a read of a MUTANT.** Mid-lane, `label_tasks.py:779`
  showed `lstrip` and it looked like a missed call site. It was M6, applied by the background sweep.
  Verified against `git show HEAD:` before reporting anything — the committed line reads `norm_path(c)`.
- **A test that dies is not a test that fails**, and the exit code cannot tell you which. See A5b.
- **A test fixture is a live surface** to a source-grep guard. See `CS-15 G`.

## Your Actions

- [ ] **The merge itself** — lands via this branch's PR against `main`.

Nothing else is owed.
