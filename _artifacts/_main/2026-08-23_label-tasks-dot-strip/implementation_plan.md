# SCC-295 — `lstrip("./")` is a character set, not a prefix

**Lane:** `chore/SCC-295-label-tasks-dot-strip` · **Repo:** Sudo_Hatter_Command · **Date:** 2026-08-23
**Parent:** SCC-293 · **Type:** Subtask · **review-runtime:** fan-out

## The defect

`label_tasks.py` normalises every declared touch-set path through:

```python
p = str(p).strip().lstrip("./")          # :718, and again inline at :758 for `creates`
```

`str.lstrip` takes a **set of characters**. It was written to strip a leading `./`; it also eats
the leading dot off every hidden path. Measured — fenced, because these are path-shaped DATA and a
link checker cannot tell an illustration from a reference:

```text
.agents/scripts/risk_seam.py   ->  agents/scripts/risk_seam.py      # dot eaten
.mcp.json                      ->  mcp.json                         # dot eaten
.gitignore                     ->  gitignore                        # dot eaten
./x.py                         ->  x.py                             # the one intended case
```

## Two consequences, not one

The ticket calls this display-only. **Half of that is right, and the other half is the reason this
is worth a test rather than a one-line patch.**

1. **Display.** `source_paths()`'s output is joined verbatim into the `evidence` field at `:897`
   and `:910`, which is what the board comment and the printed table show. Every dotted path is
   rendered wrong.
2. **⛔ The overlap math, which the ticket does not claim.** `:757` computes `paths[a] & paths[b]`
   over these same normalised strings. A dotted path and its dotless twin normalise to the SAME
   key, so **two lanes touching genuinely different files read as a collision** — a lane
   is denied `parallel-ok` for a conflict that does not exist. It is unreachable in this repo today
   only because nothing sits at a dotless `agents/` or `claude/`. That is a property of the current
   tree, not of the code, and it is exactly what a test should pin.

The ticket's own wording — *"the overlap math normalises both sides through the same function, so
verdicts are unaffected"* — is true for a path and **itself**. It is false for a dotted path and its
dotless twin. Recorded here rather than silently widening the ticket.

## The fix

Both call sites become one named helper, which also removes a duplicated normalisation that nothing
asserted agreed (the SCC-298 F14 lesson, in this file):

```python
def norm_path(p) -> str:
    """Normalise a declared touch-set path for comparison AND display."""
    s = str(p).strip()
    while s.startswith("./"):
        s = s[2:]
    return s
```

`while`, not `if`: `.//` and `././` are cheap to survive and the loop is the honest reading of
"strip the prefix". No `os.path.normpath` — that would also resolve `..`, which changes what a
declared path means.

## Acceptance — every row is checkable, and every row gets an assertion that fails first

| # | Statement | The assertion that proves it |
|---|---|---|
| A1 | A dotted directory keeps its dot through `source_paths()` | case `SCC-295 A1` — a hidden-dir path in, the same string out |
| A1b | A dotfile at the repo root keeps its dot | case `SCC-295 A1b` |
| A2 | The intended case is not regressed | cases `SCC-295 A2` / `A2b` — CONTROLS, green before the fix and after |
| A3 | A dotted path and its dotless twin are **different keys** | case `SCC-295 A3` — the two sets do not intersect |
| A4 | Two lanes touching those twins are **not** in conflict | case `SCC-295 A4` — driven through `resolve`, both approved |
| A5 | `creates` normalises identically to `paths` | cases `SCC-295 A5` / `A5b` — one shared helper, contract pinned both directions |
| A6 | The board `evidence` string shows dotted paths | case `SCC-295 A6` — read off the real `evidence` field, not a re-implementation |
| A7 | Planning-dir filtering is unchanged | case `SCC-295 A7` — CONTROL |
| A8 | The whole file and the whole suite stay green | `test_label_tasks.py` full run; `run_all.py` through `gate_receipt.py`; `workflow_lint --toolkit-only` |

The literal fixtures those cases use, fenced for the same reason as above:

```text
A1   .agents/scripts/risk_seam.py     A1b  .mcp.json  .gitignore
A2   ./x.py -> x.py                   A2b  ././x.py -> x.py
A3   .agents/x.py  vs  agents/x.py    A7   ./_artifacts/a.md -> dropped
A5   creates: .agents/scripts/new_helper.py
```

## Declared Change Set

⚠️ **AUDIT FINDING (Lens 1, 2026-08-23): this block was `incomplete` on all 8 bullets.** It was
written `path — OP → row`; `declared_change_set.py` wants `OP path`, op marker first. Rewritten to
the parsed shape — an unparseable block silently disables `/smh-code-review` Step 2's drift check,
which is exactly the consumer that depends on absence being loud.

