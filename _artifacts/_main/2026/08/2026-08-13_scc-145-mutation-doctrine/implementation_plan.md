# SCC-145 — Mutation doctrine: name it, load it into the task lane, and gate it

- **Ticket:** SCC-145 (Bug, `In Progress`)
- **Repo:** `Sudo_Hatter_Command` · **Lane:** `chore/SCC-145-mutation-doctrine` (worktree
  `.claude/worktrees/mutation-doctrine`, echoed from `rev-parse`)
- **Plan date:** 2026-08-13

## The problem, in one line

Mutation testing is practiced everywhere and written down almost nowhere: the whole doctrine is one
shape-specific sub-bullet filed under "certification SHA" (`tests-must-gate-for-real.md:53-58`), the
word "mutation" appears only in that rule's provenance narrative (line 76), the task lane never loads
the rule at all, and no test pins any of it — measured twice as repeated ad-hoc mutant runs (SCC-144
×2, SCC-129 ×1).

## Pre-plan measurements (all re-run on this tree, 2026-08-13)

1. `grep -rn "mutant\|mutation\|mutate" .agents/commands/` → 2 hits, both irrelevant
   (`smh-update-maps-indexes.md:300` about a script mutating a folder; Lynn Margulis in
   `smh-adviser-board.md:154`). Ticket claim confirmed.
2. `grep -rln "Rules in force" .agents/scripts/tests/*.py` → **zero files.** No test anywhere asserts
   on any rules-in-force block. Ticket claim confirmed.
3. Rules-in-force block audit of the 8 commands that write or judge tests:
   | command | block exists | rule in block | rule in prose |
   |---|---|---|---|
   | `smh-code-review` | yes | **yes** (line 16) | yes |
   | `smh-quick-dev` | yes | no | no |
   | `smh-self-audit` | yes | no | no |
   | `cicd-dev-story-tests` | yes (1 rule only) | no | yes ×4 (step bodies) |
   | `cicd-clean-code-audit` | yes | no | yes ×2 |
   | `smh-clean-code-audit` | yes | no | yes ×2 |
   | `cicd-write-story-tests` | **no block** | — | yes ×1 |
   | `cicd-code-review` | **no block** | — | yes ×3 |
4. Sibling lanes (read at Step 0.5): SCC-129 and SCC-144 are live. **No overlap on any functional
   file this lane edits.** Shared ledger-class files only: `docs/_scc_sops_prds/workflows_testing_SOP.md`
   and `_artifacts/_main/INDEX.md` (both siblings), `.agents/.sync-manifest.json` (SCC-144). All are
   append-style union conflicts; whichever lane lands first, the later ones absorb `main` and re-stack.
   No landing-order requirement beyond that.

## ⭐ Scope ruling the plan makes explicit (divergence from FIX 4's first bullet)

The ticket's FIX 4 prose says "every command that WRITES or JUDGES tests cites the rule INSIDE its
own rules-in-force block." Measurement 3 shows that guard would go red on **five** commands (six sit
outside the edit set, but `smh-code-review` already complies), two of
which have no block to cite it in — forcing a contract edit to five commands, two of which
(`cicd-code-review`, `cicd-dev-story-tests`) carry `-AP` twins that would each owe a twin re-diff.
That is 3× the ticket's edit set, smuggled in through a guard's phrasing.

**This plan pins the in-block citation for the acceptance list's own set** — `smh-quick-dev`,
`smh-self-audit`, plus `smh-code-review` (the one command already carrying it in-block, pinned so it
cannot regress) — and does NOT rewrite the other five. The story-lane commands bake the rule into
the step bodies that route the work, which is the *stronger* form per
`restate-alwayson-obligations-in-command-bodies`; widening their blocks is its own ticket if ever
wanted. The acceptance block (the binding list, per /smh-quick-dev Step 1 authority order) names
exactly the two task-lane commands.

## Steps (each maps to an acceptance item and names the assertion that proves it)

### S1 — Guard cases in `test_command_surfaces.py`, written FIRST, seen RED (acceptance #4)

Append a `── Mutation doctrine wiring (SCC-145) ──` section to `main()` with, in the file's own
idiom (pure-function helpers + string controls + live sweep):

