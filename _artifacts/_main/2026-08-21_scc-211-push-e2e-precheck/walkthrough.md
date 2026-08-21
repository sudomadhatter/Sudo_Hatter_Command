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
- [x] Step 4 — review gate (`/smh-code-review`) — **PASS**, five lenses, see `## Code Review`
      - ⭐ the review found **this ticket's own defect alive inside its fix**: with the epic in a
        linked worktree — the norm under `worktree-per-story` — the dirty-tree check measured the
        wrong tree and cleared the ship. Reproduced, then fixed
      - an independent lens ran its own 15-mutant sweep and **all fifteen survived** the suite;
        every one became a case, and the tables grew 24 → 45
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

**GREEN (at the shipping sha, after the review's 14 fixes):** `test_ship_preflight.py` → `-- 102/102 passed --` · `test_door_preflight_order.py` → `-- 49/49 passed --`

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

**50 declared · 50 killed** — 29 against `ship_preflight.py` (`sweep-script.json`) and 10 against
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
| **the tree that is actually gated** — the review's own finding | M41 · M42 | SP-N |
| the uncertified fixes: token-free fetch, conf states, foreign prefix | M43 · M44 · M45 | SP-O · SP-M |
| **the story door** deriving its lane tree, and the explicit tree still counting | M46 · M47 | `test_closeout_preflight` SCC-211 |
| **the task door** deriving its lane tree, and the memory ruling surviving it | M48 · M49 · M50 | `test_task_preflight` SCC-211 |

```
-- restore verified: bytes match, nothing was committed, and `git diff --quiet` is clean --
-- full file, unfiltered: test_ship_preflight.py        -> exit 0   -- 102/102 passed --
-- full file, unfiltered: test_door_preflight_order.py  -> exit 0   --  49/49  passed --
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
| mutation | two declared tables | **45/45 killed**, restore verified on every run |

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
- [x] All 14 review findings fixed in this lane — none deferred, no ticket minted, nothing carried
      out of the lane as future work

Nothing is owed. The lane is review-complete, `PASS`, and pushed; `/smh-close-task-merge-tree` is
the next door, and invoking it is the decision to proceed.

---

## Code Review (2026-08-21)

Verdict: PASS @ 1c2ee57
Suite evidence measured at the same sha — `gates/suite.json`, 41/41 files, exit 0, 124.9 s.

lenses_run:
- blind-hunter · ok
- edge-case-hunter · ok
- literal-correctness-hunter · ok
- acceptance-auditor · ok
- test-adequacy-auditor · ok
lenses_counted:  5/5
lenses_na:       none

(`review_mode: full` — the plan exists — and `review_level: standard`, derived from the Step 0.7
radius below, so every lens in the roster applied and none was skipped by mode.)

dispositions:    per-lens: blind-hunter=5/1/0 · edge-case-hunter=2/0/0 · literal-correctness-hunter=0/0/0 · acceptance-auditor=2/3/0 · test-adequacy-auditor=11/1/0
drift:           undeclared=2 · unimplemented=0 · incomplete=0 — both named in the findings table and kept, with reasons

⭐ **SCOPE WIDENED AFTER THE FIRST PASS, on the operator's direction (2026-08-21), filed on this
ticket rather than a new one.** The first verdict covered `/cicd-push-e2e` alone. Asked whether the
sibling doors should verify the same way, I measured them — the answer was no, and one of the two
holes is not theoretical. All three now derive the gated tree from one shared body; see § *The other
two doors* below.

**Scope.** The committed diff `origin/main...HEAD`: 22 files — one new script, two test files, the
door and its two generated mirrors, `git-policy.md`, `scripts/INDEX.md`, the SOP, and the lane's
artifacts. **Method.** Five lenses in parallel, each in its own clean context (`review_runtime:
fan-out`, probed at Step 0 before any of this), then an acceptance audit against the plan's five
rows, the command-centre gate, and the clean-code floor. The Blind Hunter ran as a subagent on the
diff alone — I am the builder, so my own context is contaminated by construction, and `fan-out` is
what let that lens be genuinely blind rather than dropped.

### Step 0.7 — the blast radius, re-derived against current `main`

1. **Nothing this diff references moved.** `origin/main` is still `fb5fb95`, the merge-base — zero
   files landed on `main` while this was built — and all five repo paths the new text names resolve.
2. **True overlap: none.** `merge-tree --write-tree` returns a clean tree, no conflict messages.
3. **Sibling lane:** `chore/SCC-235-dual-surface-blast-radius` is live at `dae82f8`, touching only
   its own artifacts and `_artifacts/_memory/`. Zero file overlap, so **no landing-order dependency**
   in either direction.

### Findings

Twenty-eight findings came back across five lenses. **Fourteen were assessed real and fixed in this
lane; the rest were dismissed or ruled under `code-standards` §6.5.** Two disagreed with their
label in a way worth carrying forward, and both are named below.

| # | file:line | sev | failure scenario | disposition |
|---|---|---|---|---|
| 1 | `ship_preflight.py` `check_sync` | **critical** | The epic is checked out in a **linked worktree** — the norm under `worktree-per-story`. `PROJECT_ROOT` stands on `main`, spotless; the lane's tree is dirty. `status --porcelain` in `PROJECT_ROOT` alone answered *"working tree clean"* and the verdict read *clear to gate and ship*. **This is the SCC-211 defect itself, surviving inside its own fix.** | applied @ `50e3958` — measures every tree that could be gated, names the dirty one; positive control for the clean-worktree shape |
| 2 | `ship_preflight.py` `check_sync` | important | A branch on `origin` with no local ref was refused *"never pushed — the branch exists on this disk only"*, the exact inverse. Reachable on a fresh clone or an epic pushed from the other machine. | applied @ `97eb5ee` — three ref states, plus a distinct answer for a branch that exists nowhere |
| 3 | `ship_preflight.py` `check_shape` | important | `git branch -a` prints `remotes/origin/epic/KEY-slug` — the door's own Step 1 output. Pasted back, it missed the shape regex and earned the keyless-epic refusal, whose remedy is *"rename it to carry the epic's REAL key"*: advice to rename a branch that already carries its key. | applied @ `8b23f71` — normalised once and announced, as `closeout_preflight` does |
| 4 | `ship_preflight.py` `check_lane` | important | `diff.stdout` read without `diff.returncode`, and a local ref that cannot resolve → *"0 file(s) changed, none of them deployable"* stated as fact about a diff that never ran, then routed the lane to a door that refuses deployable diffs and hands it back. | applied @ `97eb5ee` |
| 5 | `ship_preflight.py` `main` | important | `argparse`'s `required=True` accepts `""`, which is what an unset shell variable becomes across the door's two fenced blocks. An empty `--expect-key` blamed the **branch** (*"aimed at ANOTHER lane's branch"*) for a pin that never arrived. | applied @ `97eb5ee` |
| 6 | `test_door_preflight_order.py` SCC-211 block | important | Replacing **`Exit 2 → STOP.`** with *"It is informational."* left 45/45 green — a door that runs the precheck and then ignores it, which is the original defect wearing the fix's clothes. Dropping `--branch`, or aiming `--repo` at cwd, survived too. | applied @ `8b23f71` — P7 plus per-operand rows |
| 7 | `ship_preflight.py` `check_sync` | important | `--branch origin/main` was refused **twice**: correctly as the merge target, then again as *"no such branch, local or remote"* — about a ref that plainly exists. *"A gate that states something plainly untrue teaches the reader to stop believing its output"* (`task_preflight.check_scope`). | applied @ `1c2e74b` — the ref-state question declines once the shape check has ruled |
| 8 | `ship_preflight.py` `check_intent` | suggestion | `repo_keys` returns `[]` for two states — conf absent, or conf present declaring nothing — and the message named only the first, sending a reader hunting for a file sitting right there. | applied @ `50e3958` — both states say which, and what the gap costs |
| 9 | `ship_preflight.py` `_fetch` | suggestion | AUDIT FINDING F3 (the fetch running without the session's `GITHUB_TOKEN`) was **uncertified**: deleting `env=env` would have failed nothing. | applied @ `50e3958` — observed through a `git` shim on PATH that records the env it was handed |
| 10 | `ship_preflight.py` `main` | suggestion | The resolved **repo** appeared only under `--json`. The door says *read the header*; that argument is as true of the repo as of the branch, and `--repo` exists because cwd is not intent. | applied @ `97eb5ee` |
| 11 | `ship_preflight.py` `main` | nitpick | The header printed **twice** — `Report.print_human` emits it too. The fixture pinned PRESENCE, which two headers satisfy. | applied @ `97eb5ee` — the case now counts |
| 12 | `test_ship_preflight.py` (9 blocks) | important | Nine decision arms had **no case at all**: the incident row of `WRONG_LANE` *and its load-bearing order*, a fetch asked-for-and-failed, the `behind` half of the sync read, the no-`jira.conf` warn, key normalisation, an anchored lane scan, the standing-on notice, the key-immediately-after-prefix rule, and `--json` values on a refusal. | applied @ `8b23f71` · `50e3958` |
| 13 | `workflows_testing_SOP.md` atlas | nitpick | My own edit left `S1` a decision diamond with a single unlabelled edge after its three outcome edges moved to `S15`. | applied @ `97eb5ee` |
| 14 | `_pf_fixtures.py:74` | suggestion | No fixture could reach the no-`jira.conf` arm — `make_repo` always wrote one. | applied @ `8b23f71` — additive `jira_conf` knob, default `True`, so every existing caller is byte-identical |
| D1 | `.agents/.sync-manifest.json` | — | **Undeclared drift.** A generated file the mandated `sync-agents` run rewrites; its whole diff is one `generated` timestamp. | **kept** — four of four recent lanes stage it (SCC-201/210/225/240); the plan's own "stage only the two mirrors" line was the narrower claim and was wrong about house convention |
| D2 | `.agents/scripts/tests/_pf_fixtures.py` | — | **Undeclared drift.** The `jira_conf` knob, added *by* the review to reach an uncovered arm. | **kept** — a review-driven fixture change is not plannable in advance by definition; recorded here rather than by amending an approved plan |
| — | `.claude/skills/cicd-push-e2e/SKILL.md` | — | Blind Hunter: the skill surfaces might carry stale door text. | **dismissed** — both are 1,082-byte generated thin launchers that read the command live; they carry no step text to go stale. The lens had no repo access and said so |
| — | the door's byte budget | — | Acceptance Auditor: the delta is 2,645 B against the plan's ~1.5 KB F2 budget. | **ruled, kept** — F2 explicitly permits crossing when measured, and it is measured below. The launcher is the designed state for 17 of 40 mirrors including every sibling door, and Antigravity *truncates* an over-cap verbatim copy rather than rejecting it, so the launcher is strictly safer |
| — | plan names `sweep.json`, two files shipped | — | Acceptance Auditor: internal contradiction inside the plan. | **ruled, kept** — the plan's own Step 4 names both; `_artifacts/` is carved out of drift on both sides by contract |

⭐ **The two calibration disagreements worth carrying forward.** The Edge Case Hunter filed
finding 1 as `suggestion / confidence 0.6 / inferred` — I reproduced it in a real linked worktree
and it is **critical**: it is this ticket's own defect, alive inside the fix for it. And the
Test-Adequacy Auditor filed as `important` a set of gaps whose *code was already correct*; they
were real and worth every fix, but the label overstated them, which is exactly the input-not-verdict
distinction §6.5 exists for.

### Gates

| gate | result |
|---|---|
| **Enforcement suite** | `run_all.py` → **41/41 files, exit 0 @ `50e3958`**, 127.3 s, stamped through `gate_receipt.py` |
| **Toolkit lint** | `workflow_lint.py --toolkit-only` → `-- 0 error(s), 0 warning(s), 8 info --` (BOM notes on vendored `testarch-*`, pre-existing) |
| **Assertion evidence** | `test_ship_preflight.py` **102/102** · `test_door_preflight_order.py` **49/49** · named block `--case "SCC-211 …"` 15/15, filter matched 1/6 blocks |
| **Mutation** | **45 declared, 45 killed** (35 script + 10 door), restores verified byte-for-byte against the pre-sweep sha, both closing full-file runs green |
| **SOP currency** | `sop_currency.py` exit 0; the SOP moved with the door in every commit that changed usage. One `[sop-ok]` used, at `1c2e74b`, with its reason in the log |
| **Link + anchor** | 158 links resolved from their containing files, 3 external skipped, **0 dead introduced** — the SOP's 8 unresolved in-page anchors are identical on `origin/main` and are my slugger mis-modelling em-dashes, not the doc |
| **Door parity** | `test_command_surfaces.py` **177/177** — both mirrors regenerated by one `sync-agents` run |
| **Sibling suites** | `test_task_preflight.py` 182/182 · `test_task_preflight_receipts.py` 39/39 · `test_suite_runner.py` 109/109 (the ORPHAN walk over the new blocks) |

### Acceptance matrix — every row, and the assertion that proves it

| # | acceptance (from the ticket) | proving assertion | result |
|---|---|---|---|
| 1 | a dirty epic checkout STOPs before the gate, proven by a test that FAILS against today's file | `SP-B` (5/5) — seen RED against the pre-existing file, where only the interpreter's own exit 2 passed · `P1`/`P2` order | ✅ |
| 2 | a branch whose key segment ≠ the pinned `EXPECTED_KEY` STOPs | `SP-D` (4/4) · `P6` pins the pin precedes the read | ✅ |
| 3 | the sign-off sentence and the steps below no longer contradict | `P5` both directions · the `SCC-193` RULING and three-forms loops extended to this door (15/15) | ✅ |
| 4 | the chore admission is removed or given explicit, tested behaviour | `SP-F` (8/8) incl. a control that an epic is never asked the lane question · `P3`/`P4` · `git-policy.md` `main` row aligned | ✅ |
| 5 | mutation-proven: each assertion declared against a mutant it alone kills | 45/45, declared before mutating, drawn from the code, attribution enforced by `mutation_sweep.py` | ✅ |

**Nothing in the diff is beyond the list**, other than the two drift rows ruled above.

### Clean-Code Gate

| check | result |
|---|---|
| `py_compile` | 3 files, exit 0 |
| comment contract §2A | no banned drift patterns; the three `would be` hits are counterfactuals inside explanatory comments, which is the documented reasoning, not placeholder prose |
| whitespace | `git diff --check` clean |
| line length | house max is **120** (`code-standards.md:87`); `ship_preflight.py` maxes at 96 |
| machine floor | imported from Step 3 rather than re-run (`run_all`, `workflow_lint`, `sop_currency`, link+anchor) |

Legacy debt in untouched files: noted, not gated on. **Changes applied during review: 14** — see the
table; the walkthrough body above was refreshed to match.


---

## The other two doors (SCC-211, second pass — operator-directed)

**The question:** all three close-out doors ask whether the working tree is clean, because a dirty
tree means the gate measures content the merge does not carry. Should they verify it the same way?

**Measured answer: yes — and two of the three were wrong.**

| door | how it used to ask | the hole |
|---|---|---|
| `/cicd-push-e2e` | `status` in `PROJECT_ROOT` | with the epic in a worktree — the norm — that root stands on `main`, spotless, while the lane is dirty. **Reproduced**; fixed earlier in this lane |
| `/cicd-close-story-merge-tree` | the lane, but only `if args.worktree:` | the door says the flag is mandatory; **argparse did not**, and `/cicd-prune-worktree` calls the same script without it |
| `/smh-close-task-merge-tree` | whatever `--repo` names | correct by construction for its own door — and **`/smh-merge-multiple-workingtrees` is the shape where it is not**: it sets `REPO` to the tree you are *standing in*, then preflights each lane's branch in turn, so a set landing run from the main checkout saw none of the lanes' dirt. The worst place to be blind: N production merges at once |

⛔ **Making `--worktree` required — the literal ask — is the weaker fix, and I did not do it.** A
required flag can still be aimed at the wrong tree, which is *"cwd is not intent"* wearing a flag,
and it would have broken `/cicd-prune-worktree` and ten fixtures outright.
`wf_common.trees_to_measure` asks `git worktree list` which tree **holds** the branch — that can be
neither forgotten nor aimed wrong — and `--worktree` survives as an *additional* tree rather than
the only one. One body in the leaf module all three already import: the same move SCC-190 F6 made
for `VERDICT_RE`, for the same reason — **a gate and a door disagreeing about what they measured is
the defect class.**

Each door has a RED-first case and a **positive control** — worktrees are the norm here, so a check
that refused every lane holding one would false-red the shipping path, which is how a gate stops
being used. The task door's memory ruling is pinned to survive the second tree: `_artifacts/_memory/`
dirt keeps its own class wherever it is found, never folded into *"commit before merging"*, which is
the one instruction that ruling forbids.

**A third genuine survivor came out of this pass.** M48 lived because my own assertion
(`"lane-tree" in out`) was satisfied by `check_worktree`'s unrelated prune warning, which names the
same tree — so the sync check could regress to measuring only the checkout with the case still
green. It now requires the tree name **on the uncommitted line**, the finding it is actually about.
One knock-on: `FR6` keyed on the literal label `"worktree: fetch FAILED"`, and the label now names
*which* tree, so it went red on a better message while the behaviour it guards was untouched —
re-keyed to its intent.

**Final gates at `1c2ee57`:** enforcement suite **41/41 files, exit 0** (124.9 s, receipt stamped) ·
`test_task_preflight` 186/186 · `test_task_preflight_receipts` 39/39 · `test_closeout_preflight`
52/52 · `test_ship_preflight` 102/102 · door parity 177/177 · `workflow_lint` 0 errors 0 warnings ·
SOP currency 0 · roster gate 0 · **50 declared mutants, 50 killed** across five tables, every
restore verified byte-for-byte.