- EDIT `.agents/scripts/label_tasks.py` — one `norm_path()` helper, both call sites routed through it → A1, A2, A3, A4, A5, A6, A7
- EDIT `.agents/scripts/tests/test_label_tasks.py` — the RED cases and the two regression controls → A1, A2, A3, A4, A5, A6, A7
- NEW `_artifacts/_main/2026-08-23_label-tasks-dot-strip/implementation_plan.md` — this file → plan
- NEW `_artifacts/_main/2026-08-23_label-tasks-dot-strip/task.yaml` — lane manifest → close
- NEW `_artifacts/_main/2026-08-23_label-tasks-dot-strip/walkthrough.md` — RED/GREEN evidence, verdict, Your Actions → A8
- NEW `_artifacts/_main/2026-08-23_label-tasks-dot-strip/sweep.json` — the mutant table → A8
- NEW `_artifacts/_main/2026-08-23_label-tasks-dot-strip/gates/suite.json` — the suite receipt → A8
- EDIT `_artifacts/_main/INDEX.md` — the lane's ledger row → plan

## Steps

1. **RED** — add the cases above to `test_label_tasks.py` and run the file. Expect A1, A3, A4, A5,
   A6 to FAIL and A2, A7 to PASS (A2/A7 are regression controls and must be green from the start —
   a control that starts red is measuring the wrong thing).
2. **GREEN** — add `norm_path()`, route `:718` and `:758` through it, re-run.
3. **Sweep** — mutants drawn from the new code, each naming the case that must kill it, run as one
   `mutation_sweep.py` pass.

   ⚠️ **AUDIT FINDING (Lens 1, 2026-08-23): this table MUST carry `"unfiltered": true`.**
   `mutation_sweep.py:37-40` names `test_label_tasks.py` by name as the file that *"declares no
   `c.block()` at all — there is no label to select, so a filter, ANY filter, matches nothing, the
   harness exits 3, and every mutant comes back a sweep error rather than a result."* Confirmed:
   `grep -n "block(" .agents/scripts/tests/test_label_tasks.py` returns nothing. ⛔ Declaring both
   `unfiltered` and `block` is **refused at load**, so the table carries `unfiltered` and `case`
   only. Attribution stays strict — the declared `case` must name a case on the `FAILED:` line.
4. **Gate** — `run_all.py` through `gate_receipt.py`, `workflow_lint --toolkit-only`, `check_links`.
5. **Review** — `/smh-code-review`.

## Decisions taken up front

- **`[sop-ok]` is expected on the code commit, and this is the reason.** `.agents/scripts/*.py` is a
  SOP usage surface, but `workflows_testing_SOP.md` answers *what does the operator type*, and
  nothing an operator types changes here. What changes is a string the labeller prints. If the gate
  disagrees at commit time, the SOP gets a real edit on merit rather than a reflexive opt-out.
- **A6 is proved through the real `evidence` construction, not by re-implementing the join.** A test
  that asserts `", ".join(sorted(...))` against its own copy of that expression proves only that the
  test can read itself.

## Landing-order dependency

`claude/teaching-edition` (SCC-280) is live and touches **`_artifacts/_main/INDEX.md`**, the one file
this lane also edits. It is a ledger: both lanes add a row at the top of the same table.

- **Either order is fine.** Whichever lands second absorbs `main` and resolves a one-line conflict by
  keeping both rows.
- **If that lane lands first**, this lane's absorb at close-out shows that conflict; it is the known
  ledger class, not a real disagreement, and nothing in this lane's code is affected.
- **No other overlap.** SCC-280's 40-file set contains no `label_tasks.py` and no test file of mine.
  `chore/SCC-300-sandbox-claude-hooks-skills` has zero commits and one untracked artifacts folder.

---

## Self-Audit (2026-08-23)

**Level: LEDGER+BLAST** — the Declared Change Set touches `.agents/scripts/label_tasks.py`, a script
with its own test and an `INDEX.md` row. **Mode:** PRE-WORK.

```
lens:        1 Repo Reality + Scope Ledger
checks_run:  every path/script/rule the plan names exists on disk; `declared_change_set.py parse`;
             both-machines command check; lane fit (deployable paths); Scope Ledger precondition
             and the NEW x acceptance table; the sweep instrument's own preconditions
read:        .agents/scripts/label_tasks.py:713-721,753-762,422-432,555-563,893-912 ·
             .agents/scripts/tests/test_label_tasks.py:1-30,364-380,190-196 ·
             .agents/scripts/mutation_sweep.py:30-58 · .agents/scripts/INDEX.md:25,36 ·
             .claude/rules/sop-currency.md · `declared_change_set.py parse <plan>` ·
             `sop_currency.py --paths .agents/scripts/label_tasks.py`
verdict:     findings below
```

```
lens:        2 Parity + Blast
checks_run:  real importers vs mentions; callers in .githooks/; twin engine; scripts/INDEX.md row
             staleness; SOP usage surface; sibling worktrees after a real `git fetch origin main`;
             risk_seam classify
read:        `grep -rln label_tasks .agents .githooks docs` (10 hits) ·
             `grep -rn "^import label_tasks|^from label_tasks"` (1 hit: the test) ·
             `grep -rn source_paths` outside the module (0 non-test hits) ·
             `risk_seam.py classify` -> {"status":"unclassified","root":"<this worktree>"} ·
             `git worktree list` + per-tree `diff --name-only origin/main...HEAD`
verdict:     findings below
```

