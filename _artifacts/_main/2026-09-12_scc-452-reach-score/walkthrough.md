---
ticket: SCC-452
lane: chore/SCC-451-reach-score
riders: [SCC-452]
base: origin/main @ 3cbed78f
---

# SCC-452 — Blast radius instead of a line count

`ceremony_tier` decides how much review a change has earned. Until now its cheapest verdict,
`tiny` — "the plan is two sentences" — was a line count: fifty lines, five files. SCC-451 shipped
that deliberately crude, behind a named interface, and said so in the code.

Lines are a proxy for blast radius and a bad one. Three lines in a module forty files import is not
a small change; forty lines in a leaf nobody imports is. The count cannot tell them apart, and the
difference is the only thing a reviewer actually cares about.

This lane puts a **measured reverse-dependency reach score** in front of the count — how many other
files reach the ones you touched, read from `code-review-graph`, which already owns the import
parsing for six languages. Nothing here re-implements that.

## The one design decision, and why it changed on contact

The approved plan said: no evidence → `quick`, never `tiny`. Absence of evidence must not buy a
cheap review. The principle is right. The implementation it implied is not, and measuring the
ground on the way in is what showed it.

**Two of the ten repos in this workspace have a graph at all.** A worktree never inherits its
parent's, and every story in this system is built in a worktree. And the tool refuses to certify a
zero for the two languages that matter: `uncertainty.LANGUAGE_GAPS` lists `impact_radius` under both
the call patterns and the import patterns for Python and the whole JS/TS family, so a zero about a
`.py` or a `.tsx` always comes back carrying a blind-spot note instead — measured, **178 of 209**
lobby source files.

Under `None → quick`, every one of those is `quick` forever. The rule would not have tightened the
tier; it would have deleted it, while looking like a tightening.

So the rule that shipped is the principle underneath it, stated in one direction:

> **Reach can only RAISE ceremony. It is never an admission ticket.**

With no evidence the line caps decide, which is exactly today's behaviour, so no repo gets weaker
than it is now. With evidence, a hub is pushed up to `quick` no matter how small the diff.

That shape also retires the staleness problem rather than guarding it. A stale number that reads too
high costs one `quick` review nobody needed; one that reads too low falls through to the caps.
Neither can make the answer permissive, which is why there is no staleness gate in the code — and
why the plan's "a stale graph is worse than no graph" stopped being true once the direction was
fixed. It was true for an admission ticket. It is false for a veto.

## What the entry-point rule survives

`app/layout.tsx` has reach **0** and wraps every screen. `app/dashboard/page.tsx` has reach **0**
and is a whole user journey. Nothing imports a page — the router loads it. A reach score consulted
first ranks the riskiest files in the tree as the safest.

`_is_entry_point` therefore runs **before** any score, exactly where SCC-451 left it, and the
mutation below proves the order rather than asserting it.

## Task Checklist

| # | Item | State |
|---|---|---|
| 1 | Measure the reach distribution in both graphed repos and pick `TINY_MAX_REACH` from it | done |
| 2 | `reach_score()` — every no-evidence arm returns `None` | done |
| 3 | `_reach_from_impact()` — the contract as a pure function, testable where the binary is not | done |
| 4 | Wire the veto into `ceremony_tier`, after the entry-point loop | done |
| 5 | Block K / K2 in `test_inert_paths.py`, each pin with its control | done |
| 6 | Mutation sweep over every new arm | done — 8/8 killed |
| 7 | `run_all.py` green | done — 92/92 |

## Evidence

### The measurement that chose `TINY_MAX_REACH = 10`

Run 2026-09-12, `code-review-graph impact --depth 2` over every tracked `.py/.ts/.tsx/.js/.jsx`
file in both repos that carry a graph, after bringing each graph current.

| Repo | Files | Measured | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|
| lobby | 209 | 29 | 2 | 4 | 9 | 10 | 86 (`tests/_harness.py`) |
| AviationChat | 899 | 308 | 6 | 18 | 50 | 96 | 204 |

AviationChat's per-value counts for reach 1 through 10 run `37 · 27 · 39 · 31 · 20 · 16 · 9 · 9 ·
10 · 9`, then collapse to `4 · 8 · 2 · 1 · 1`. Two thirds of every measured file sits at 10 or
under, and the lobby's 95th percentile is exactly 10. The knee lands in the same place in both
repos, so the cap sits on it.

The gap between "files" and "measured" is the no-evidence population — 180 in the lobby, 591 in
AviationChat — and it is what the fail direction exists for.

### The mutation sweep — 8 of 8 killed

Each mutant breaks one arm of the new code and the suite must notice.

| Mutant | What it breaks | Result |
|---|---|---|
| M1 | every zero is read as a real zero | KILLED — `K · a python blind-spot zero is None, NOT 0` |
| M2 | the veto is deleted | KILLED — `K2 · reach over the cap (11) is quick at THREE lines` |
| M3 | `>` becomes `>=` | KILLED — `K2 · CONTROL: reach exactly AT the cap (10) is still tiny` |
| M4 | no evidence routes to `quick` (the plan's original rule) | KILLED — `E · …sizes to tiny at 12 lines` |
| M5 | the entry-point exclusion is replaced by the score | KILLED — `H · app/layout.tsx is an entry point — 3 lines, still full` |
| M6 | the empty-path guard is dropped | KILLED (see below) |
| M7 | a wrong-typed `impacted_files` is trusted | KILLED — `K · a wrong-typed impacted_files is None` |
| M8 | a non-ok `status` is trusted | KILLED — `K · a non-ok status is None` |

**M6 survived its first run, and the pin was the thing that was wrong.** Written as
`reach_score(repo, []) is None` it passed with the guard deleted, because `--files` is `nargs="+"`
and argparse exits 2 on an empty one — so the assertion was about argparse, not about the guard. The
pin now asserts what the guard actually does: that **no process is spawned at all**. Same shape the
parent lane hit twice; the rule that catches it is *ask what this asserts if I delete the guard*.

### The suite

```
python3 .agents/scripts/tests/run_all.py
92/92 files passed
python3 .agents/scripts/tests/test_inert_paths.py
-- 114/114 passed --
```

Two files were red on the first full run and both were this lane's own doing, both fixed here:

- `test_jira_feed.py` SCC-335 E1 — `task_preflight.py:380` decoded captured output with the machine
  locale. The new `subprocess.run` now passes `encoding="utf-8", errors="replace"`, the house
  pattern from `wf_common.git`.
- `test_check_maps.py` F2 — this artifact folder had no `INDEX.md` row. Added.

## Code Review (2026-09-12)

Not yet run. This lane is built and green; the review is the next step.

## Your Actions

- **Merge the PR when its check is green.** Docs plus two gate files; the lobby runs one check
  (`main-write-gate`), which runs `run_all.py` and `workflow_lint`.
- **`code-review-graph` is a per-machine `pip --user` install and CI does not carry it.** That is
  handled — the contract is pinned as a pure function that needs no binary, and the one live pin
  asserts the documented fallback when the binary is absent. Nothing to install for CI.
- **The tier is only as sharp as the graph is current.** `code-review-graph update --repo <r>` is
  what buys the sharper answer; skipping it costs a `quick` review you did not strictly need, never
  a skipped one. Both graphs were brought current during this lane (lobby at `dddf0ee3`,
  AviationChat at `1aa35485`).
- **SCC-451 can close once this lands.** Its partial landing declared this ticket as the remainder,
  and this is the remainder.