- `rif_block(text) -> str` — extract the contiguous `>`-blockquote following
  `**Rules in force for this command:**` (empty string when no block). The helper is what makes the
  check **block-scoped rather than file-grep** — the exact vacuity the ticket names.
- Case A: for each of `smh-quick-dev.md`, `smh-self-audit.md`, `smh-code-review.md`:
  `tests-must-gate-for-real` appears **inside** `rif_block(read(cmd))`.
- Case B (controls for A, pure strings): a file citing the rule only in body prose → caught; a file
  citing it in-block → passes; a file with no block at all → caught. (Three shapes, so the helper
  collapsing into a plain grep kills a control, not just the sweep.)
- Case C: extract `## Step 3` section of `smh-quick-dev.md` (from the `## Step 3` heading to the next
  `## ` heading); assert the mutant-table obligation sits inside it — pin the three load-bearing
  phrases: declared table ("before you mutate"), "one sweep", and the defective-mutant clause
  ("DEFECTIVE"). Section-anchored so a bullet drifting to another step goes red
  (`source-grep-guards-cannot-see-order`).
- Case D: `tests-must-gate-for-real.md` carries a `##`-level heading naming the practice
  (regex `^##.*mutation`, case-insensitive, anchored to line start so a prose mention cannot match) —
  and all three technique names (RELOCATE / INVERT / DEFECTIVE) appear inside that section.
- **RED proof:** run the file on the un-edited tree → cases A (2 of 3 files), C, D fail; paste the
  output. Case B's controls are green from birth (they are pure-string controls, stated as such).

### S2 — Promote the doctrine in `tests-must-gate-for-real.md` (FIX 3, acceptance #3)

