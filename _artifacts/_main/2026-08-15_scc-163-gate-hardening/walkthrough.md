# SCC-163 — walkthrough

**Lane:** `chore/SCC-163-gate-hardening` · **Base:** `main` @ `8ae2e25` · **LANE: LOCAL**
**Plan:** [implementation_plan.md](implementation_plan.md) — `Audit verdict: GO`, approval *"approved"* @ `12efa6d`
**Two gate defects, one branch**, per the operator's scope ruling: *"add it to the SCC-163 I want to
keep as much on one ticket as possible."* They share no files, so each proved independently.

## Task Checklist

- [x] **A1** RED first: a case reproducing `chore ← epic` by fast-forward, seen failing
- [x] **A2** the push is REFUSED and prints the standard banner
- [x] **A3** `refs/heads/epic` covered; the `:105` ref filter **documented as a ruled omission**
- [x] **A4** no regression on the four ALLOW pairings — `epic←main`, `epic←story`, `story←epic`, `main←epic`
  - ⚠ `EP2` had to be re-fixtured to an **unpushed** epic, or it passed against its own mutant
- [x] **A5** mutation sweep drawn from the code, declared in the plan before code existed
- [x] **B1** RED first against a **real corpus**; AVCH-58's pre-correction section caught
  - ⚠ the fixture lives at `9674880d` in **AGY_AVIATIONCHAT** — vendored, not fetched
- [x] **B2** flags rows asking the operator to create / place / rule on ticket work
- [x] **B3** does **not** flag the three allowed classes — the hard part, and the corpus proved why
- [x] **B4** fenced examples are not rows; `_unfenced` reused, not re-derived
- [x] **B5** status-note rows declared out of scope **in the code**
- [x] **B6** mutation sweep drawn from the code
  - ⚠ the sweep harness itself scored two crashed suites as survivors — fixed, re-run
- [x] SOP + `scripts/INDEX.md` + `_artifacts/_main/INDEX.md` landed with their surfaces

## Evidence

HEAD at implementation: **`918f15f`**. Every assertion below drives the real script or the real
function and reads its verdict; the one structural pin reads **executable lines only**.

### A — the backstop was blind to `epic/*`

**RED** (`test_git_hooks.py --case "EP · …"`, before a line of the fix existed) — 6/12, and the
reproduction is the ticket's, exactly:

```
 * [new branch]      chore/SCC-163-lane -> chore/SCC-163-lane
[FAIL] EP1 · ...and nothing reached the remote: b57c54ae…  refs/heads/chore/SCC-163-lane
[FAIL] EP1 · a chore lane carrying an UNLANDED epic is REFUSED
[FAIL] EP1 · ...and the refusal names the epic
[FAIL] EP1 · ...and prints the standard banner
[FAIL] EP6 · the epic enumeration is keyed to chore/* only
[FAIL] EP6 · ...and the omission is documented with its reason
-- 6/12 passed --
```

The five ALLOW controls (`EP2`, `EP2b`, `EP3`, `EP4`, `EP5`) passed here **and** after — that is
what makes them controls rather than tests of the fix.

**GREEN** — `12/12`, and the whole file `129/129 → 141/141`, exit 0.

**The fix is four words in a `case`, and all the difficulty is in why it is not one word in the
`for`.** Three arms of `merge-target-guard`'s own judge table (`target:source`) say an epic inside a
lane is legitimate:

| pairing | verdict | consequence |
|---|---|---|
| `chore:epic` | **refuse** | the defect — must enumerate |
| `story:epic` | allow | a story lane absorbing its own epic **is** `/cicd-park`, run daily |
| `incident:epic` | allow | *"absorbing main (or an epic) is the everyday mid-incident move"* |
| `epic:story` / `main:epic` | allow | pushed ref is `epic/*` or `main` — declined at the ref filter |

So the enumeration is keyed on the lane class, mirroring the `BASES` switch beside it: `chore/*` only.

> ⚠️ **`EP2` was re-fixtured mid-build, and the reason is the case's whole value.** Written with the
> epic pushed to `origin`, a blanket widening *still* scores `landed=1` through the `claude/*` arm of
> the `BASES` switch — so the control would have passed against **the exact mutant it exists to
> kill** (A-M2). With the epic local, `BASES` is `origin/main` alone and only the lane-class arm keeps
> it green. `EP2b` keeps the pushed shape as a second control.

**The `:105` omission is ruled, not overlooked** — operator: *"A3. no we dont need it."* `epic:chore`
and `epic:epic` remain escapable by fast-forward. Both are named in the script with the reason:
judging a pushed epic needs a **third** candidate set that *excludes* `claude/*`, because stories
landing on the epic is what an epic IS, and a false red there sits on `/cicd-push-e2e`. `EP4` pins
the current behaviour so a later widening goes red and explains itself.

### B — `## Your Actions` was prose

**RED, twice, and the first one was not good enough.** The bare run raised
`AttributeError: module 'jira_feed' has no attribute 'banned_action_rows'` — honest, but it kills the
file before any assertion, and `red-test-can-die-before-its-assertion` says read *which line raised*.
A no-op stub produced the real red:

