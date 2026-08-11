# SCC-88 — walkthrough (lobby half of the first relocation sweep)

**Result: 21,296 → 17,285 B. 83.2% → 67.5%. 4,011 bytes freed, headroom 4,304 → 8,315.**
For scale, SCC-69's full compaction pass over all 145 memories freed **633 bytes**. Nothing was
summarized, shortened, or retired to get this — 33 facts moved to the repo they are true in.

## What landed

| | |
|---|---|
| Files relocated out of the lobby | 33 (145 → 112 memories) |
| Index rows deleted / rewritten | 13 / 5 |
| Headings corrected | 3 |
| Gate | `run_all` **12/12 exit 0** · memory suite **44/44 exit 0** (was 39) · `workflow_lint --toolkit-only` **0 errors 0 warnings exit 0** · `sop_currency` **exit 0** |

The AGY half is **AVCH-53** (`c0b53879`, pushed): the owed mirror back-pointer plus all 33 files
indexed. It is the destination, so **it must merge before this branch does** — this half is a
deletion, and you do not delete before the destination is durable.

## The defect this sweep created, and the fix

Relocation produces a third kind of `[[link]]` residue the gate did not know about. After the
move, 34 wikilink edges pointed from staying lobby memories at relocated ones, and
`audit_signals()` reported all 17 targets as **danglers** — described as "either a forward
reference or danglers left behind by a retirement (**fix the source**)."

That advice is wrong for every one of them, and the list is long enough to re-triage on every
future audit and conclude "not actionable" each time. That is precisely how a signal becomes noise
people learn to skip — the failure this file's own `rotted_pointers()` comment already documents
about a check with a bad hit-rate.

Fixed by teaching the check the difference: a dangling target that exists in a *project* store is
a cross-store reference, not a dangler, and the next move is to **follow it**, not repair it. The
lookup reads live sibling repos, so it rides the same explicit `repo` opt-in as
`project_store_signals` — the hermeticity leak SCC-73's review caught (a live-state read behind a
default, green in a worktree and red on `main` for every unrelated lane) is exactly the trap this
would otherwise have re-dug. Five fixtures pin it, including the hermetic case.

**Verified against real data, not fixtures:** run with the post-sweep lobby store resolved against
the main checkout where AGY's store is populated, all **17 targets classify as RELOCATED and zero
as dangling**.

## Three headings the sweep made wrong

After the move, `## AGY sprint & stories` contained **zero** AGY memories and `## AGY infra & ops`
held the git branch model, the ⛔ backticks hazard, the one-merge rule and all four per-machine
memories. A session hunting for the branch model would not look under an AGY heading. The sweep
caused that, so correcting it is part of the same job:

- `## AGY sprint & stories` → `## Sprint, stories & close-out`
- `## AGY infra & ops` → `## Git, machines & worktrees`
- `## AGY access & data` → `## ⛔ AGY data safety — AGY-scoped, kept HERE on purpose`, with a
  two-line comment recording the ruling. Without it the next audit reads those three rows as
  unfinished business and moves a production-data guardrail out of the index that every session
  loads.

## Errors made and corrected

1. **A hand-typed line-number set was wrong.** My first projection hard-coded the rows to delete
   and included the `autopilot-glm-hybrid-lane` row, which stays. Rewritten to derive every row
   decision from the moved-file list, with a hard failure if a partial row has no rewrite mapping
   and if any rewrite rule never matches. Deleted rows: **13, not 14.**
2. **The projected figure was wrong in all three numbers** — I reported 4,419 B / 65.9% from that
   bad set, then added the safety-ruling comment. Real: **4,011 B / 67.5%.** The comment costs
   ~200 B and is worth it.
3. **I broke a passing test** (43/44). My fixtures wrote into `repo/"mem"`, a store a later case
   rewrites and then asserts is clean, so the fixture file read as an orphan there. Fixed by
   giving the new cases their own store dir, with the reason written at the line.
4. Left two `(AGY's … moved to its store)` parentheticals in rewritten index rows on the first
   pass — move history, not lesson, in a file every session pays for. Removed.

## Not touched, deliberately

`_my_resources/migrations/` → `docs/migrations/` appeared in the **main checkout** at 11:58:47,
mid-session, from another live session (the tree was clean at 08:31). Excluded entirely and never
staged. Two other lanes are also live (`chore/SCC-77-main-write-gate`, `chore/SCC-83-sop-content-audit`),
which is why this work was done in a worktree rather than on the main checkout.

## Still owed

- **An AGY-side memory gate** (AVCH). AGY's store is now 48 memories and nothing in that repo
  enforces its own integrity — it is only detected advisorily from the lobby.
- Phase 2 (thin root + category files) stays parked. `audit_block()` still names it as the remedy
  for when compaction *and* relocation are both spent. This sweep bought roughly 4 KB of headroom,
  not a new ceiling.