New `## Mutation testing — proving a test can fail` section (heading names the practice, greppable),
carrying the three techniques:
- **RELOCATE** the guard — structural guard + behavioral test in one file; never delete (moved
  verbatim from Rule 4's fourth sub-bullet, which shrinks to a pointer at the new section).
- **INVERT** the decision — gates, hooks, shell checks; nothing to relocate.
- **A mutant that removes nothing is DEFECTIVE** — it is a SKIP that counts as a survivor; re-aim it
  before believing it. (New text; the direct cause of 3 of the 4 wasted runs.)
Plus the sweep discipline: declare the table (mutant → file → named case it must kill), run as ONE
sweep, a surviving mutant is a finding, record the table in the walkthrough.

### S3 — Load the rule into the task lane (FIX 1, acceptance #1)

One line each, matching the blocks' existing one-line-why idiom:
- `smh-quick-dev.md` rules-in-force block: `tests-must-gate-for-real.md` — the Step 2 red must fail
  for the right reason, and Step 3's mutants follow its §Mutation testing.
- `smh-self-audit.md` rules-in-force block: same rule — the audit judges the plan's test strategy
  against it.
Verified: neither command has an `-AP` twin (only `cicd-self-audit-AP.md` exists) → no twin re-diff owed.

### S4 — The mutant-table STEP in `/smh-quick-dev` Step 3 (FIX 2, acceptance #2)

One bullet in Step 3 (GREEN), per the ticket's own wording: declare the mutant table before you
mutate (each mutant, the file, the NAMED case it must kill); run as one sweep, never one at a time;
a survivor is a finding; a mutant whose edit does not appear in the original text is DEFECTIVE — a
SKIP that counts as a survivor — re-aim before believing it; record the table in the walkthrough.

### S5 — GREEN + the doctrine applied to itself (acceptance #4's mutant proof)

Re-run `test_command_surfaces.py` → green. Then the declared mutant sweep, run as ONE sweep:

| # | mutant | file | named case it must kill |
|---|---|---|---|
| M1 | move the rule line out of the block into body prose | `smh-quick-dev.md` | A (proves block-scoping) |
| M2 | delete the rules-in-force block entirely | `smh-self-audit.md` | A (proves no-block is caught) |
| M3 | move the mutant-table bullet from Step 3 to Step 2 | `smh-quick-dev.md` | C (proves section anchoring) |
| M4 | demote the `## Mutation testing` heading to bold prose | `tests-must-gate-for-real.md` | D (proves heading anchoring) |
| M5 | drop the DEFECTIVE technique from the new section | `tests-must-gate-for-real.md` | D (proves the 3 techniques are pinned) |

Every mutant's edit is verified present in the original text before the sweep (the defective-mutant
check, applied to this lane's own mutants). Results table goes in the walkthrough.

### S6 — Sync, SOP, gates, commit (acceptance #5, #6)

- `/smh-sync-agents` regenerates the `.opencode/commands/` + `.agents/workflows/` mirrors for the two
  edited commands (generated surfaces are never hand-edited). Risk: the engine is PowerShell — if
  `pwsh` is absent on this Mac, STOP and report rather than hand-editing mirrors.
- SOP currency: the change alters what `/smh-quick-dev` asks of an operator's session → update the
  SOP page (the path `sop_currency.py` enforces — both siblings staged
  `docs/_scc_sops_prds/workflows_testing_SOP.md`) in the same commit.
- Gates, bare, at the shipping SHA: `python3 .agents/scripts/tests/run_all.py` ·
  `python3 .agents/scripts/workflow_lint.py --toolkit-only` ·
  `python3 .agents/scripts/check_maps.py --depth3-only --strict` (AUTO-STALE label is the cwd
  basename in a worktree — known-false, per `check-maps-stale-is-false-in-worktrees`).
- Commit: explicit paths, key-led subject, `-F` file (the message will contain backticks).

## Out of scope (unchanged from the ticket)

- No mutation harness in the gate — `run_all.py` stays stdlib-only and deterministic.
- SCC-143 (lens_budget) — separate ticket, separate contract.
- The five story-lane commands' rules-in-force blocks (ruling above).

## Rollback

Every edit is additive prose or additive test cases in one lane; revert = drop the branch. The one
moved text (Rule 4 sub-bullet → §Mutation testing) keeps a pointer behind, so no citation elsewhere
in the tree dangles.

## Self-Audit (2026-08-13) — PRE-WORK mode

**Right-size: FULL** — the plan touches a rule (`tests-must-gate-for-real.md`), the enforcement
suite (`test_command_surfaces.py`), and two multi-platform command surfaces.

**Phase 0 — scope + checkable list.** Change set: 1 rule (rewrite-in-place), 2 command bodies, 1
test file (extended, never forked — `red-file-hosts-expansion-tests`), 4 generated mirrors via sync
+ `.sync-manifest.json`, the SOP page, artifacts dir + `_artifacts/_main/INDEX.md` row. Checkable
list = the ticket's 6 ACCEPTANCE items, traced both directions: #1→S3 · #2→S4 · #3→S2 · #4→S1+S5 ·
#5,#6→S6; every step traces back, no orphan steps. The ONE deliberate cut — FIX 4's "every command
that writes or judges tests" bullet — is measured (6 commands would go red, 2 have no block, 2 owe
`-AP` twin diffs) and ruled in §Scope ruling; the acceptance block itself only binds the two
task-lane commands. No deployable path in the change set → correct lane.

**Phase 1 — blast radius (greps run, not assumed).**
- Rule file: `grep -rn tests-must-gate-for-real .agents/scripts/` → 3 hits, all prose/comments; the
  only numbered citation is "rule 3" (`test_main_ruleset_armed.py:14`) and rule numbering is
  unchanged. `workflow_lint.py` has no pointer to this rule. No test pins the literal Rule-4
  sub-bullet text being moved. Commands citing "Rule 4" cite the certification headline, which stays.
- Command files: doors for both commands regenerate via `/smh-sync-agents`; descriptions are
  unchanged so launcher skills stay current; `commands/INDEX.md` row content unchanged. The existing
  door-parity check ("every mirror door still says what its brain says") mechanically catches a
  forgotten sync — the failure mode is loud, not silent.
- `pwsh` verified present at `/opt/homebrew/bin/pwsh` — the S6 sync risk is retired.
- Sibling lanes re-read at plan time: SCC-129 + SCC-144 live; zero functional-file overlap; shared
  ledger-class files only (SOP page, `_artifacts/_main/INDEX.md`, `.sync-manifest.json`). Landing
  order is free; later lanes absorb and re-stack. Named per the rule: if a sibling lands first, this
  lane's merge re-diffs those three files — nothing in this lane's functional set is at risk.

