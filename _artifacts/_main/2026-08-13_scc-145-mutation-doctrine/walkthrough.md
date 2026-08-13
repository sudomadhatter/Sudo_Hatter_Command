# SCC-145 — Mutation doctrine: name it, load it into the task lane, and gate it

- **Ticket:** SCC-145 (Bug) · **Lane:** `chore/SCC-145-mutation-doctrine` · **Repo:** `Sudo_Hatter_Command`
- **Branched from:** `5dadcd6` → **absorbed** `ba062a0` (SCC-144) mid-lane → **build sha** `268f894`
- **Date:** 2026-08-13

## Task Checklist

- [x] **Step 0 / 0.5** — repo + lane pinned from `rev-parse`; SCC-145 → `In Progress` (`jira_feed start`, exit 0)
  - Sibling lanes read at open: SCC-129 (`gate-the-gate`) and SCC-144 (`merge-target-guard`), **zero
    functional-file overlap**; only ledger-class files shared.
- [x] **Step 1** — checkable list taken from the ticket's own `ACCEPTANCE` block (authority order #1)
- [x] **Step 1.5** — plan written, `/smh-self-audit` **GO** (FULL tier), stopped for the literal `approved`
  - ⚠ **Amended after approval, on the operator's call to pull first** — see *Deviations* #1.
- [x] **Step 2** — RED: **49/52, exit 1**, three cases failing for the right reason
- [x] **Step 3** — GREEN: **52/52, exit 0**; sync run; SOP + ledger row staged in the same commit
- [x] **Step 3b** — mutation sweep: **8 declared, 8 killed**, tree verified restored
- [ ] **Step 4** — `/smh-code-review`
- [x] **Step 5** — artifacts, manifest, Dev Record

## What was actually wrong

Mutation testing was practiced constantly and written down almost nowhere. Re-measured on this tree
before a line was edited:

| Claim | Measurement |
|---|---|
| The practice is absent from the command surface | `grep -rn "mutant\|mutation\|mutate" .agents/commands/` → **2 hits**: a script that mutates `_my_resources/`, and *"Lynn Margulis — merger beats mutation"* in the adviser board. A biologist. |
| The doctrine is one sub-bullet, filed under another concern | `tests-must-gate-for-real.md` → `## The Rule` → item **4** (headlined *"Certification is measured at the SHIPPING SHA"*) → **fourth** sub-bullet |
| The normative text never names the practice | the word "mutation" appeared **once** in that file, at line 76, inside `## Why` — the provenance narrative, not the binding rule |
| The one technique given does not transfer | *relocate, never delete* assumes a structural guard + behavioral test in one file. A shell gate has **nothing to relocate** — the useful mutant **inverts a decision** |
| ⭐ It reaches the STORY lane but not the TASK lane | loaded by 6 story-lane commands; on the task lane only `/smh-code-review` — **after** the mutants are designed. `/smh-quick-dev` (writes the assertions) and `/smh-self-audit` (judges the plan that picks the strategy) loaded it **not at all** |
| Nothing mechanical could see any of it | `grep -rln "Rules in force" .agents/scripts/tests/*.py` → **zero files.** No test anywhere asserted on any rules-in-force block |
| The operator's own SOP never named it either | `grep -i "mutant\|mutation"` over `workflows_testing_SOP.md` → **zero hits** (not in the ticket; found while fixing it) |

## Evidence

| Acceptance item | The assertion that proves it | RED → GREEN |
|---|---|---|
| #1 rule in the rules-in-force block of `smh-quick-dev` + `smh-self-audit` | `test_command_surfaces.py` — *"the mutation rule is LOADED …"*, scoped by `rif_block` | `['smh-quick-dev.md', 'smh-self-audit.md']` → `[]` |
| #2 Step 3 carries the mutant-table obligation | *"/smh-quick-dev Step 3 carries the mutant-table obligation…"*, scoped by `md_section` | missing `['mutant table', 'one sweep', 'DEFECTIVE', 'from the code', 'git status']` → `[]` |
| #3 rule has a section named for the practice, all techniques | *"the mutation rule has a section whose HEADING names the practice…"* | `no ## heading names mutation` → `[]` |
| #4 guards pin the BLOCK, not the filename anywhere | 6 controls + the M1/M7 mutants below | proven, not assumed — see *Mutation* |
| #5 gate green at the shipping sha | `run_all` · `workflow_lint --toolkit-only` · `check_maps --depth3-only --strict`, all **bare** | see *Gates* |
| #6 SOP currency | SOP staged in the same commit as the usage-surface change | `268f894` |