```
lens:        3 Pre-Mortem
checks_run:  attached failure narratives to the anchored findings above; no originated findings
read:        the two findings from lenses 1 and 2
verdict:     clean (narratives attached, nothing originated)
```

### Findings

| anchor | literal text read | consequence | severity |
|---|---|---|---|
| `_artifacts/_main/2026-08-23_label-tasks-dot-strip/implementation_plan.md` — the `## Declared Change Set` block | `- \`.agents/scripts/label_tasks.py\` — EDIT → A1, A2, …` | Parsed **`incomplete` on all 8 bullets** — the op marker must lead, not trail. `/smh-code-review` Step 2 diffs the real diff against `entries`, which was `[]`: the drift check would have passed on an empty list and reported nothing, for every file in the lane. **Pre-mortem:** the silent one — a green drift check that never compared anything. **FIXED INLINE**; re-parse now reads `entries: 8, incomplete: 0` | **high** |
| `.agents/scripts/mutation_sweep.py:37-40` | *"`"unfiltered": true` … is the ONLY honest answer for a test file that declares no `c.block()` at all (`test_label_tasks.py`): there is no label to select, so a filter — any filter — matches nothing, the harness exits 3, and every mutant comes back a sweep error rather than a result."* | Plan step 3 declared an ordinary sweep. Every mutant would have returned a **sweep error**, not a kill — and the lane would have shipped with zero mutation evidence while appearing to have run one. Confirmed against the file: `grep -n "block(" test_label_tasks.py` returns **nothing**. **Pre-mortem:** the sibling-of-8681d83 one — an agent reading eight errors as "the sweep ran". **FIXED INLINE** in step 3 | **high** |
| `.claude/rules/sop-currency.md` (usage-surface table) + `sop_currency.py` run output | `\| \`.agents/scripts/*.py\` · \`*.ps1\` \| The safety net. \|` and, on this exact path, `x The SOP quick-reference was not updated with this change.` | The armed `commit-msg` hook **will refuse** the code commit unless the SOP is staged or `[sop-ok]` is in the message. The plan already predicted this; running the gate confirms it rather than assuming. **Pre-mortem:** the reflex one — reaching for `[sop-ok]` without looking, which is what the rule says trains the gate into checking nothing | **medium** |

### Observations (uncounted — judgment, no check behind them)

- **The ceremony artefacts have no acceptance row, and that is by design.** `walkthrough.md`,
  `task.yaml`, `sweep.json` and `gates/suite.json` are required by `artifacts-always-first.md` and
  by this lane's own door, not by an acceptance statement. Their "caller" is the rule. Recorded here
  rather than raised as a Scope Ledger finding, which would be a false positive on every lane.
- **`risk_seam` returns `unclassified`, correctly.** SCC-289: the centre carries no code graph
  because a code graph parses code and this repo is markdown. `"root"` confirms it answered about
  this worktree. Every judgement in Lens 2 was taken from the diff.
- **`scripts/INDEX.md` rows 25 and 36 do not go stale.** They describe the two modes, the set math
  and the planning-dir carve-out; neither mentions path normalisation, and `norm_path()` is private.
  No INDEX edit is owed — checked rather than assumed.
- **Blast radius is genuinely contained.** `source_paths` has **no caller outside `label_tasks.py`
  and its own test**. The four other files matching `label_tasks` cite it in comments as precedent
  (`mutation_sweep.py:39`, `jira_feed.py:1685`, `declared_change_set.py:51`,
  `test_twin_parity.py:178`) — no code dependency, nothing to port.
- **One engine, two doors.** `/cicd-label-tasks` and `/smh-label-tasks` both drive this one script
  (two-mode since SCC-155), so there is no twin script to keep in parity — the usual `cicd`/`smh`
  divergence risk does not apply here.

### Scope Ledger

**Precondition met:** SCC-295 carries a 3-row `Plan` block, each row naming a concrete observable
(the two call sites; the two test behaviours; the re-run confirmation).

| NEW artefact | acceptance row that requires it |
|---|---|
| `implementation_plan.md` | `artifacts-always-first.md` §2 (this lane's plan) |
| `walkthrough.md` | A8 + the close-out preflight, which blocks without it |
| `task.yaml` | the close-out manifest contract |
| `sweep.json` | A8 (the mutation evidence) |
| `gates/suite.json` | A8 (the suite receipt) |

No empty cells → no Scope Ledger finding.

### Landing-order dependency

`claude/teaching-edition` (SCC-280) is live, 40 files, and shares exactly one path with this lane:
**`_artifacts/_main/INDEX.md`**. Ledger class — both lanes prepend a row to the same table. Either
order lands; whichever is second absorbs `main` and keeps both rows. No code overlap: SCC-280's set
contains no `label_tasks.py` and no test file of this lane's.
`chore/SCC-300-sandbox-claude-hooks-skills` has zero commits and one untracked artifacts folder.

```
Audit verdict: GO
```

Neither high finding breaks an acceptance row or a hard gate — both were fixable at plan time and
are fixed inline above, which is the whole point of running this before the work.