**Phase 2 — over-engineering gate.** No new command, rule file, or script. One helper
(`rif_block`) traces directly to acceptance #4's block-scoping demand. No flags, N=1, no
cannot-fail gates (every new case carries string controls + a named mutant that kills it). Plan
size proportional to a 6-item list. No tripwire fires.

**Phase 3 — pre-mortem.** Both machines: gate commands are `python3` (Mac) with PC `python` noted;
the test file is pure stdlib. Fresh clone: no new hook; the guard rides `run_all.py`. Fires on
someone else's commit: each new case's failure message names the file and the fix (matching the
file's house style). Empty input fails CLOSED: a missing block → empty string → case A red; a
missing file → `read()` raises loudly. Four caches: S6 syncs; door-parity backstops. Sibling lands
first: plan still applies (no shared functional files). Rollback: additive; drop the branch.
Surviving failure mode named: a future regeneration of `smh-quick-dev.md` from a template that
drops the bullet — which is exactly what cases A and C exist to catch; that is the ticket's point,
not a residual risk.

**Findings table:** none at severity. One ruling recorded (FIX 4 scope, above) — a divergence from
ticket prose in favor of the ticket's own acceptance block, stated for the operator to overrule at
approval time if the wider 8-command guard is wanted.

**Four quick gates:** verification strategy present per item (named command + expected output in
S1/S5/S6) ✅ · nothing irreversible (no delete, no transition, no merge) ✅ · no step vague enough
to guess — mutant table is declared in full in S5 ✅ · conventions anchored (test idiom, block
idiom, artifacts path, SOP-same-commit) ✅.

Audit verdict: GO

---

## ⚠️ AMENDMENT (2026-08-13, post-approval) — SCC-144 landed and handed this ticket two more techniques

**Why the plan changed after `approved`:** the operator called for a pull before work started. `main`
moved `5dadcd6` → `ba062a0` (SCC-144's merge-target guard landed; its worktree is pruned). This lane
fast-forwarded — **zero functional-file overlap, no conflict, nothing re-planned structurally.**

SCC-144's walkthrough `Your Actions` is written **to this ticket by name** ("there is no mutation
procedure anywhere in the command surface", three fixes + a fourth from its review). Two of its four
items are **not in the approved plan**, and both are load-bearing. They are additive inside
acceptance item #3, which already demands the practice's own section — so they widen the section's
content, not the change set, and no new file is touched.

**NEW A — mutants must be drawn from the CODE, never from the cases.** SCC-144's review measured it:
**24 of 25 code-derived mutants survived the 14 case-derived ones.** Reading your own cases and
asking "what would break this?" yields mutants the cases already cover — they die on arrival and
prove only that the suite is self-consistent. Drawing each mutant from a *decision in the source
under test* is what finds the holes. This is `prose-pinning-guards-are-vacuous` recurring one level
up, inside the mutation pass itself, and it is the single highest-value technique in the doctrine.

**NEW B — restore-on-interrupt, and never start dirty.** A `timeout`-killed sweep in SCC-144's lane
left `commit-msg-jira.sh` **on disk, mutated, uncommitted** — reverted to the very worktree-blind
probe that lane existed to remove. A mutated gate on disk is committable and shippable. So: restore
in a `finally`/trap, refuse to start against a dirty tree (otherwise residue is indistinguishable
from your own work), and re-check `git status` **after** the sweep before believing any result.

**Consequently the §Mutation testing section carries FIVE elements, not three** (S2), and the Step 3
bullet (S4) gains the code-derived requirement and the restore obligation. The mutant table in S5
gains **M6** — delete the code-derived clause from the rule — so the new text is itself pinned.

**Also confirmed against `ba062a0`, not assumed:** SCC-144 touched `test_git_hooks.py` and
`test_hooks_armed.py`, **not** `test_command_surfaces.py`; and it touched
`smh-merge-multiple-workingtrees.md`, **not** `smh-quick-dev.md`, `smh-self-audit.md` or
`tests-must-gate-for-real.md`. The functional change set is untouched by the landing. New baseline
to be additive against: **22/22 files, 1794/1794 cases**.

Amendment verdict: GO (unchanged) — additive within acceptance #3; overrule at review if the two new
techniques should be their own ticket.

