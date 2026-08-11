# SCC-88 — walkthrough (lobby half of the first relocation sweep)

**Result: 21,296 → 17,272 B. 83.2% → 67.5%. 4,024 bytes freed, headroom 4,304 → 8,328.**
For scale, SCC-69's full compaction pass over all 145 memories freed **633 bytes**. Nothing was
summarized, shortened, or retired to get this — 33 facts moved to the repo they are true in.

## What landed

| | |
|---|---|
| Files relocated out of the lobby | 33 (145 → 112 memories) |
| Index rows deleted / rewritten | 13 / 5 |
| Headings corrected | 3 |
| Gate | `run_all` **12/12 exit 0** · memory suite **46/46 exit 0** (39 pre-task → 44 → 46 after review) · `workflow_lint --toolkit-only` **0 errors 0 warnings exit 0** · `sop_currency` **exit 0** |

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
would otherwise have re-dug. Fixtures pin it, including the hermetic case and the unreadable-store caveat added at review.

**⚠ Corrected after review — the original claim here was false as written.** It said the split was
*"verified against the main checkout, all 17 RELOCATED and zero dangling."* Re-measured against the
main checkout today: **0 RELOCATED, 17 dangling.** The original measurement was real, but it was
taken while AGY was checked out on `chore/AVCH-53-memory-store-intake`; that checkout was then
returned to `epic/AVCH-18-adk-2x-runtime`, and the claim was left describing a transient state the
same document elsewhere records as not AGY's state.

The correction matters more than the wording, because it exposes the real property: **the split is
branch-sensitive, not merge-sensitive.** It resolves against whatever AGY's single shared checkout
currently has. Even after AVCH-53 lands on AGY main, any AGY checkout sitting on an older
branch — including the long-lived `epic/AVCH-18-adk-2x-runtime`, which carries a written "don't
merge to main early" — reports the 17 as danglers again.