```
[FAIL] B1 · AVCH-58 row 1 (fold into AVCH-54 / mint its own key) is FLAGGED
[FAIL] B4 · 'Mint a ticket for the N deferred items' is FLAGGED
[FAIL] B5.1x / B5.2x / B5.3x · a REAL banned row from the same corpus IS flagged
[FAIL] B7 · finish prints the banned-row banner
[FAIL] B9 · check-actions reports the fixture's one banned row
-- 212/220 passed --
```

Every **positive** failed; every **negative control** passed vacuously on a detector that does
nothing — which is exactly why the positives carry the proof.

**GREEN** — `197/197 → 221/221`, exit 0.

**⭐ The corpus was measured before the rule was written, and it changed the design.**
`open_actions()` over every `.md` in `_artifacts/`: **101 walkthroughs carry the section, 25
unchecked rows.** The ticket's B2 phrase list, read literally, flags **8 of 25 — at most 4 real**:

| row | naive | correct | why |
|---|---|---|---|
| `**SOP-nag ticket … your call**` | FLAG | **FLAG** | proposes a residue ticket |
| `Decide whether finding 13 earns a ticket` | FLAG | **FLAG** | the banned shape, by name |
| `**File the follow-on Task** …` | FLAG | **FLAG** | the banned shape, by name |
| `**Rule the landing order.**` | FLAG | **allow** | merge sequencing |
| `**Decide whether the CONCERNS is worth clearing…**` | FLAG | **allow** | a product decision |
| `**Rule on A1** / `A2` / `A6`` | FLAG | **allow** | acceptance disputes — the operator's own call |

All four false positives are things Step 5 **permits**. So a bare verb is never a trigger: the
detector fires on **verb × ticket-work object**, and a bare ticket key is deliberately not an object
(`"Merge AVCH-59 to main"` and `"Move SCC-99 to Done"` both carry one and are both allowed). The
seven real allow-rows are pinned as negative controls; three real banned rows from the same corpus
are pinned as positives, so the suite cannot pass by never firing.

**Arming, per the ruling *"1. yes"*:** `finish` prints a `⛔ BANNED ACTION ROW` banner and **holds
exactly as before** — the verdict is unchanged, the diagnosis is new. `--strict-actions` refuses and
**ships disarmed**. A block here would fire *after* the merge, trading a held ticket for an erroring
close-out.

### Two vacuous greens, both caught by the reds themselves

1. **`B8` passed before the flag existed.** `--strict-actions` was undefined, so argparse exited 2 on
   *unrecognized arguments* — the same 2 a real refusal returns. `code == 2` was satisfied by the
   feature **being absent**. Now paired with the banner, plus a clean-input half proving the flag
   discriminates rather than blanket-refusing.
2. **The mutation harness scored two crashed suites as survivors.** It counted `[FAIL]` lines and
   ignored the exit code; `B-M3`/`B-M4` crashed the suite (`AttributeError` at `B5.1`) and emitted
   zero `[FAIL]` lines, so a *killed* mutant read as *survived*. The kill signal is now the **exit
   code** — the same `piping-a-gate-hides-its-exit-code` shape, aimed at the tool meant to catch it.

### Mutation sweep — 8/8 killed, 0 survivors, 0 defective, tree CLEAN after restore

Declared in the plan **before code existed**, drawn from the fix's own lines, run as one sweep.

| # | Mutant | Killed by |
|---|---|---|
| A-M1 | drop `refs/heads/epic` from the chore arm | `EP1` |
| A-M2 | blanket widening (move it into the bare enumeration) | `EP2`, `EP3` |
| A-M3 | retarget the arm `chore/*)` → `claude/*)` | `EP1` |
| A-M4 | widen the `:105` filter to accept `refs/heads/epic/*` | `EP4`, `EP6` |
| B-M1 | defeat fence stripping in `_unfenced` | `B6` |
| B-M2 | add a bare ticket key to `_TICKET_OBJECT` | **`B5.1/B5.3/B5.5` — the live corpus only** |
| B-M3 | drop the object requirement (`if verb`) | crash at `B5.1` |
| B-M4 | drop the verb requirement (`if obj`) | crash at `B5.5` |

> ⭐ **B-M2 is the one worth reading.** It was declared to be killed by `B2`/`B3` — the ticket's own
> named negative controls — and it **was not**. "Merge" and "Move" are not banned verbs, so a
> bare-key object never reaches those rows. The only cases that catch it are the **real corpus rows**
> pinned in `B5`. Without the corpus work, that mutation would have shipped undetected.

## Your Actions

- [ ] **Merge and close out** — `/smh-close-task-merge-tree --expect-key SCC-163`. Invoking it is
      the per-merge sign-off; one invocation, one merge. The lane is pushed and clean.

*(Nothing else is owed. Part A's `:105` omission and Part B's status-note exclusion are both ruled
and recorded in the code — they are settled decisions, not open items, and per this ticket's own
Part B they would be banned rows if written as ones.)*