**RED** (`red-01-mutation-doctrine.txt`, bare, exit **1**):

```
[FAIL] the mutation rule is LOADED (in the rules-in-force block) by every task-lane command …
       ['smh-quick-dev.md', 'smh-self-audit.md'] - cite `.agents/rules/tests-must-gate-for-real.md`
       INSIDE the block, not in step prose.
[FAIL] /smh-quick-dev Step 3 carries the mutant-table obligation …
       missing from `## Step 3`: ['mutant table', 'one sweep', 'DEFECTIVE', 'from the code', 'git status']
[FAIL] the mutation rule has a section whose HEADING names the practice, carrying every technique
       no `##` heading in tests-must-gate-for-real.md names mutation
-- 49/52 passed --
```

**GREEN** (`green-01-mutation-doctrine.txt`, bare, exit **0**): `-- 52/52 passed --`

⛔ **One case went red in between, and that was the mechanism working.** Editing two command bodies
without re-syncing turned *"every mirror door still says what its brain says"* red — the SCC-113
door-parity check catching a forgotten sync. `/smh-sync-agents` cleared it. The failure mode is loud,
exactly as the plan's Phase 1 predicted.

## Mutation

**8 declared before mutating, run as ONE sweep, drawn from the code, restored in a `finally`.** The
sweep refused to start dirty and re-checked `git status` on exit — so the doctrine this ticket ships
is the doctrine that proved it. Sweep script kept out of the tree (running mutation *in the gate* is
explicitly out of scope); the table is the artifact.

| # | Mutant | File | Named case it must kill | Result |
|---|---|---|---|---|
| M1 | the rule's line deleted from the rules-in-force block | `smh-quick-dev.md` | the rule is LOADED | **KILLED** |
| M2 | the whole rules-in-force block header deleted | `smh-self-audit.md` | the rule is LOADED | **KILLED** |
| M3 | the mutant-table bullet **relocated** out of Step 3 into Step 2 | `smh-quick-dev.md` | Step 3 carries the obligation | **KILLED** |
| M4 | `## Mutation Testing` heading demoted to bold prose | `tests-must-gate-for-real.md` | the section names the practice | **KILLED** |
| M5 | `DEFECTIVE` removed from its subsection heading | `tests-must-gate-for-real.md` | the section names the practice | **KILLED** |
| M6 | the whole `CODE-DERIVED` technique deleted | `tests-must-gate-for-real.md` | the section names the practice | **KILLED** |
| M7 | ⭐ `rif_block` returns the whole file (block-scoping collapses to a file grep) | `test_command_surfaces.py` | *CONTROL: cited only in BODY PROSE is NOT loaded* | **KILLED** |
| M8 | ⭐ `md_section` loses its `## ` boundary (sections run on forever) | `test_command_surfaces.py` | *CONTROL: `## Step 3` does not swallow `## Step 3.5`* | **KILLED** |

**8/8 killed. `restored clean: YES`.**

⭐ **M7 and M8 are the CODE-DERIVED half, and they are the point.** M1–M6 mutate the documents the
guard reads — useful, but drawn close to the cases. M7 and M8 mutate **the guard's own helpers**,
which is where a vacuous check would actually live. SCC-144's review measured why this matters: 24 of
25 code-derived mutants survived the 14 case-derived ones.

⭐ **M1 proves the block-scoping is load-bearing rather than decorative**, and it was verified
mechanically rather than argued. With M1 applied to `smh-quick-dev.md`:

```
file-wide grep still finds the rule (a naive guard PASSES): True
block-scoped check finds it (the real guard FAILS):         False
```

The rule name survives in Step 3's own prose, so the obvious implementation of this guard — *"does
the file mention the rule?"* — would have shipped green against a command that had just lost it.
That is `prose-pinning-guards-are-vacuous` (SCC-125), defeated in advance instead of in hindsight.

## Deviations from the ticket, and why

1. **The plan was amended after `approved`, and the amendment is recorded in the plan itself.** The
   operator called for a pull before work began; `main` had moved `5dadcd6` → `ba062a0`. SCC-144's
   walkthrough `Your Actions` is addressed **to this ticket by name** and carries two techniques the
   ticket predates: **CODE-DERIVED** (its review's own finding) and **RESTORE on interrupt** (a
   `timeout`-killed sweep left `commit-msg-jira.sh` mutated on disk, uncommitted — reverted to the
   exact bug that lane existed to remove). Both are additive inside acceptance item #3, which already
   demanded the practice's own section, so the change set did not grow. The section ships **four
   techniques plus the DEFECTIVE rule**, not three.
2. ⭐ **FIX 4's first bullet was deliberately NOT implemented as written, and this is the one call
   worth overruling if you disagree.** The ticket says *every* command that writes or judges tests
   must cite the rule inside its own rules-in-force block. Measured, that guard goes red on **six**
   commands — two of which (`cicd-code-review`, `cicd-write-story-tests`) have **no such block at
   all**, and two of which carry `-AP` twins owing a twin re-diff. That is ~3× the ticket's edit set,
   entering through a guard's phrasing rather than through its acceptance block. The binding list
   (Step 1's authority order #1) names only the two task-lane commands. **Pinned here:**
   `smh-quick-dev`, `smh-self-audit`, and `smh-code-review` — the last because it already complied,
   and an unpinned compliance is one edit from being gone. The five story-lane commands keep the
   *stronger* form: the rule baked into the step bodies that route the work
   (`restate-alwayson-obligations-in-command-bodies`). Widening them is its own ticket.
3. **The SOP gained a section the ticket did not ask for.** `workflows_testing_SOP.md` had **zero**
   mentions of mutation — the operator's own reference had never named the practice either. Fixing
   the commands while leaving the SOP silent would have satisfied the gate and missed the point.
4. **No mutation harness in the gate.** Unchanged from the ticket's *Out of scope*: `run_all.py`
   stays stdlib-only and deterministic. The sweep script lives in the scratchpad, not the tree.

## Gates

| Gate | Result |
|---|---|
| Enforcement suite | `run_all.py` → *(final certification below)* |
| Toolkit lint | `workflow_lint.py --toolkit-only` → *(final certification below)* |
| Map / INDEX | `check_maps.py --depth3-only --strict` → **exit 0** |
| Assertion evidence | RED and GREEN captured bare, both committed beside this file |
| Mutation | **8/8 killed**, tree verified restored |
| SOP currency | `268f894` stages the SOP with the usage-surface change |
| Door parity | green after `/smh-sync-agents` (went red first — see *Evidence*) |

## Your Actions

- **Review and close out** — `/smh-close-task-merge-tree` is yours, and typing it is the merge sign-off.
- ⭐ **The one judgement call to confirm or overrule:** *Deviations #2* — the in-block citation is
  pinned for the two task-lane commands plus `smh-code-review`, not for all eight commands that write
  or judge tests. Say the word and the wider guard is a follow-on ticket.
- **Still owed, deliberately not smuggled in here:**
  - **SCC-143** — `/cicd-code-review` passes no `lens_budget`, so an interactive review silently takes
    the autopilot's `capped` default. Separate contract, separate ticket, no file overlap with this
    lane. It was checked for duplication against this ticket and is **not** a duplicate.
  - SCC-144's other open handoffs: the SOP mermaid node for the merge-target gate, and propagating
    its hooks to `Projects/*` (repo-local by law — needs its own key per repo).
