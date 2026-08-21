---
IsArtifact: true
ArtifactMetadata:
  title: "SCC-211 — the production door pre-flights before it writes or gates"
  type: walkthrough
  date: 2026-08-21
---

review-runtime: fan-out

# SCC-211 — walkthrough

**Lane:** `chore/SCC-211-push-e2e-precheck` · **HEAD:** `cdc23a0` · **Base:** `origin/main` @ `fb5fb95`
**Plan:** [implementation_plan.md](implementation_plan.md) (Audit verdict: GO, three findings baked in)

## What changed, in one paragraph

`/cicd-push-e2e` is the only command in this system that writes production `main`, and it was the
only door that asserted nothing mechanically before it started — both siblings call a preflight
script first. The consequence was not theoretical: uncommitted work in the epic checkout meant
Step 3 gated *that tree* while Step 4 merged *the branch*, so what reached production was never
what went green, and nothing in the file's 151 lines would have said so. It now pins the ticket at
Step 0.6 and runs `ship_preflight.py` at Step 1.5 — shape, that pinned key against the branch's,
a clean checkout that is `0 0` with its remote, and the lane — with **exit 2 stopping the command**.
Two smaller contradictions went with it: the mint no longer demands merge words the three-form
ruling says were already given, and a `chore/*` branch is admitted here only when its diff reaches
deployable code.

## Task Checklist

- [x] Step 0 — repo resolved from `git rev-parse`; SCC-211 read; runtime probed (`fan-out`)
- [x] Step 0.5 — worktree cut off `origin/main`, assets linked, ticket → `In Progress` (exit 0)
- [x] Step 1 — five acceptance rows fixed from the ticket's own ACCEPTANCE block
- [x] Step 1.5 — plan written, `/smh-self-audit` → **GO** (3 findings, all baked in), `approved`
- [x] Step 1.6 — subtasks: none earn a branch; one commit set, said so and moved on
- [x] Step 2 — RED: both files written first and **seen red** (10/34 and 42/43 — see Evidence)
      - the 10 "passes" in the first red were exit-code-only halves passing on the interpreter's
        own exit 2; every case pins a phrase precisely so that cannot be mistaken for green
      - one weak assertion (`"SCC" in out`) matched the worktree PATH — tightened to the sentence
- [x] Step 3 — GREEN: script, door, rule, INDEX, SOP, mirrors; suite stamped through the receipt
      - `fold_continuations()` added: P1's first cut failed a **correct** door over a legal `\`
        continuation, and a guard a formatting choice breaks is one the next author reformats around
      - the first full suite run was **RED** and caught two real defects of mine (below)
- [x] Step 3.5 — eject tripwire re-checked: no deployable path, no story shape, all rows checkable
- [x] Step 4 — review gate (`/smh-code-review`) — see `## Code Review`
- [x] Step 5 — artifacts, manifest, Dev Record

## Evidence

### AC1 · a dirty epic checkout STOPs before the gate — proven by a test that failed against today's file

**RED** (`test_ship_preflight.py`, before the script existed):

```
[FAIL] the script exists at .agents/scripts/ship_preflight.py: RED: /cicd-push-e2e still has no mechanical precheck (SCC-211 finding 1)
[PASS] SP-B dirty tree -> exit 2: ... can't open file 'ship_preflight.py': [Errno 2] No such file or directory
[FAIL] SP-B ...and it says UNCOMMITTED: ... [Errno 2] No such file or directory
[FAIL] SP-B ...and it says the merge would not carry them: ...
[FAIL] SP-B the VERDICT is BLOCKED, not a warning under a clear line: ...
-- 10/34 passed --
```

⭐ **Read the `[PASS]` on the exit code.** A missing script exits 2 from the interpreter, so the
refusal's exit-code half passed while its phrase halves failed. That is the whole reason every case
here pins a phrase — an exit-code-only suite of refusals would have been "green" against nothing.

**RED** (`test_door_preflight_order.py`, the ordering half):

```
[FAIL] P1 the door RUNS ship_preflight.py (fenced, not prose): prose describing a check is not a check: git fetch origin | git branch -a --list '*epic/*' | ...
[FAIL] P2 ORDER preflight -> absorb main -> mint -> push main: missing: ship_preflight.py
-- 31/43 passed --
```

**GREEN:** `test_ship_preflight.py` → `-- 41/41 passed --` · `test_door_preflight_order.py` → `-- 45/45 passed --`

### AC2 · a branch whose key segment ≠ the pinned EXPECTED_KEY STOPs

Covered by SP-D (both halves: the wrong pinned key, and a key this repo does not answer to) and by
P6, which pins that `EXPECTED_KEY=` appears **before** the preflight reads it — an unset variable is
an empty `--expect-key`, and an empty operand is never a pass. Both green above; mutants M4, M5 and
M14 kill them.

### AC3 · the sign-off sentence and the steps below it no longer contradict