That is now handled rather than hidden: a store the run **could not read** is named on the dangler
line itself (*"⚠ 2 project store(s) could not be read here (AGY_AVIATIONCHAT, NEXgen-VR-Director) —
some of these may be RELOCATED rather than dangling"*). The honest scope of A6 is therefore: the
split resolves correctly wherever the project store is readable, and says so plainly wherever it is
not. Verified in both states.

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
   bad set, then added the safety-ruling comment. Real: **4,024 B / 67.5%.** The comment costs ~200 B and is worth it.
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

- **An AGY-side memory gate** (AVCH). AGY's store now holds every relocated memory and nothing in that repo
  enforces its own integrity — it is only detected advisorily from the lobby.
- Phase 2 (thin root + category files) stays parked. `audit_block()` still names it as the remedy
  for when compaction *and* relocation are both spent. This sweep bought roughly 4 KB of headroom,
  not a new ceiling.

---

## Code Review (2026-08-11)

Verdict: PASS @ b5d3180
Suite evidence measured at `b5d3180` — the sha carrying every fix below. The review opened at
`aec47e5` as **CONCERNS** (one BLOCKER, three MAJOR); all of them are applied and re-measured
here, so the verdict is stated at the code that will actually land, not at the code that was
reviewed. Only this doc-line changes after `b5d3180`, which does not invalidate the run.

**Scope** — the 39-file diff of `chore/SCC-88-memory-relocation-sweep` vs `main`, plus its paired
half `AVCH-53 @ c0b53879`.
**Method** — clean-room adversarial hunt in a subagent with no conversation context (diff first,
plan and walkthrough only after), acceptance audit against A1–A7, command-centre gate, Step 0.7
re-derivation against current `main`.

### Findings

| file:line | severity | failure scenario | disposition |
|---|---|---|---|
| `_artifacts/_memory/` (33 deletions) | **BLOCKER** | Close out SCC-88 while `AVCH-53` is unmerged: `main` carries 112 memories, every reachable AGY checkout has 15, and the 33 relocated facts are unreachable until someone remembers a branch in another repo. The one claim whose violation destroys 33 memories was left to prose. | **applied** — made mechanical in SCC-94's `check_secondary`: a `landing: independent-task` half whose HEAD is not on its `origin/main` now warns *at the merge*, naming the ticket to land first. Fires correctly on this lane today. |
| `test_memory_store.py:643` | MAJOR (as reported) | Reviewer: the hermeticity assertion "cannot fail", mutation-proven with `project_stores(repo or REPO_ROOT)` still 44/44. | **partly dismissed, then hardened.** The mutation was **inert** — the outer `if repo is not None` guard short-circuits, so that line is dead code and 44/44 was correct, not tautological. Against the *real* leak shape (guard removed) the original assertion already failed. Hardened anyway with a stem that exists in the live AGY store; mutation-proven both ways from the main checkout (43/45 under the real leak). |
| `test_memory_store.py:381` | MAJOR | `project_stores(repo)[0]` discarded the skips, so in a worktree — where `Projects/` is an empty stub and nearly all work happens — the split resolved nothing and printed the full "fix the source" list it exists to prevent, with no hint the project tier was never consulted. | **applied** — the dangler line now names the stores it could not read: *"⚠ 2 project store(s) could not be read here (AGY_AVIATIONCHAT, NEXgen-VR-Director) — some of these may be RELOCATED rather than dangling."* Pinned by a fixture using the `UNCLONED` stub. |
| `walkthrough.md:39` | MAJOR | The "verified against the main checkout — 17 RELOCATED, 0 dangling" claim was **false as written**. Re-measured: 0 RELOCATED, 17 dangling. The measurement was real but taken while AGY sat on the AVCH-53 branch, which was then reverted. | **applied** — corrected in place with the error left visible, and the underlying property named: the split is **branch-sensitive, not merge-sensitive**. |
| `MEMORY.md:16` | MINOR | `"— 48 memories"` is true only on the AVCH-53 branch (AGY main has 15), nothing gates it, and AGY's next write invalidates it. Direct prior art: SCC-82 caught the SOP calling a folder a "13-doc manifest" after it went to 11. | **applied** — count dropped. |
| `closeout_preflight.py:318` | MINOR | A docstring pointed at `agy-epic-keys-rot-silently`, which this diff relocates; a lobby reader following it finds nothing. Only such reference outside the store. | **applied** — now names the new store. |
| `test_memory_store.py:405` | MINOR | `rotted_pointers(store, REPO_ROOT, …)` runs unconditionally, ignoring `repo`, inside the function whose docstring says cross-repo reads are opt-in. | **deferred** — pre-existing and identical on `main`; latent (no fixture body carries a backtick path). Not this diff's to fix, but the new comment does lean on a contract the function does not fully keep. |
| `test_memory_store.py:613`, `:619` | NIT | Dead fixture content; single-store attribution would also pass if the code always named the first store. | **deferred** — both latent; production has exactly one indexed project store. |

### Gates — actual output

- **Enforcement suite** — `python3 .agents/scripts/tests/run_all.py` → `12/12 files passed`, **exit 0**
- **Memory suite** — `python3 .agents/scripts/tests/test_memory_store.py` → `-- 46/46 passed --`, **exit 0** (39 pre-task → 44 → 46 after review)
- **Toolkit lint** — `python3 .agents/scripts/workflow_lint.py --toolkit-only` → `-- 0 error(s), 0 warning(s), 8 info --`, **exit 0**
- **SOP currency** — `python3 .agents/scripts/sop_currency.py` → **exit 0**
- **Link + anchor** — every markdown link in `MEMORY.md` resolves; swept all 33 relocated stems repo-wide: **0** `](<stem>.md)` links anywhere outside the store
- **Assertion evidence** — the review's own fixtures re-run green; the leak mutation re-runs **red** (43/45) from the main checkout

### Acceptance

| item | proving assertion |
|---|---|
| A1 index materially below trigger, cap unmoved | 17,272 B = 67.5%; `INDEX_CAP` / `TRIGGER_PCT` pinned by two fixtures |
| A2 files exist + indexed in AGY before the lobby deletes | all 33 present on `AVCH-53`; `check_store()` on it → 0 problems. **Ordering now warned mechanically** (see BLOCKER row) |
| A3 back-pointer present | `LOBBY_BACKPOINTER in AGY MEMORY.md` → True; the lobby `[SIGNAL]` cleared |
| A4 both stores clean, links resolve | `check_store()` → 0 problems on both |
| A5 no broken markdown link outside the store | repo-wide sweep, 0 hits |
| A6 relocated ≠ dangling | 17 RELOCATED / 0 dangling **where the store is readable**; where it is not, the line says so. Scope corrected — see the MAJOR row |
| A7 gates green | pasted above |

### Clean-Code Gate

Machine floor green (`run_all` 12/12, `workflow_lint` 0/0). Per the command's Step 3.5, Step 1's
drift/bloat pass is imported rather than re-run: it found **no** over-engineering, dead code, or
unnecessary abstraction beyond the two NITs above — the production change is 7 lines and comment
density matches this file's established style. Boundary conditions (`[:4]` truncations) verified
correct. No banned patterns, no secrets, no unowned TODOs.

### Step 0.7 — re-derivation against current `main`

1. **Nothing moved under this diff.** `origin/main` = local `main` = `50e357b` = the merge-base;
   **0 files landed** since branching. No reference this diff names was moved, renamed or deleted.
2. **True overlap with `main`: none.** `merge-tree` vs `main` is clean.
3. **Sibling-lane landing order.** Six lanes live. `_artifacts/_main/INDEX.md` conflicts with
   SCC-83, SCC-90 and SCC-94 — mechanical, everyone appends a row at the top; resolve by keeping
   all rows, never by dropping one. **The one real dependency: `AVCH-53` must merge before this
   branch.** Reversed, the lobby deletes 33 memories whose destination has not landed. Also live:
   **SCC-89 modifies `agy-canonical-test-venv.md` while this branch deletes it** (modify/delete);
   its repoint must be carried into AGY's copy or it is lost silently, since nothing gates path rot
   inside a project store. `.gitignore` conflicts against SCC-77 are **not** from this diff —
   SCC-77 is **31 behind main** and independently re-fixes what SCC-73 already landed.

## Merge Reconciliation (2026-08-11) — landing #4

Verdict: PASS @ (this commit) — re-measured after absorbing `main`; supersedes `PASS @ b5d3180`,
measured before SCC-90, SCC-89 and SCC-94 landed.

### The modify/delete, and why it was NOT resolved blindly

`_artifacts/_memory/agy-canonical-test-venv.md` — **deleted in HEAD, modified in `origin/main`.**

SCC-89 repointed a path *inside* the file this lane deletes. Git presents this as a conflict with
two mechanical options, and **both are wrong on their own**: keep the file and this lane's whole
purpose is undone for one memory; drop it and SCC-89's fix disappears with no message. Ordering does
not rescue it either — the earlier report suggesting it might was checked and is incorrect. Both
orders end with the lobby copy deleted.

**Resolved as a decision, with the precondition proven first.** The deletion wins, per SCC-73's
two-tier law: the memory is AGY's, and the lobby copy is the one that should not exist. That is only
safe if the path fix survives at the destination — so it was **verified before accepting the
deletion**, not after:

```
AGY  main:_artifacts/_memory/agy-canonical-test-venv.md:20
  -> `docs/migrations/install_guides/python_vytest-updates-other-machines.md` (lobby repo)   ✓ fixed
```

The repair travelled to AGY under **AVCH-53**, which landed at `eba1fae5` **before** this lane —
exactly the ordering this walkthrough's landing note demanded.

### The anti-stranding check

Deleting 33 memories from the lobby is only safe if all 33 exist on a **merged** branch in AGY. Not
assumed — enumerated:

```
for each file deleted from _artifacts/_memory/ in main...HEAD:
    git -C Projects/AGY_AVIATIONCHAT cat-file -e main:_artifacts/_memory/<file>
-> deleted-from-lobby files absent in AGY main: 0
```

### The ledger

`_artifacts/_main/INDEX.md` — 1 row ours, 6 rows theirs, **no deletions either side**. Kept all
seven; this lane's row on top, because it lands last and the table is newest-first.

### Gates after the reconcile (bare)

```
python3 .agents/scripts/tests/run_all.py                -> exit 0   12/12 files passed
python3 .agents/scripts/workflow_lint.py --toolkit-only -> exit 0   0 errors, 0 warnings, 8 info
python3 .agents/scripts/tests/test_memory_store.py      -> exit 0   46/46 passed
```

`test_memory_store.py` reports `project store not gated — submodule not checked out` for both
projects. That is the **designed** behaviour in a worktree (`Projects/` is an empty stub there), and
it is a *named* skip rather than a silent pass — the distinction SCC-73 built deliberately, so a
project store nobody can read never reds a lane nobody in the lobby could repair.
