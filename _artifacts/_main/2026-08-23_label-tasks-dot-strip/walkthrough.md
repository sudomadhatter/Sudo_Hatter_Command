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
- `.agents/scripts/tests/test_label_tasks.py` — **fifteen** `SCC-295` cases: seven behaviours,
  three controls, one sweep-driven, and **four regression guards the code review forced** (A8-A10).
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
feeds a **substring match both ways** and a leading dot is invisible to it:

```text
"agents/x.py" in ".agents/x.py"   ->  True    # so almost any pair matches either spelling
".agents"     in ".agents/x.py"   ->  True    # A5c: an import of the DIRECTORY
".agents"     in "agents/x.py"    ->  False   # ...matches neither side of the dotless twin
"agents/x.py" in ".agents"        ->  False
```

`A5c` is that discriminating shape. ⛔ It was written **because the sweep found the hole**, not
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

## Code Review (2026-08-23)

Verdict: CONCERNS @ fcce5e9
Suite evidence re-stamped at the landing sha — see the gate table below.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

dispositions:    per-lens: blind=4/1/0 · edge=2/0/0 · literal=4/0/0 · acceptance=3/1/0 · test-adequacy=1/4/0 (a multi-lens finding counts once per contributing lens; the leading-slash regression was reached by three lenses independently and is merged into F1 below)
drift:           undeclared=0 · unimplemented=0 · incomplete=0 — `declared_change_set.py diff` against the real diff, 8 declared, 8 changed

**Scope:** `origin/main...HEAD`, 8 files (2 source, 6 artifacts). **Method:** `review_level: standard`,
`review_runtime: fan-out`, `lens_budget: standard`. Five lenses in parallel; the Blind Hunter was fed
the diff text and never opened the repo.

### Why CONCERNS and not PASS

**The review found a regression the builder introduced, and the builder's own gates were green over
it.** RED-first, a 7-mutant sweep and 140 passing cases all passed a change that made the labeller
fail in the direction its own source calls unacceptable. Three of the four defects below are mine,
written after the plan was approved and the audit said GO. A PASS would claim the process caught its
own work. It did not.

### Findings

| # | file | severity | failure scenario | disposition |
|---|---|---|---|---|
| F1 | `label_tasks.py` `norm_path` (blind ×2, edge, literal) | **critical** | `lstrip("./")` also stripped a leading `/`. The prefix-only replacement did not, so `/src/a.py` and `src/a.py` — the SAME file, two spellings — stopped intersecting and **both lanes were stamped `parallel-ok` and dispatched to edit one file**. ⛔ Direction matters: `cmd_resolve` states *"a false green puts two lanes on the same line, a false lock costs only serialisation."* The original bug erred safe; this regression erred unsafe. Reproduced by three lenses independently. | **applied @ `bf5bccd`** — fixed-point loop stripping `./`, any leading `/`, and whitespace each pass; `A8`/`A8b`/`A8c` pin all three shapes, `A8d` is the control that the dot still survives |
| F2 | `label_tasks.py` `source_paths` (edge, literal) | **important** | Same root: `PLANNING_PREFIXES` is tested **after** normalisation, so a surviving `/` made `/_artifacts/plan.md` read as a real source path. Every planned lane writes under `_artifacts/`, so two lanes would collide over their own planning files. | **applied @ `bf5bccd`** — `A9` |
| F3 | `label_tasks.py` `conflict_graph` (blind, edge, literal) | **important** | `norm_path("./")` is `""`, and `"" in s` is True for **every** import string, so one empty `creates` entry locked its lane against every other and printed an invented reason onto the board. `source_paths` filtered empties six lines above; this copy never did. | **applied @ `bf5bccd`** — `A10` |
| F4 | `test_label_tasks.py` (test-adequacy) | **important** | A mutant survived all 146 cases: `lstrip("./")` **inside** the prefix branch. Observable on exactly one shape — `./` in front of a dotted path — where both halves of the bug meet. Every fixture missed it: `./x.py` has no dot to eat, `.agents/x.py` has no prefix to strip. Under it the whole SCC-295 defect returns. | **applied @ `fcce5e9`** — `A11` + sweep `M9` |
| F5 | walkthrough gate table (acceptance) | **important** | The table claimed `check_links … clean`. Measured while the walkthrough was still **untracked**, so it was not in the scanned set; the real answer at HEAD was **4 dead paths**. A gate result recorded before the file it measured existed. | **applied @ `2196217`** — fenced; re-run scans 3 files / 20 claims, exit 0 |
| F6 | `label_tasks.py` docstring + test comments (literal) | suggestion | The docstring cited **`verdicts_for`, a function that exists nowhere in the repo**; and all five line-number references were stale — this diff shifted them 21 lines, so `:757`/`:758` landed inside `blocked_by_of`. | **applied @ `9fea6d1`** — numbers removed entirely, functions named instead |
| — | sweep `M4` (`s[2:]`→`s[1:]`) | — | **Not a finding — an EQUIVALENT mutant.** `startswith("./")` guarantees `s[1] == "/"`, which the next line's `lstrip("/")` removes, so the two are the same function. Proven over 14 inputs, 0 differ. Re-aimed to `s[3:]`, which is observable. ⛔ A sweep cannot tell an equivalent mutant from a test gap. | **re-aimed @ `9fea6d1`** |
| — | uppercase keys · `../` · tab whitespace · trailing slash · `str()` coercion · `imports` normalisation (test-adequacy ×5) | suggestion | **dismissed — no reproduced failure.** Each is a surviving mutant with no concrete input/state/wrong-output chain, on behaviour identical before and after this diff. Recorded rather than chased: the engine's own rule is that a lens always returns findings and treating them as a work queue is how a lane never closes. | dismissed |