The door now states the ruling positively where Rule 1 is, and Step 4's mint comment reads the
operator's **invocation this turn** as its evidence. The old `No such words this turn → STOP and
ask` is gone. Pinned by P5 (both directions) and by the extended `SCC-193` RULING/forms loops,
which now cover this door; mutants M15 and M18 kill them.

### AC4 · the chore-branch admission has explicit, tested behaviour

`ship_preflight.py` derives it from the diff, importing `task_preflight.PRODUCT_DIRS` rather than
re-typing the list, so the two doors cannot drift about what "deployable" means. Deployable diff →
exit 0 under the light gate; nothing deployable → exit 2 and the lane goes to
`/smh-close-task-merge-tree`. A repo with no deployable surface at all is refused with its own
reason. `git-policy.md`'s `main` row now says the same thing. SP-F (four cases + a control that an
epic is never subjected to the question), P3, P4; mutants M9, M10, M16, M17.

### AC5 · mutation-proven — 18 mutants, every one drawn from the code

**39 declared · 39 killed** — 29 against `ship_preflight.py` (`sweep-script.json`) and 10 against
the door (`sweep-door.json`). The full table lives in those two files; grouped by what they attack:

| group | mutants | killed by |
|---|---|---|
| the four checks the script exists for — dirty tree, `0 0`, the pinned key, the lane | M1 · M2 · M4 · M9 | SP-B · SP-C · SP-D · SP-F |
| the refusals that must name the right command | M5 · M6 · M7 · M8 · M10 · M20 · M36 | SP-D · SP-E · SP-A · SP-F · SP-C · SP-M |
| **width, not just existence** — a narrowing rather than a deletion | M2 · M7 · M30 · M31 | SP-C · SP-E · SP-M |
| the three ref states, and the diff that must actually run | M3 · M19 · M21 · M22 | SP-C · SP-K |
| the operands the script refuses to guess at | M23 · M24 · M25 · M33 · M35 | SP-I · SP-J · SP-M |
| the lane table's membership **and its order** | M26 · M27 · M28 | SP-L · SP-M |
| the outcome-not-the-flag rules | M11 · M29 · M32 · M34 | SP-G · SP-M |
| the door: order, teeth, and the operands of its fenced call | M12–M18 · M37 · M38 · M39 | P1–P7 · S5 |

```
-- restore verified: bytes match, nothing was committed, and `git diff --quiet` is clean --
-- full file, unfiltered: test_ship_preflight.py        -> exit 0   -- 92/92 passed --
-- full file, unfiltered: test_door_preflight_order.py  -> exit 0   -- 49/49 passed --
```

⭐ **The sweep did its job twice, and both are recorded rather than tidied away:**

- **M10 genuinely SURVIVED.** Deleting the "this repo has no deployable surface" arm left SP-F
  green, because the diff arm below also refuses and also names the Task door — same verdict,
  different fact. The fact is the arm's whole value: *"your diff happened to miss"* is actionable;
  *"this repo can never qualify"* ends the question. **The case was strengthened to assert the
  reason**, and the re-aimed mutant dies on it.
- **M7 was killed by a SIBLING case**, so the sweep refused to score it — correctly, because a kill
  attributed to the wrong case is not evidence about the declared one. The **declaration** was
  re-aimed; the code was not touched.
- ⭐ **Round 2 was an independent lens running its OWN 15-mutant sweep — and all fifteen
  survived this suite.** Every one was a real hole: the arms existed and behaved correctly,
  but nothing checked them, so nothing would have noticed them break. One turned out to be a
  live defect rather than only a gap (the `remotes/origin/…` spelling — see the Code Review
  section). The suite went 54 → 92 cases and the door test 45 → 49; all fifteen mutants were
  adopted into the declared tables so they are now certified rather than merely fixed.
- One mutant was refused outright at declaration time (an empty `mutated` field reads as
  "never filled in", not "delete this") and was re-aimed as a comment.
- **A second real survivor came out of the review round: M21.** The `diff.returncode` arm had
  **no covering case at all** — the ref-fallback fix that landed beside it removed the arm's
  only trigger, leaving defensive code nobody had exercised. The arm is right (a repo with
  neither `main` nor `origin/main` cannot resolve a base), so the answer was a case, not a
  deletion. M23 repeated M7's shape: killed by sibling cases, declaration re-aimed.

### Gates

| gate | command | result |
|---|---|---|
| enforcement suite | `gate_receipt.py run --task SCC-211 --gate suite` | **41/41 files, exit 0 @ `cdc23a0`**, receipt at `gates/suite.json` |
| toolkit lint | `workflow_lint.py --toolkit-only` | 0 errors, 0 warnings, 8 info (BOM notes, pre-existing) |
| door parity | `test_command_surfaces.py` | 177/177 — both mirrors regenerated by one `sync-agents` run |
| SOP currency | door + SOP staged in the same commit | armed gate satisfied; no `[sop-ok]` used |
| mutation | two declared tables | **18/18 killed**, restore verified twice |

⚠️ **The first full suite run was RED, and it caught two defects of mine** — the receipt records it
and the fix rather than hiding it:

1. `test_ship_preflight.py` had one `c.check` **outside** a `c.block` guard. An unguarded check
   runs under every `--case` filter and counts toward every filtered tally, so a mutant it killed
   would be attributed to whichever case the sweep named — the exact corruption this lane's own
   sweep depends on not happening. Now `SP-0`, guarded.
2. `_artifacts/_main/INDEX.md` had no row for this session folder.

## Measurements worth keeping

- **The door crossed the Antigravity mirror budget: 9,758 → 12,403 bytes** (threshold 11,500). The
  `.agents/workflows/` mirror is therefore now a **generated launcher**, which is the designed
  state for **17 of 40** mirrors including every sibling door — and strictly better than the
  alternative, since Antigravity *truncates* an over-cap verbatim copy rather than rejecting it.
  The `.opencode/` mirror stays byte-identical to the brain. Not a regression; measured, not assumed.
- **Full suite wall: 122 s** (41 files, parallel).

## Your Actions

- [x] The merge itself — lands via this branch's PR
- [x] Plan approved 2026-08-21; the three audit findings were baked into the plan before any code

Nothing else is owed. The lane is review-complete and pushed; `/smh-close-task-merge-tree` is the
next door, and invoking it is the decision to proceed.
