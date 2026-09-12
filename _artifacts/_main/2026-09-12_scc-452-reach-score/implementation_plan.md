# SCC-452 — replace the line-count `tiny` arm with a measured reach score

**Lane:** `chore/SCC-451-reach-score`, `riders: [SCC-452]`, cut from `origin/main` @ `3cbed78f`.
**Parent:** SCC-451, which stays In Progress until this lands (its partial landing declared exactly
that, and this is the ticket that lets it close).

## What is wrong today

`ceremony_tier` decides review depth — `tiny` means "the plan is two sentences". Its `tiny` arm is a
line count behind a named interface, written crude on purpose in SCC-451 step one:

```python
inert = set(inert_paths(repo, rels))
counted = [p for p in rels if p not in inert]
if lines <= TINY_MAX_LINES and len(counted) <= TINY_MAX_FILES:   # 50 lines, 5 files
    return "tiny"
return "quick"
```

Lines are a proxy for blast radius and a bad one. A three-line change to a module forty files import
is not small; a forty-line change to a leaf nobody imports is. The count cannot tell them apart.

## The mechanism

`code-review-graph impact --files <paths> --repo <r> --depth <n>` already answers the real question —
how many files reach the changed one. It is installed at `/home/dlohn/.local/bin/code-review-graph`.
**This lane reads that graph; it does not build a second import parser.** `ceremony_tier` already
refuses to re-parse the critical-surface map for the same reason it should refuse here — *"a second
matcher is a second answer"* (`task_preflight.py:339`).

New constant beside the existing caps:

```python
TINY_MAX_REACH = <measured, not guessed — see Verification 1>
```

New helper, with the fail direction stated in its own docstring:

```python
def reach_score(repo: Path, rels: list[str]) -> int | None:
    """How many files reach these paths, per code-review-graph. `None` = NO EVIDENCE.

    ⛔ `None` IS NOT ZERO. Zero means "measured, nothing imports it"; None means "not measured".
    Every arm that cannot produce a real number returns None: binary absent, graph absent, graph
    stale vs HEAD, non-zero exit, unparseable output, timeout. The caller must never read None
    as a low score -- that is the fail-toward-permissive hole this whole story exists to close.
    """
```

## Where it goes — and what does NOT move

The order above the `tiny` arm is unchanged. Only the last two lines change.

| # | Check | Result | Changed? |
|---|---|---|---|
| 1 | critical-surface veto (via `scope_check`) | `full` | no — absolute, never overridden by a score |
| 2 | CI dir / manifest name | `full` | no |
| 3 | `_is_entry_point(rel)` | `full` | **no — and this is the regression to guard** |
| 4 | `lines is None or structural` | `quick` | no |
| 5 | reach score + line/file caps | `tiny` or `quick` | **yes, this lane** |

⛔ **`_is_entry_point` must survive untouched, and a reach score is exactly what would kill it.**
Measured 2026-09-12 over AviationChat's 146 frontend components: `app/layout.tsx` has reach **0** and
wraps every screen; `app/dashboard/page.tsx` has reach **0** and is an entire user journey. Nothing
imports a page — the router loads it. A reach score alone ranks the riskiest files as the safest.
The name-based exclusion runs at step 3, before any score is consulted, and stays there.

## Fail direction — the whole point

`None` → `quick`. Never `tiny`. Same shape as `load_inert`'s malformed arm from SCC-451: absence of
evidence lowers nothing.

**Staleness is load-bearing, not a nicety.** `code-review-graph status` reports `built_at_commit`. If
it does not equal HEAD, the reach numbers describe a different tree, and a number about the wrong
tree is worse than no number because it looks like evidence. Stale → `None`.

## Acceptance

| # | Statement | Check |
|---|---|---|
| A | An entry point with reach 0 is still `full` | `ceremony_tier(repo, ["app/layout.tsx"], lines=1, structural=False) == "full"` |
| B | No graph → `quick`, never `tiny` | binary made unavailable; same input that IS `tiny` with a score present |
| C | A stale graph → `quick` | `built_at_commit` != HEAD |
| D | High reach + tiny diff → `quick` | a leaf-importing module above `TINY_MAX_REACH` |
| E | Low reach + tiny diff → `tiny` | a true leaf under both caps |
| F | The critical-surface veto still beats any score | an auth file with reach 0 → `full` |
| G | SCC-451's 30 unrun mutants run and are killed or explained | the saved harness |

⛔ **Every acceptance row gets a CONTROL in the other direction.** B is the one that matters: an
assertion that "no graph means not tiny" passes with the whole reach check deleted unless the control
proves the same input reaches `tiny` when a score IS present. That is the vacuous-pin shape this lane's
parent hit twice — an assertion about a guard must use input the guard actually admits.

## Verification

1. **Measure before choosing `TINY_MAX_REACH`.** Run `impact` over AviationChat's frontend and the
   lobby's `.agents/scripts/`, plot the distribution, pick the knee, and record both the number and the
   run that produced it. A threshold nobody measured is the line count again with extra steps.
2. RED first on every acceptance row, pasted.
3. `run_all.py` green; `test_inert_paths.py` blocks E and G rewritten, not appended to.
4. The 30 mutants from SCC-451 batch B, via `scratchpad/saved-mutants/mutation_harness_45.py`.
5. Mutate the new code deliberately — drop the `None` arm, drop the staleness check, drop the
   entry-point call — and confirm each goes red.

## Declared Change Set

- EDIT `.agents/scripts/task_preflight.py` — `TINY_MAX_REACH`, `reach_score()`, the `tiny` arm → A–F
- EDIT `.agents/scripts/tests/test_inert_paths.py` — blocks E and G rewritten, each with its control → A–F
- NEW `_artifacts/_main/2026-09-12_scc-452-reach-score/walkthrough.md` — the record → G

## Open question for the operator

**Depending on `code-review-graph` puts a shipping gate behind a binary that SCC-453 flags as
silently absent on machines where nobody installed it by hand.** My recommendation is to take the
dependency and make absence fail toward ceremony (a missing graph costs you a `quick` review you
did not strictly need, never a skipped one). The alternative — a second import parser living inside
`task_preflight.py` — is a second answer to a question the graph already answers, and it would need
to handle TypeScript, JSX, and Python imports correctly to be worth anything.