### Step 0.7 — re-derivation

1. **Nothing this diff references moved.** Re-derived against `origin/main` after absorbing it: the lane is 0 behind, and the merge-base diff of what landed while building is **0 files**. Earlier in the lane SCC-299 and SCC-300 both landed and were absorbed at `57f347d`.
2. **True overlap is empty and the merge is clean.** `grep -Fxf mine theirs` → no shared paths; `merge-tree --write-tree` returned a tree sha with no conflict messages.
3. **One sibling lane is live and it is a ledger dependency only.** `claude/teaching-edition` (SCC-280, 40 files) shares `_artifacts/_main/INDEX.md`. Either order lands; whichever is second absorbs `main` and keeps both rows. No code overlap.

### Gates

| Gate | Result |
|---|---|
| `tests/test_label_tasks.py` | **147/147, exit 0** |
| `tests/run_all.py` via `gate_receipt.py` | re-stamped at the landing sha — see `gates/suite.json` |
| `mutation_sweep.py` | 8/8 killed on the 8-mutant table; `M9` added with `A11` and re-run at the landing sha |
| `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info |
| `check_maps.py --depth3-only --strict` | exit 0 |
| `check_links.py --base origin/main` | clean — 3 files, 20 claims |
| `declared_change_set.py diff` | undeclared 0 · unimplemented 0 · incomplete 0 |

### Process findings — bigger than this ticket

- ⛔ **`code-review-engine` runs its lenses in the builder's own worktree.** Three of the five wrote
  to `label_tasks.py` while this lane was editing it. One produced a RED run reporting `'rc/a.py'` —
  arithmetic no version of this code performs — which was a mutant being measured as if it were the
  build. It was caught only because the number was impossible. The Agent tool has
  `isolation: "worktree"`; the engine does not use it. **A review that can edit the code under
  review is not a review.**
- ⛔ **`lane_qualify.py` sizes by path prefix, not blast radius.** Anything under `.agents/scripts/`
  returns `TASK`. Ten lines and a 24-file door rewrite are indistinguishable to it, and there is no
  lane between "no ceremony" and "all of it". This ticket was typed as `/smh-quick-fix` and ran the
  heaviest process in the system.

## Your Actions

- [ ] **The merge itself** — lands via this branch's PR against `main`.

Nothing else is owed.
